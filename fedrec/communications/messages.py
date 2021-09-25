from abc import ABC, abstractmethod
from enum import Enum

class ProcMessage(Enum):
    SYNC_MODEL = 1

class JobCompletions():
    SENDER_ID = 1
    STATUS = True
    RESULTS = {}
    ERRORS = ""


class Message(ABC):
    def __init__(self, senderid, receiverid):
        self.senderid = senderid
        self.receiverid = receiverid
        self.data = {}
    
    @abstractmethod
    def get_sender_id(self):
        return self.senderid

    @abstractmethod
    def get_receiver_id(self):
        return self.receiverid

class JobSubmission(Message):
    def __init__(self, senderid, receiverid, workerState):
        super().__init__(senderid, receiverid)
        self.workerstate = workerState

    def get_worker_state(self):
        return self.workerstate

class train_JobSubmission(JobSubmission):
    def __init__(self, senderid, receiverid, workerState):
        super().__init__(senderid, receiverid, workerState)

class test_JobSubmmission(JobSubmission):
    def __init__(self, senderid, receiverid, workerState):
        super().__init__(senderid, receiverid, workerState)

class get_model(Message):
    def __init__(self, senderid, receiverid):
        super().__init__(senderid, receiverid)

class send_model(Message):
    def __init__(self, senderid, receiverid, modelweights, local_sample_num):
        super().__init__(senderid, receiverid)
        self.modelweights = modelweights
        self.local_sample_num = local_sample_num

    def get_model_weights(self):
        return self.modelweights

    def get_local_sample_num(self):
        return self.local_sample_num
    