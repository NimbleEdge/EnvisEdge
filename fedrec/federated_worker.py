
from abc import ABC, abstractmethod
from asyncio.exceptions import InvalidStateError
from collections import defaultdict
from types import FunctionType
from typing_extensions import Required
from fedrec.utilities import registry
from fedrec.utilities.logger import BaseLogger
from fedrec.communications.worker_manager import WorkerComManager
import logging
from typing import Dict, List, Set
import attr
import asyncio
import json

import numpy as np
from fedrec.trainers.base_trainer import BaseTrainer
from fedrec.utilities.cuda_utils import map_to_list
from fedrec.utilities.random_state import RandomContext, Reproducible

ROLE_HANDLER_DICT = defaultdict(dict)


def role(role_type):

    def register_handler(func: FunctionType):
        if func.__name__ in registry:
            raise LookupError('{} already present {}'.format(
                role_type, func.__name__))
        ROLE_HANDLER_DICT[role_type] = func
        return func

    return register_handler


@attr.s(kw_only=True)
class WorkerState:
    id = attr.ib()
    model_preproc = attr.ib()
    roles = attr.ib()
    round_idx = attr.ib(0)
    state_dict = attr.ib(None)
    storage = attr.ib(None)
    neighbours = attr.ib(dict)


@attr.s
class Neighbour:
    id = attr.ib()
    model = attr.ib(None)
    sample_num = attr.ib(None)
    last_sync = attr.ib(-1)

    def update(self, kwargs):
        for k, v in kwargs:
            if k == 'id' and v != self.id:
                return
            if hasattr(self, k):
                setattr(self, k, v)


class FederatedWorker(Reproducible, ABC):
    # Class description inspired from FedML
    # https://github.com/FedML-AI/FedML/blob/master/fedml_api/distributed/fedavg/FedAVGAggregator.py

    def __init__(self,
                 worker_index: int,
                 roles,
                 in_neighbours: Dict[int, Neighbour],
                 out_neighbours: Dict[int, Neighbour],
                 base_trainer: BaseTrainer,
                 com_dict: Dict,
                 persistent_storage: str = None,
                 is_mobile: bool = True,
                 round_idx: int = 0):

        self.round_idx = round_idx
        self.worker_index = worker_index
        self.roles = roles
        self.is_mobile = is_mobile
        self.persistent_storage = persistent_storage
        self.in_neighbours = in_neighbours
        self.out_neighbours = out_neighbours

        self.trainer = base_trainer
        self.local_sample_number = None

        self.fl_com_manager = WorkerComManager(
            trainer=base_trainer, id=worker_index, config_dict=com_dict)

        # TODO remove these
        self.model_dict = dict()
        self.sample_num_dict = dict()

    def serialise(self):
        in_neigh = {k: v.last_sync for k, v in self.in_neighbours}
        out_neigh = {k: v.last_sync for k, v in self.out_neighbours}
        return WorkerState(
            id=self.worker_index,
            round_idx=self.round_idx,
            state_dict={
                'model': self._get_model_params(),
                'optimizer': self.trainer.optimizer.state_dict(),
                'step': 0
            },
            model_preproc=self.trainer.model_preproc,
            roles=self.roles,
            storage=self.persistent_storage,
            neighbours={
                "in": in_neigh,
                "out": out_neigh
            }
        )

    @classmethod
    def load_worker(
            cls,
            trainer: BaseTrainer,
            in_neigh: List[Neighbour],
            out_neigh: List[Neighbour],
            state: WorkerState):

        trainer.load_state(
            state.state_dict['model'],
            state.state_dict['optimizer'],
            state.model_preproc)

        return cls(
            state.id,
            state.roles,
            in_neigh,
            out_neigh,
            base_trainer=trainer,
            persistent_storage=state.storage,
            round_idx=state.round_idx
        )

    def _get_model_params(self):
        return self.trainer.model.cpu().state_dict()

    def update_model(self, weights):
        self.trainer.model.load_state_dict(weights)

    def update_recieved_model(self, sender_id, kwargs):
        self.in_neighbours[sender_id].update(**kwargs)

    def update_dataset(self, worker_index, model_preproc):
        self.worker_index = worker_index
        self.trainer.model_preproc = model_preproc
        self.local_sample_number = len(
            self.trainer.model_preproc.datasets('train'))
        self.trainer.reset_loaders()

    async def train(self, *args, **kwargs):
        raw_output = await self.fl_com_manager.send_job("train", *args, **kwargs)
        new_state, output = json.loads(raw_output)
        self.trainer.update_state(
            new_state.state_dict['model'],
            new_state.state_dict['optimizer'])
        return output

    async def test(self, *args, **kwargs):
        await self.fl_com_manager.send_job("test", *args, **kwargs)

    async def get_model(self, round_idx, out_neighbours: Set[int]):
        '''
            Send the model to whoever needs it. 
            Train it if already submitted the current model.
        '''
        neighbours = set(self.out_neighbours.keys())
        if not out_neighbours.issubset(neighbours):
            raise ValueError("invalid recieve call")

        out_reqs = {
            n for n in out_neighbours if self.out_neighbours[n].last_sync < round_idx}
        if out_reqs:
            await self.run()
            # transform Tensor to list
        weights, s_n = self._get_model_params(), self.local_sample_number
        if self.is_mobile == 1:
            weights = map_to_list(weights)
        for n in out_neighbours:
            self.out_neighbours[n].last_sync = self.round_idx

        return weights, s_n, self.round_idx

    async def request_models_suspendable(self, neighbours):
        out_req = {
            n for n in neighbours if self.in_neighbours[n].last_sync < self.round_idx}
        if out_req:
            result = await self.fl_com_manager.send_message_get_models(
                self.worker_index, out_req)
            for id in self.in_neighbours.keys():
                self.update_recieved_model(id, result[id])
        return neighbours

    def request_models(self, neighbours):
        asyncio.run(self.request_models_suspendable(neighbours))
        return neighbours

    def broadcast_model(self, out_neighbour_ids):
        for n in out_neighbour_ids:
            self.fl_com_manager.send_model(n, self._get_model_params(),
                                           self.local_sample_number)


class WorkerDataset:
    def __init__(self) -> None:
        self._workers = {}
        self.workers_by_types = defaultdict(list)
        self._len = 0

    def add_worker(self,
                   trainer,
                   roles,
                   in_neighbours,
                   out_neighbours):

        in_neighbours = [Neighbour(n) for n in in_neighbours]
        out_neighbours = [Neighbour(n) for n in out_neighbours]

        self._workers[self._len] = FederatedWorker(
            self._len, roles, in_neighbours, out_neighbours, trainer)

        for role in roles:
            self.workers_by_types[role] += [self._len]

        self._len += 1

    def get_worker(self, id):
        # TODO We might persist the state in future
        # So this loading will be dynamic.
        # Then would create a new Federated worker everytime from the persisted storage
        return self._workers[id]

    def get_workers_by_roles(self, role):
        return [self._workers[id] for id in self.get_workers_by_roles[role]]

    def __len__(self):
        return self._len


@registry.load('fl_algo', 'fed_avg')
class FedAvgWorker(FederatedWorker):
    def __init__(self,
                 worker_index: int,
                 roles,
                 in_neighbours: Dict[int, Neighbour],
                 out_neighbours: Dict[int, Neighbour],
                 base_trainer: BaseTrainer,
                 com_dict: Dict,
                 persistent_storage: str):

        super().__init__(worker_index, roles, in_neighbours,
                         out_neighbours, base_trainer, com_dict,
                         persistent_storage=persistent_storage)

    async def run(self):
        '''
            `Run` function updates the local model. 
            Implement this method to determine how the roles interact with each other to determine the final updated model.
            For example a worker which has both the `aggregator` and `trainer` roles might first train locally then run discounted `aggregate()` to get the fianl update model 


            In the following example,
            1. Aggregator requests models from the trainers before aggregating and updating its model.
            2. Trainer responds to aggregators' requests after updating its own model by local training.

            Since standard FL requires force updates from central entity before each cycle, trainers always start with global model/aggregator's model 

        '''
        assert role in self.roles, InvalidStateError("unknown role for worker")

        if role == 'aggregator':
            neighbours = await self.request_models_suspendable(self.sample_neighbours())
            weighted_params = self.aggregate(neighbours)
            self.update_model(weighted_params)
        elif role == 'trainer':
            # central server in this case
            aggregators = list(self.out_neighbours.values())
            global_models = await self.request_models_suspendable(aggregators)
            self.update_model(global_models[0])
            await self.train(model_dir=self.persistent_storage)
        self.round_idx += 1

    @BaseLogger.time
    def aggregate(self, neighbour_ids):
        model_list = [
            (self.in_neighbours[id].sample_num, self.in_neighbours[id].model)
            for id in neighbour_ids
        ]
        (num0, averaged_params) = model_list[0]
        for k in averaged_params.keys():
            for i in range(0, len(model_list)):
                local_sample_number, local_model_params = model_list[i]
                w = local_sample_number / training_num
                if i == 0:
                    averaged_params[k] = local_model_params[k] * w
                else:
                    averaged_params[k] += local_model_params[k] * w

        return averaged_params

    def sample_neighbours(self, round_idx, client_num_per_round):
        num_neighbours = len(self.in_neighbours)
        if num_neighbours == client_num_per_round:
            selected_neighbours = [
                neighbour for neighbour in self.in_neighbours]
        else:
            with RandomContext(round_idx):
                selected_neighbours = np.random.choice(
                    self.in_neighbours, min(client_num_per_round, num_neighbours), replace=False)
        logging.info("worker_indexes = %s" % str(selected_neighbours))
        return selected_neighbours
