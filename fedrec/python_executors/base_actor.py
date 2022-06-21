import os
from abc import ABC, abstractclassmethod, abstractmethod
from random import randint
from typing import Dict, List, Tuple

import torch
from fedrec.data_models.state_tensors_model import StateTensors
from fedrec.data_models.tensors_model import EnvisTensors
from fedrec.user_modules.envis_preprocessor import EnvisPreProcessor
from fedrec.utilities import registry
from fedrec.utilities.logger import BaseLogger
from fedrec.utilities.random_state import Reproducible


class BaseActor(Reproducible, ABC):
    """Base Actor implements the core federated learning logic.
    It encapsulates the ML trainer to enable distributed training
    for the models defined in the standard setting.


    Attributes
    ----------
    worker_id : str
        The unique id alloted to the worker by the orchestrator
    persistent_storage : str
        The location to serialize and store the `WorkerState`
    is_mobile : bool
        Whether the worker represents a mobile device or not
    round_idx : int
        Number of local iterations finished
    """

    def __init__(self,
                 worker_id: str,
                 config: Dict,
                 logger: BaseLogger,
                 is_mobile: bool = True,
                 round_idx: int = 0):

        super().__init__(config["random"])
        self.round_idx = round_idx
        self.worker_id = worker_id
        self.is_mobile = is_mobile
        self.persistent_storage = (config["log_dir"]["PATH"]
                                   + "worker_id_"
                                   + str(self.worker_id))
        if not os.path.exists(self.persistent_storage):
            os.makedirs(self.persistent_storage)
        self.config = config
        self.logger = logger

        modelCls = registry.lookup('model', config["model"])
        self.model_preproc: EnvisPreProcessor = registry.instantiate(
            modelCls.Preproc,
            config["model"]['preproc'])
        self._model = None
        self._optimizer = None
        self.worker = None
        self.worker_funcs = {}

    @property
    def name(self):
        return self.__class__.__name__.lower()

    @property
    def optimizer(self):
        return None

    @abstractmethod
    def serialize(self):
        raise NotImplementedError

    @abstractclassmethod
    def load_worker(cls, *args, **kwargs):
        raise NotImplementedError

    @property
    def model(self):
        if self._model is not None:
            return self._model

        with self.model_random:
            # 1. Construct model
            self.model_preproc.load_data_description()
            self._model = registry.construct(
                'model', self.config['model'],
                preprocessor=self.model_preproc,
                unused_keys=('name', 'preproc')
            )
            if torch.cuda.is_available():
                self._model.cuda()
        # model being used by trainer
        return self._model

    def _get_model_params(self):
        """Get the current model parameters for the trainer .

        Returns
        -------
        Dict:
            A dict containing the model weights.
        """
        return self.wrap_tensors(self.model.state_dict())

    def _get_optimizer_params(self):
        if self._optimizer is not None:
            return self.wrap_tensors(self.optimizer.state_dict())
        else:
            raise ValueError("No optimizer found")

    def load_model(self, state_dict):
        """Update the model weights with weights.

        Parameters
        ----------
        weights : StateTensors
            The model weights to be loaded into the optimizer
        """
        if isinstance(state_dict, dict):
            assert all(isinstance(value, EnvisTensors)
                       for value in state_dict.values())
            self.model.load_state_dict({
                k: v.get_torch_obj() for k, v in state_dict.items()})
        elif isinstance(state_dict, StateTensors):
            self.model.load_state_dict(state_dict.get_torch_obj())
        else:
            ValueError("Invalid state_dict type")

    def load_optimizer(self, state_dict: StateTensors):
        self.optimizer.load_state_dict(state_dict.get_torch_obj())

    def wrap_tensors(self, tensors, suffix=""):
        return StateTensors(
            storage=self.persistent_storage,
            tensors=tensors,
            suffix=suffix
        )

    def process_args(self, argument):
        # TODO implement other secondary processing if needed
        # TODO : Fix randint
        if isinstance(argument, (Tuple, List)):
            return [
                self.process_args(arg)
                for arg in argument
            ]
        elif isinstance(argument, torch.Tensor):
            return EnvisTensors(str(randint(0,100)), self.persistent_storage, argument)
        elif isinstance(argument, Dict):
            if (all(isinstance(value, torch.Tensor)
                    for value in argument.items())):
                return self.wrap_tensors(argument, str(randint(0, 100)))
            return {
                key: self.process_args(value)
                for key, value in argument.items()
            }
        else:
            return argument

    def run(func_name, *args, **kwargs):
        pass
