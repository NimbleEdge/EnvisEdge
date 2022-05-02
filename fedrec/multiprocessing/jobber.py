"""Jobber python module for scheduling job requrests to run
in sequence. It is a utility program that executes
the pipeline and publishes job requests.
"""

import atexit
import os
from typing import Dict

from fedrec.data_models.job_response_model import JobResponseMessage
from fedrec.data_models.job_submit_model import JobSubmitMessage
from fedrec.python_executors.base_actor import BaseActor
from fedrec.utilities import registry


class Jobber:
    """
    Jobber class handles job requests based on job types
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

        # look for the key in the dictionary and return its object
        self.comm_manager = registry.construct(
            "communication_interface", config=com_manager_config)
        self.logger = logger
        atexit.register(self.stop)

    def run(self) -> None:
        """
        After calling the function, the Communication
        Manager listens to the queue for messages,
        executes the job request and publishes the results
        in that order.
        """
        while True:
            try:
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
                self.stop(False)


    def execute(self, message: JobSubmitMessage) -> JobResponseMessage:
        """
        This function takes message object and
        stores the job request to publish.
        Parameters
        ----------
        message : object
            Creates a message object for job submit request
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
        Publishes the result on kafka after executing the job request
        Parameters
        ----------
        job_result : object
            Creates message objects for job response message
        """
        self.comm_manager.send_message(job_result)
        pass

    def stop(self, success=True) -> None:
        '''
        This function is called after the end of a job request
        to perform cleanup, logging, etc.
        '''
        self.comm_manager.finish()
        os._exit(success)
