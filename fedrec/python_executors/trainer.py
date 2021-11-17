
from abc import ABC
from typing import Dict
import attr
from fedrec.python_executors.base_actor import BaseActor, ActorState
from fedrec.utilities.logger import BaseLogger
from fedrec.utilities import registry


@attr.s(kw_only=True)
class TrainerState(ActorState):
    """Construct a workerState object to reinstatiate a worker when needed.

    Attributes
    ----------
    id : int
        Unique worker identifier
    model_preproc : `Preprocessor`
        The local dataset of the worker 
    round_idx : int
        The number of local training cycles finished
    state_dict : dict
        A dictionary of state dicts storing model weights and optimizer dicts
    storage : str
        The address for persistent storage 
    """
    model_preproc = attr.ib()
    local_sample_number = attr.ib()
    local_training_steps = attr.ib()


class Trainer(BaseActor, ABC):
    """
    The Trainer class is responsible for training the model.
    """

    def __init__(self,
                 worker_index: int,
                 model_config: Dict,
                 logger: BaseLogger,
                 persistent_storage: str = None,
                 is_mobile: bool = True,
                 round_idx: int = 0):
        """
        Initialize the Trainer class.

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
        local_sample_number : int or None
            The number of datapoints in the local dataset

        """
        super().__init__(worker_index, model_config, logger,
                         persistent_storage, is_mobile, round_idx)
        self.local_sample_number = None
        self.local_training_steps = 0
        self._data_loaders = {}
        #TODO update trainer logic to avoid double model initialization
        self.trainer = registry.construct('trainer', model_config['model'], **model_config['train'])
        self.trainer_funcs = {func.__name__: func for func in dir(
            self.trainer) if callable(func)}

    def reset_loaders(self):
        self._data_loaders = {}

    def serialise(self):
        """Serialise the state of the worker to a TrainerState.

        Returns
        -------
        `TrainerState` 
            The serialised class object to be written to Json or persisted into the file.
        """
        state = {
            'model': self._get_model_params(),
            'step': self.local_training_steps
        }
        if self.optimizer is not None:
            state['optimizer'] = self.optimizer.state_dict()

        return TrainerState(
            id=self.worker_index,
            round_idx=self.round_idx,
            state_dict=state,
            model_preproc=self.model_preproc,
            storage=self.persistent_storage
        )

    def load_worker(
            self,
            state: TrainerState):
        """Constructs a trainer object from the state.

        Parameters
        ----------
        state : TrainerState
            TrainerState containing the weights
        """
        self.worker_index = state.id
        self.persistent_storage = state.storage
        self.round_idx = state.round_idx
        self.model.load_state_dict(state.state_dict['model'])
        self.local_training_steps = state.state_dict['step']
        if self.optimizer is not None:
            self.optimizer.load_state_dict(state.state_dict['optimizer'])

    def update_dataset(self, model_preproc):
        """Update the dataset, trainer_index and model_index .

        Parameters
        ----------
        worker_index : int
            unique worker id
        model_preproc : `Preprocessor`
            The preprocessor contains the dataset of the worker 
        """
        self.model_preproc = model_preproc
        self.local_sample_number = len(
            self.model_preproc.datasets('train'))
        self.reset_loaders()

    def run(self, func_name, *args, **kwargs):
        """
        Run the model.

        func_name : Name of the function to run in the trainer
        """
        if func_name in self.trainer_funcs:
            self.trainer_funcs[func_name](*args, **kwargs)
        else:
            raise ValueError(
                f"Job type <{func_name}> not part of worker <{self.trainer.__class__.__name__}> functions")
