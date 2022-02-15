from abc import ABC, abstractmethod
from typing import Dict

import attr
from fedrec.python_executors.base_actor import BaseActor
from fedrec.utilities import registry
from fedrec.utilities.logger import BaseLogger
from fedrec.data_models.aggregator_state_model import AggregatorState


@attr.s
class Neighbour:
    """A class that represents a new Neighbour instance.

    Attributes
    ----------
    id : int
        Unique identifier for the worker
    model : Dict
        Model weights of the worker
    sample_num : int
        Number of datapoints in the neighbour's local dataset
    last_sync : int
        Last cycle when the models were synced
    """
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


class Aggregator(BaseActor, ABC):
    """
    This class is used to aggregate the data from a list of actors.

    Attributes
    ----------
    round_idx : int
        Number of local iterations finished
    worker_index : int
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
                 worker_index: int,
                 config: Dict,
                 logger: BaseLogger,
                 in_neighbours: Dict[int, Neighbour] = None,
                 out_neighbours: Dict[int, Neighbour] = None,
                 persistent_storage: str = None,
                 is_mobile: bool = True,
                 round_idx: int = 0):
        super().__init__(worker_index, config, logger,
                         persistent_storage, is_mobile, round_idx)
        self.in_neighbours = in_neighbours
        self.out_neighbours = out_neighbours
        # TODO update trainer logic to avoid double model initialization
        self.worker = registry.construct('aggregator',
                                         config['aggregator'],
                                         in_neighbours=in_neighbours,
                                         out_neighbours=out_neighbours)
        # self.worker_funcs =
        # {func_name: getattr(self.worker, func_name) for func_name in dir(
        #     self.worker) if callable(getattr(self.worker, func_name))}
        self.worker_funcs = {"test_run": getattr(self.worker, "test_run")}

    def serialize(self):
        """Serialise the state of the worker to a AggregatorState.

        Returns
        -------
        `AggregatorState`
            The serialised class object to be written
            to Json or persisted into the file.
        """
        return AggregatorState(
            id=self.worker_index,
            round_idx=self.round_idx,
            state_dict={
                'model': self._get_model_params(),
                'step': self.round_idx
            },
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
        self.worker_index = state.id
        self.persistent_storage = state.storage
        self.in_neighbours = state.in_neighbours
        self.out_neighbours = state.out_neighbours
        self.round_idx = state.round_idx
        self.model.load_state_dict(state.state_dict['model'])
        if self.optimizer is not None:
            self.optimizer.load_state_dict(state.state_dict['optimizer'])

    def run(self, func_name, *args, **kwargs):
        """
        Run the aggregation.

        func_name : Name of the function to run in the aggregation
        """
        if func_name in self.worker_funcs:
            print(f"Running function name: {func_name}")
            return self.worker_funcs[func_name](*args, **kwargs)
        else:
            raise ValueError(
                f"Job type <{func_name}> not part of worker"
                + f"<{self.worker.__class__.__name__}> functions")
