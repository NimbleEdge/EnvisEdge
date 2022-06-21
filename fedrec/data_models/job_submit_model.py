from dataclasses import dataclass
from typing import Dict, List

from fedrec.data_models.base_actor_state_model import ActorState
from fedrec.data_models.messages import Message
from fedrec.serialization.serializer_registry import (deserialize_attribute,
                                                      serialize_attribute)
from fedrec.utilities.registry import Registrable


@Registrable.register_class_ref
@dataclass
class JobSubmitMessage(Message):
    '''
    Creates a message object for job submit request

    Attributes
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

    def get_receiver_id(self):
        '''Returns receiverid from JobSubmitMessage Object'''
        return super().get_receiver_id()

    def serialize(self):
        # pack the arguments after serilization into the resposne dict
        response_dict = {
            "job_type": self.job_type,
            "job_args": serialize_attribute(
                self.job_args),
            "job_kwargs": serialize_attribute(
                self.job_kwargs),
            "senderid": self.senderid,
            "receiverid": self.receiverid,
            "workerstate": serialize_attribute(
                self.workerstate)
        }
        return self.append_type(response_dict)

    @classmethod
    def deserialize(cls, obj):
        # unpack the response dict to create the class object
        worker_state = None
        job_args = deserialize_attribute(obj["job_args"])
        job_kwargs = deserialize_attribute(obj["job_kwargs"])
        worker_state = deserialize_attribute(obj["workerstate"])
        
        return cls(
            obj["job_type"],
            job_args,
            job_kwargs,
            obj["senderid"],
            obj["receiverid"],
            worker_state
        )
