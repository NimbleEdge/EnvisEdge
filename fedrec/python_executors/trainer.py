import inspect
from abc import ABC
from typing import Dict

from fedrec.data_models.trainer_state_model import TrainerState
from fedrec.python_executors.base_actor import BaseActor
from fedrec.user_modules.envis_base_module import EnvisBase
from fedrec.utilities import registry
from fedrec.utilities.logger import BaseLogger


class Trainer(BaseActor, ABC):
    """
    The Trainer class is responsible for training the model, updating the
    model weights, and running the training steps. It also handles the loading
    and preprocessing of data.

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
    
    Methods
    -------
    reset_loaders()
        Reset the data loaders to empty dict to avoid memory issues when
        loading the data multiple times in the same epoch.
    serialize()
        Serialize the state of the worker to a TrainerState.
    load_worker()
        Constructs a trainer object from the state.
    update_dataset()
        Update the dataset, trainer_index and model_index.
    run()
        Run the model.
    """

    def __init__(self,
                 worker_index: int,
                 config: Dict,
                 logger: BaseLogger,
                 client_id: int,
                 is_mobile: bool = True,
                 round_idx: int = 0):
        super().__init__(worker_index, config, logger,
                         is_mobile, round_idx)
        self.local_sample_number = None
        self.local_training_steps = 10
        self._data_loaders = {}
        self.client_id = client_id
        # TODO update trainer logic to avoid double model initialization
        self.worker: EnvisBase = registry.construct(
            'trainer',
            config["trainer"],
            unused_keys=(),
            config_dict=config,
            client_id=self.client_id,
            logger=logger)

        self.worker_funcs = {
            func_name_list[0]: getattr(self.worker, func_name_list[0])
            for func_name_list in
            inspect.getmembers(self.worker, predicate=inspect.ismethod)
        }
        #  self.worker_funcs = {"test_run": getattr(self.worker, "test_run")}

    def reset_loaders(self):
        self._data_loaders = {}

    def serialize(self):
        """Serialize the state of the worker to a TrainerState.

        Returns
        -------
        `TrainerState`
            The serialised class object to be written
            to Json or persisted into the file.
        """
        state = {
            'model': self._get_model_params(),
            'worker_state': self.worker.envis_state,
            'step': self.local_training_steps
        }
        if self.optimizer is not None:
            state['optimizer'] = self._get_optimizer_params()

        return TrainerState(
            worker_index=self.worker_index,
            round_idx=self.round_idx,
            state_dict=state,
            model_preproc=self.model_preproc,
            storage=self.persistent_storage,
            local_sample_number=self.local_sample_number,
            local_training_steps=self.local_training_steps
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
        self.worker_index = state.worker_index
        self.persistent_storage = state.storage
        self.round_idx = state.round_idx
        self.load_model(state.state_dict['model'])
        self.local_training_steps = state.state_dict['step']
        if self.optimizer is not None:
            self.load_optimizer(state.state_dict['optimizer'])
        self.worker.update(state.state_dict["worker_state"])

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
        if func_name in self.worker_funcs:
            print(f"Running function name: {func_name}")
            return self.process_args(
                self.worker_funcs[func_name](*args, **kwargs))
        else:
            raise ValueError(
                f"Job type <{func_name}> not part of worker"
                + f"<{self.worker.__class__.__name__}> functions")
