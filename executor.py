from fedrec.federated_worker import FederatedWorker, Neighbour, WorkerDataset
from fedrec.utilities.cuda_utils import mapping_processes_to_gpus
import logging
import os
import socket
from argparse import ArgumentParser

import setproctitle
import torch
import functools

import yaml
from fedrec.trainers.base_trainer import BaseTrainer
from fedrec.utilities import registry
from fedrec.utilities.logger import NoOpLogger, TBLogger
from fedrec.utilities.random_state import Reproducible



class JobExecutor(Reproducible):
    def __init__(self, args, config_dict, process_id, worker_num, logger) -> None:

        device = mapping_processes_to_gpus(
            config_dict["communications"]["gpu_map"], process_id, worker_num
        )
        # load data
        self.model_preprocs = load_and_split_data()

        # Construct trainer and do training
        self.config_dict = config_dict
        self.train_config = registry.construct(
            "train_config",
            merge_config_and_args(self.config_dict["train"]["config"], args),
        )
        self.fl_config: FL_Config = registry.construct("")
        self.logger = logger
        self.process_id = process_id
        self.trainer: BaseTrainer = registry.construct(
            "trainer",
            config={"name": config_dict["train"]["name"]},
            config_dict=config_dict,
            train_config=self.train_config,
            model_preproc=None,
            logger=logger,
        )

        # If only process_id ==0 has access to comm manager/comm_stream
        # all tasks need to go through it. Bad for parallelization & async
        if self.process_id == 0:
            self._setup_workers()
        self.process_manager = registry.construct(
            "process_manager",
            config_dict=config_dict["process_manager"],
            trainer=self.trainer,
            logger=self.logger,
        )

    def start_executor(self):
        self.process_manager.start_processes()
        


def main():    
    parser = ArgumentParser()
    parser.add_argument("--config", type=str)
    parser.add_argument("--logdir", type=str, default=None)

    args = parser.parse_args()

    with open(args.config, "r") as stream:
        config_dict = yaml.safe_load(stream)
    
    comm, process_id, worker_number = FedML_init()

    # Please check "GPU_MAPPING.md" to see how to define the topology
    logging.info("process_id = %d, size = %d" % (process_id, worker_number))

    if args.logger:
        if args.logdir is None:
            raise ValueError("logdir cannot be null if logging is enabled")
        logger = TBLogger(args.logdir)
    else:
        logger = NoOpLogger()


if __name__ == "__main__":
    main()