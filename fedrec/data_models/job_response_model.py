from typing import Dict, List

from fedrec.python_executors.base_actor import ActorState
from fedrec.data_models.messages import Message
from fedrec.utilities import registry
from dataclasses import dataclass
from fedrec.serialization.abstract_serializer import (
    AbstractSerializer,
    get_serializer,
    serializable_with)

class JobResponseSerializer(AbstractSerializer):

    def __init__(self,serialization_strategy):
        super().__init__(serialization_strategy)

    def serialize(self, obj):
        response_dict = {}
        response_dict["job_type"] = obj.job_type
        response_dict["job_args"] = [self.serialize_attribute(arg)
                                     for arg in obj.obj_args]
        response_dict["job_kwargs"] = [self.serialize_attribute(kwarg)
                                       for kwarg in obj.obj_kwargs]
        response_dict["worker_state"] = self.serialize_attribute(
            obj.workerstate)

        return self.serialization_strategy.unparse(response_dict)

    def deserialize(self, obj: Dict):
        job_type = obj.job_type
        job_args = [self.deserialize_attribute(arg) for
                    arg in obj.obj_args]
        job_kwargs = [self.deserialize_attribute(kwarg) for
                      kwarg in obj.obj_kwargs]
        worker_state = self.deserialize_attribute(obj.workerstate)
        
        JobResponseMessage(obj["job_type"],
                           job_args,
                           job_kwargs,
                           worker_state)
        
        return super().deserialize()

@serializable_with(JobResponseSerializer)
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

