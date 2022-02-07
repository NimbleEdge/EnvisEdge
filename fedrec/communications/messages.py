from typing import Dict, List

from fedrec.python_executors.base_actor import ActorState
from fedrec.utilities import registry
from dataclasses import dataclass


@registry.load("serializer", "Message")
@dataclass
class Message(object):
    '''
    Base class that is inherited by other Message classes

    Attributes:
    -----------
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
        '''Returns senderid from Message Object'''
        return self.senderid

    def get_receiver_id(self):
        '''Returns senderid from Message Object'''
        return self.receiverid


@registry.load("serializer", "JobSubmitMessage")
@dataclass
class JobSubmitMessage(Message):
    '''
    Creates a message object for job submit request

    Attributes:
    -----------
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
        '''Returns workerstate from JobSubmitMessage Object'''
        return self.workerstate

    def get_job_type(self):
        '''Returns job_type from JobSubmitMessage Object'''
        return self.job_type


@registry.load("serializer", "JobResponseMessage")
@dataclass
class JobResponseMessage(Message):
    '''
    Creates message objects for job response message

    Attributes:
    -----------
        job_type : str
            type of job (train/test)
        senderid : str
            id of sender
        receiverid : str
            id of receiver
        results : dict
            dict of results obtained from job completion
        errors : null
    '''
    __type__ = "JobResponseMessage"

    def __init__(self, job_type, senderid, receiverid):
        super().__init__(senderid, receiverid)
        self.job_type: str = job_type
        self.results = {}
        self.errors = None

    @property
    def status(self):
        '''
        Check if errors is None and returns response
        message status accordingly
        '''
        if self.errors is None:
            return True
        else:
            return False
