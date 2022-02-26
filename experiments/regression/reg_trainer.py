from typing import Dict

import attr
from fedrec import base_trainer
from fedrec.preprocessor import PreProcessor
from fedrec.utilities import registry
from fedrec.utilities.logger import BaseLogger
from fedrec.utilities.random_state import Reproducible


@attr.s
class RegressionConfig:
    eval_every_n = attr.ib(default=10000)
    report_every_n = attr.ib(default=10)
    save_every_n = attr.ib(default=2000)
    keep_every_n = attr.ib(default=10000)

    batch_size = attr.ib(default=32)
    eval_batch_size = attr.ib(default=128)
    num_epochs = attr.ib(default=-1)

    num_batches = attr.ib(default=-1)

    @num_batches.validator
    def check_only_one_declaration(instance, _, value):
        if instance.num_epochs > 0 & value > 0:
            raise ValueError(
                "only one out of num_epochs and num_batches must be declared!")

    num_eval_batches = attr.ib(default=-1)
    eval_on_train = attr.ib(default=False)
    eval_on_val = attr.ib(default=True)

    num_workers = attr.ib(default=0)
    pin_memory = attr.ib(default=True)


@registry.load('trainer', 'regression')
class RegressionTrainer(Reproducible):

    def __init__(
            self,
            config_dict: Dict,
            logger: BaseLogger) -> None:

        super().__init__(config_dict["random"])
        self.config_dict = config_dict
        self.train_config = RegressionConfig(
            **config_dict["trainer"]["config"]
        )
        self.logger = logger
        modelCls = registry.lookup('model', config_dict["model"])
        self.model_preproc: PreProcessor = registry.instantiate(
            modelCls.Preproc,
            config_dict["model"]['preproc'])

        self._model = None
        self._data_loaders = {}

        self._optimizer = None
        self._saver = None

    base_trainer.reset_loaders()

    # @staticmethod
    base_trainer._yield_batches_from_epochs(loader, start_epoch)

    # @property
    base_trainer.model(self)

    # @property
    base_trainer.optimizer(self)
    base_trainer.get_scheduler(self, optimi, **kwargs)

    # @property
    base_trainer.saver(self)

    # @property
    base_trainer.data_loaders(self)

    # @staticmethod
    base_trainer.eval_model(model,
                            loader,
                            eval_section,
                            logger,
                            num_eval_batches=-1,
                            best_acc_test=None,
                            best_auc_test=None,
                            step=-1)
    base_trainer.test(self)
    base_trainer.train(self, modeldir=None)
