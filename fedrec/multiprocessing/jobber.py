import atexit
from typing import Dict

from fedrec.communications.messages import JobResponseMessage, JobSubmitMessage
from fedrec.python_executors.base_actor import BaseActor
from fedrec.utilities import registry
from fedrec.utilities.serialization import deserialize_object, serialize_object


class Jobber:
    """
    Jobber class handles job requests based on job type
    Attributes
    ----------
    worker : BaseActor
        Trainer/Aggregator executing on the actor
    logger : logger
        Logger Object
    com_manager_config : dict
        Configuration of communication manager stored as dictionary
    """

    def __init__(self, worker, logger, com_manager_config: Dict) -> None:
        self.logger = logger
        self.worker: BaseActor = worker
        self.worker_funcs = {func.__name__: func for func in dir(
            self.worker) if callable(func)}
        self.comm_manager = registry.construct(
            "communications", config_dict=com_manager_config)
        self.logger = logger
        atexit.register(self.stop)

    def run(self) -> None:
        """
        After calling the function, the Communication 
        Manager listens to the queue for messages, 
        executes the job request and publishes the results 
        in that order.
        """
        try:
            while True:
                job_request: JobSubmitMessage = self.process_comm_manager.receive_message()
                result = self.execute(job_request)
                self.publish(result)
        except Exception as e:
            self.logger.error(f"Exception {e}")
            self.stop()

    def execute(self, message: JobSubmitMessage):
        if message.job_type in self.worker_funcs:
            job_args = [
                deserialize_object(i) for i in message.job_args.items()]
            job_kwargs = {
                key: deserialize_object(val)
                for key, val in message.job_kwargs.items()}
            result_message = JobResponseMessage(
                job_type=message.job_type,
                senderid=message.receiverid,
                receiverid=message.senderid)
            try:
                job_result = self.worker_funcs[message.job_type](
                    *job_args, **job_kwargs)
                result_message.results = {key: serialize_object(
                    val) for key, val in job_result}
            except Exception as e:
                result_message.errors = e
            return result_message
        else:
            raise ValueError(
                f"Job type <{message.job_type}> not part of worker <{self.worker.__class__.__name__}> functions")

    def publish(self, job_result: JobResponseMessage) -> None:
        """
        Publishes the result after executing the job request
        """
        self.comm_manager.send_message(job_result.result())

    def stop(self) -> None:
        self.comm_manager.stop()
