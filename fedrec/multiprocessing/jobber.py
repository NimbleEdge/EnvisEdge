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

        # append worker infromation to dictionary
        if com_manager_config["producer_topic"] is not None:
            com_manager_config["producer_topic"] = com_manager_config[
                "producer_topic"] + "-" + self.worker.name
        if com_manager_config["consumer_topic"] is not None:
            com_manager_config["consumer_topic"] = com_manager_config[
                "consumer_topic"] + "-" + self.worker.name

        self.comm_manager = registry.construct(
            "communications", config=com_manager_config)
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
                print("Waiting for job request")
                job_request = self.comm_manager.receive_message()
                print(
                    "Received job request"
                    + f"{job_request}, {type(job_request)} on"
                    + self.worker.name)

                result = self.execute(job_request)
                self.publish(result)
        except Exception as e:
            print(f"Exception {e}")
            self.stop()

    def execute(self, message: JobSubmitMessage):
        """
        executes the BaseActor model ,implemented in the worker funcs and run them according to job_type
        Attributes
        ----------
        message: JobSubmitMessage
            JobSubmitMessage containing message details

        Returns
        ----------
        result_message: JobResponseMessage
            JobResponseMessage containing response to message like job result
        """
        result_message = JobResponseMessage(
            job_type=message.job_type,
            senderid=message.receiverid,
            receiverid=message.senderid)
        try:
            self.worker.load_worker(message.workerstate)
            job_result = self.worker.run(message.job_type,
                                         *message.job_args,
                                         **message.job_kwargs)
            print(job_result)
            result_message.results = job_result
        except Exception as e:
            print(e)
            result_message.errors = e
        return result_message

    def publish(self, job_result: JobResponseMessage) -> None:
        """
        Publishes the result after executing the job request
        """
        self.comm_manager.send_message(job_result)

    def stop(self) -> None:
        self.comm_manager.finish()
