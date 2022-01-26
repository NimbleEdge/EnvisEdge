from typing import Dict, List

from fedrec.python_executors.base_actor import ActorState
from fedrec.utilities import registry
from dataclasses import dataclass


@registry.load("serializer", "Message")
@dataclass
class Message(object):
    '''
    Stores information into Message object

    Args:
    -----
        senderid : str
            id of sender
        receiverid : str
            id of receiver
    '''
    __type__ = "Message"

    def __init__(self, senderid, receiverid):
        self.senderid = senderid
        self.receiverid = receiverid

    def get_sender_id(self):
        return self.senderid

    def get_receiver_id(self):
        return self.receiverid


@registry.load("serializer", "JobSubmitMessage")
@dataclass
class JobSubmitMessage(Message):
    '''
    Stores message of job submit request

    Args:
    -----
        job_type : str
            type of job
        job_args : list
            list of job arguments
        job_kwargs: dict
            Extra key-pair arguments related to job
        senderid : str
            id of sender
        receiverid : str
            id of reciever
        workerstate : ActorState
            ActorState object containing worker's state
    '''
    __type__ = "JobSubmitMessage"

    def __init__(self,
                 job_type,
                 job_args,
                 job_kwargs,
                 senderid,
                 receiverid,
                 workerstate):
        super().__init__(senderid, receiverid)
        self.job_type: str = job_type
        self.job_args: List = job_args
        self.job_kwargs: Dict = job_kwargs
        self.workerstate: ActorState = workerstate

    def get_worker_state(self):
        return self.workerstate

    def get_job_type(self):
        return self.job_type


@registry.load("serializer", "JobResponseMessage")
@dataclass
class JobResponseMessage(Message):
    '''
    Stores job response message

    Args:
    -----
        job_type : str
            type of job (train/test)
        senderid : str
            id of sender
        receiverid : str
            id of receiver
        results : dict
            dict of results obtained from job completion
    '''
    __type__ = "JobResponseMessage"

    def __init__(self, job_type, senderid, receiverid):
        super().__init__(senderid, receiverid)
        self.job_type: str = job_type
        self.results = {}
        self.errors = None

    @property
    def status(self):
        if self.errors is None:
            return True
        else:
            return False
