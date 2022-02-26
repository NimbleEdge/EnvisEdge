import sys
from argparse import ArgumentParser
from typing import Callable, Dict

import yaml

from fedrec.multiprocessing.jobber import Jobber
from fedrec.multiprocessing.process_manager import ProcessManager
from fedrec.python_executors.aggregator import Aggregator
from fedrec.python_executors.trainer import Trainer
from fedrec.utilities import registry
from fedrec.utilities.logger import BaseLogger, NoOpLogger


class JobExecutor():
    def __init__(self,
                 actorCls: Callable,
                 config: Dict,
                 logger: BaseLogger,
                 **kwargs) -> None:
        """ Class responsible for running aggregator/trainer on a single node.
        """
        # Construct trainer and do training
        self.config = config
        if not set(['experiments',
                    'fedrec',
                    'fl_strategies']).issubset(set(sys.modules.values())):
            import experiments
            import fedrec
            import fl_strategies
            import datasets
        self.worker = actorCls(
            0, config, logger, **kwargs)
        self.jobber = Jobber(
            self.worker, logger,
            config["multiprocessing"]["communication_interface"])

    def run(self):
        return self.jobber.run()


def main():
    parser = ArgumentParser()
    parser.add_argument("--config", type=str, required=True)
    parser.add_argument("--logdir", type=str, default=None)
    parser.add_argument("--logger", action="store_true", default=False)
    args = parser.parse_args()

    with open(args.config, "r") as stream:
        config_dict = yaml.safe_load(stream)

    if args.logger:
        if args.logdir is None:
            raise ValueError("logdir cannot be null if logging is enabled")
        from fedrec.utilities.logger import TBLogger
        logger = TBLogger(args.logdir)
    else:
        logger = NoOpLogger()

    process_manager: ProcessManager = registry.construct(
        "process_manager", config_dict["multiprocessing"]["process_manager"])

    process_manager.distribute(
        JobExecutor, Aggregator.__name__,
        config_dict["multiprocessing"]["num_aggregators"],
        actorCls=Aggregator,
        config=config_dict, logger=logger,
    )
    process_manager.distribute(
        JobExecutor, Trainer.__name__,
        config_dict["multiprocessing"]["num_trainers"],
        actorCls=Trainer,
        config=config_dict, logger=logger,
    )

    process_manager.start(Aggregator.__name__, "run")
    process_manager.start(Trainer.__name__, "run")

    import time
    time.sleep(234234)


if __name__ == "__main__":
    main()
