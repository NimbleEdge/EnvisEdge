from typing import Dict

from fedrec.user_modules.envis_trainer import EnvisTrainer, TrainConfig
from fedrec.utilities import registry
from fedrec.utilities.logger import BaseLogger


@registry.load('trainer', 'regression')
class RegressionTrainer(EnvisTrainer):

    def __init__(
            self,
            config_dict: Dict,
            logger: BaseLogger,
            client_id=None) -> None:

        super().__init__(config_dict, logger, client_id)
        self.train_config = TrainConfig(
            **config_dict["trainer"]["config"]
        )
