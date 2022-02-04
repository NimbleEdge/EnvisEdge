from typing import Dict, List

from fedrec.python_executors.base_actor import ActorState
from fedrec.utilities import registry
from dataclasses import dataclass


@registry.load("serializer", "Message")
@dataclass
class Message(object):
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
