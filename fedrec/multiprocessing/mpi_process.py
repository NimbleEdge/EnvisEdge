from typing import Dict
from fedrec.utilities import registry
from fedrec.trainers.base_trainer import BaseTrainer
from fedrec.multiprocessing.jobber import Jobber
from mpi4py import MPI


@registry.load("multiprocessing", "MPI")
class MPIProcess:

    def __init__(self,
                 trainer: BaseTrainer,
                 logger,
                 com_manager_config: Dict) -> None:
        self.pool = MPI.COMM_WORLD
        self.rank = self.pool.Get_rank()
        self.num_processes = self.pool.Get_size()
        self.jobber = Jobber(trainer=trainer, logger=logger)
        self.process_comm_manager = registry.construct(
            "comm_manager", config_dict=com_manager_config)

    def run(self) -> None:
        while True:
            job_request = self.process_comm_manager.receive_message()
            if job_request.JOB_TYPE == "STOP":
                return
            
            result = self.jobber.run(job_request)
            self.publish(result)

    def publish(self, job_result) -> None:
        self.process_comm_manager.send_message(job_result.result())

    def stop(self) -> None:
        self.process_comm_manager.stop()
