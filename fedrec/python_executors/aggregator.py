import inspect
from abc import ABC
from typing import Dict

from fedrec.data_models.aggregator_state_model import (AggregatorState,
                                                       Neighbour)
from fedrec.python_executors.base_actor import BaseActor
from fedrec.user_modules.envis_base_module import EnvisBase
from fedrec.utilities import registry
from fedrec.utilities.logger import BaseLogger


class Aggregator(BaseActor, ABC):
    """
    This class is used to aggregate the data from a list of actors.

    Attributes
    ----------
    round_idx : int
        Number of local iterations finished
    worker_id : str
        The unique id alloted to the worker by the orchestrator
    is_mobile : bool
        Whether the worker represents a mobile device or not
    persistent_storage : str
        The location to serialize and store the `WorkerState`
    in_neighbours : List[`Neighbour`]
        Neighbours from which the the worker can take the models
    out_neighbours : List[`Neighbour`]
        Neighbours to which the worker can broadcast its model
    """

    def __init__(self,
                 worker_id: str,
                 config: Dict,
                 logger: BaseLogger,
                 in_neighbours: Dict[int, Neighbour] = None,
                 out_neighbours: Dict[int, Neighbour] = None,
                 is_mobile: bool = True,
                 round_idx: int = 0):
        super().__init__(worker_id, config, logger,
                         is_mobile, round_idx)
        self.in_neighbours = in_neighbours
        self.out_neighbours = out_neighbours
        # TODO update trainer logic to avoid double model initialization
        self.worker: EnvisBase = registry.construct(
            'aggregator',
            config['aggregator'],
            unused_keys=(),
            config_dict=config,
            in_neighbours=in_neighbours,
            out_neighbours=out_neighbours
        )
        self.worker_funcs = {
            func_name_list[0]: getattr(self.worker, func_name_list[0])
            for func_name_list in
            inspect.getmembers(self.worker, predicate=inspect.ismethod)
        }

    def serialize(self):
        """Serialise the state of the worker to a AggregatorState.

        Returns
        -------
        `AggregatorState`
            The serialised class object to be written
            to Json or persisted into the file.
        """
        state = {
            'model': self._get_model_params(),
            'worker_state': self.worker.envis_state,
            'step': self.round_idx
        }
        if self.optimizer is not None:
            state['optimizer'] = self._get_optimizer_params()

        return AggregatorState(
            worker_id=self.worker_id,
            round_idx=self.round_idx,
            state_dict=state,
            storage=self.persistent_storage,
            in_neighbours=self.in_neighbours,
            out_neighbours=self.out_neighbours
        )

    def load_worker(
            self,
            state: AggregatorState):
        """Constructs a aggregator object from the state.

        Parameters
        ----------
        state : AggregatorState
            AggregatorState containing the weights
        """
        self.worker_id = state.worker_id
        self.persistent_storage = state.storage
        self.in_neighbours = state.in_neighbours
        self.out_neighbours = state.out_neighbours
        self.round_idx = state.round_idx
        if state.state_dict is not None:
            self.update_local_state(state.state_dict)
        
        self.update_worker_state(state.state_dict)

    def update_local_state(self, state_dict):
        """
        Update the state dict of the worker.

        state_dict : Dict
            Dictionary of the state to be updated
        """
        self.load_model(state_dict['model'])
        if self.optimizer is not None:
            self.load_optimizer(state_dict['optimizer'])

    def update_worker_state(self, state_dict):
        """
        Update the state of the worker.

        state : Dict
            Dictionary of the state to be updated
        """
        if ("worker_state" not in state_dict) or (state_dict is None):
            local_state = {
                "model" : self.model.state_dict(),
                "in_neighbours" : self.in_neighbours,
            }
        else :
            local_state = state_dict["worker_state"]
        self.worker.update(local_state)

    def run(self, func_name, *args, **kwargs):
        """
        Run the aggregation.

        func_name : Name of the function to run in the aggregation
        """
        if func_name in self.worker_funcs:
            print(f"Running function name: {func_name}")
            return self.process_args(
                self.worker_funcs[func_name](*args, **kwargs))
        else:
            raise ValueError(
                f"Job type <{func_name}> not part of worker"
                + f"<{self.worker.__class__.__name__}> functions")
