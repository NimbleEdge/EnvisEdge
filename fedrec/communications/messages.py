from enum import Enum

class ProcMessage(Enum):
    SYNC_MODEL = 1

class JobCompletions():
    SENDER_ID = 1
    STATUS = True
    RESULTS = {}
    ERRORS = ""


class Message(object):
    def __init__(self, senderid, receiverid):
        self.senderid = senderid
        self.receiverid = receiverid

class JobSubmitMessage(Message):
    def __init__(self, senderid, receiverid):
        super().__init__(senderid, receiverid)

    def get_sender_id(self):
        return self.senderid

    def get_receiver_id(self):
        return self.receiverid

    def get_worker_state(self):
        return self.workerstate

    def add_WorkerState(self, workerState):
        self.workerstate = workerState
    
    def add_modelweights(self, modelweights):
        self.modelweights = modelweights
    
    def add_local_sample_num(self, local_sample_num):
        self.local_sample_num = local_sample_num

    def get_model_weights(self):
        return self.modelweights

    def get_local_sample_num(self):
        return self.local_sample_num

    
    