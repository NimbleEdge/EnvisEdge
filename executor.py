from argparse import ArgumentParser
from atexit import register

import yaml
from fedrec.multiprocessing.jobber import Jobber
from fedrec.multiprocessing.process_manager import ProcessManager

from fedrec.python_executors.aggregator import Aggregator
from fedrec.python_executors.trainer import Trainer
from fedrec.utilities import registry, roles
from fedrec.utilities.logger import NoOpLogger, TBLogger
from fedrec.utilities.random_state import Reproducible


class JobExecutor(Reproducible):
    def __init__(self, config_dict, worker_idx, logger, role, **kwargs) -> None:
        """ Class responsible for running aggregator/trainer on a single node.
        """
        # Construct trainer and do training
        self.config_dict = config_dict
        if role == roles.Roles.TRAINER:
            self.worker = Trainer(worker_idx, config_dict, logger, **kwargs)
        elif role == roles.Roles.AGGREGATOR:
            self.worker = Aggregator(worker_idx, config_dict, logger, **kwargs)

        self.jobber = Jobber(
            self.worker, logger, config_dict["multiprocessing"]["communications"])

    def run(self):
        return self.jobber.run()


def main():
    parser = ArgumentParser()
    parser.add_argument("--config", type=str, required=True)
    parser.add_argument("--logdir", type=str, default=None)

    args = parser.parse_args()

    with open(args.config, "r") as stream:
        config_dict = yaml.safe_load(stream)

    if args.logger:
        if args.logdir is None:
            raise ValueError("logdir cannot be null if logging is enabled")
        logger = TBLogger(args.logdir)
    else:
        logger = NoOpLogger()

    process_manager: ProcessManager = registry.construct(
        "process_manager", config_dict["multiprocessing"]["distribution"])
    process_manager.start()


if __name__ == "__main__":
    main()
