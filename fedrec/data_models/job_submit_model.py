from typing import Dict, List

from dataclasses import dataclass
from fedrec.data_models.base_actor_state_model import ActorState
from fedrec.data_models.messages import Message


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
