from typing import Dict
<<<<<<< HEAD
<<<<<<< HEAD
from fedrec.communications.messages import JobResponseMessage, JobSubmitMessage
=======
>>>>>>> 667eb80 (support aggregator and trainer in jobber)
=======
from fedrec.communications.messages import JobResponseMessage, JobSubmitMessage
>>>>>>> cc840ea (remove unnecessary imports)

from fedrec.multiprocessing.jobber import Jobber
from fedrec.python_executors.base_actor import BaseActor
from fedrec.utilities import registry
<<<<<<< HEAD
<<<<<<< HEAD
=======
from mpi4py import MPI
>>>>>>> 667eb80 (support aggregator and trainer in jobber)
=======
>>>>>>> cc840ea (remove unnecessary imports)


@registry.load("multiprocessing", "MPI")
class MPIProcess:
    """
    Construct an MPI Process Manager for Trainers

    Attributes
    ----------
    trainer : BaseTrainer
        Trainer executing on the actor
    logger : logger
        Logger Object
    com_manager_config : dict
        Communication of config manager stored as dictionary
    """
    def __init__(self,
                 worker: BaseActor,
                 logger,
                 com_manager_config: Dict) -> None:
<<<<<<< HEAD
<<<<<<< HEAD
=======
        self.pool = MPI.COMM_WORLD
        self.rank = self.pool.Get_rank()
        self.num_processes = self.pool.Get_size()
>>>>>>> 667eb80 (support aggregator and trainer in jobber)
=======
>>>>>>> cc840ea (remove unnecessary imports)
        self.jobber = Jobber(worker=worker, logger=logger)
        self.process_comm_manager = registry.construct(
            "communications", config_dict=com_manager_config)

    def run(self) -> None:
        """
        After calling the function, the Communication 
        Manager listens to the queue for messages, 
        executes the job request and publishes the results 
        in that order. It will stop listening after receiving
        job_request with job_type "STOP" 
        """
        while True:
            job_request: JobSubmitMessage = self.process_comm_manager.receive_message()
            if job_request.job_type == "STOP":
                return

            result = self.jobber.run(job_request)
            self.publish(result)

    def publish(self, job_result: JobResponseMessage) -> None:
<<<<<<< HEAD
        """
        Publishes the result after executing the job request
        """
=======
>>>>>>> cc840ea (remove unnecessary imports)
        self.process_comm_manager.send_message(job_result.result())

    def stop(self) -> None:
        self.process_comm_manager.stop()
