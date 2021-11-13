from typing import Dict
from fedrec.communications.messages import JobResponseMessage, JobSubmitMessage

from fedrec.multiprocessing.jobber import Jobber
from fedrec.python_executors.base_actor import BaseActor
from fedrec.utilities import registry


@registry.load("multiprocessing", "MPI")
class MPIProcess:

    def __init__(self,
                 worker: BaseActor,
                 logger,
                 com_manager_config: Dict) -> None:
        self.jobber = Jobber(worker=worker, logger=logger)
        self.process_comm_manager = registry.construct(
            "communications", config_dict=com_manager_config)

    def run(self) -> None:
        while True:
            job_request: JobSubmitMessage = self.process_comm_manager.receive_message()
            if job_request.job_type == "STOP":
                return

            result = self.jobber.run(job_request)
            self.publish(result)

    def publish(self, job_result: JobResponseMessage) -> None:
        self.process_comm_manager.send_message(job_result.result())

    def stop(self) -> None:
        self.process_comm_manager.stop()
