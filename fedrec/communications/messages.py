from enum import Enum, auto

class ProcMessage(Enum):
    SYNC_MODEL = 1
    TRAIN_JOB = auto()
    TEST_JOB = auto()

class JobCompletions():
    SENDER_ID = 1
    STATUS = True
    RESULTS = {}
    ERRORS = ""


class Message(object):
    def __init__(self, senderid, receiverid):
        self.senderid = senderid
        self.receiverid = receiverid

    def get_sender_id(self):
        return self.senderid

    def get_receiver_id(self):
        return self.receiverid

class JobSubmitMessage(Message):
    def __init__(self, job_type, senderid, receiverid, workerState):
        super().__init__(senderid, receiverid)
        if job_type == 'train':
            self.job_type = ProcMessage.TRAIN_JOB
        else:
            self.job_type = ProcMessage.TEST_JOB
        self.workerstate = workerState
        
    def get_worker_state(self):
        return self.workerstate

    def get_job_type(self):
        return self.job_type

class JobResponseMessage(Message):
    def __init__(self, senderid, receiverid):
        super().__init__(senderid,receiverid)
    
    
class ModelRequestMessage(Message):
    def __init__(self, senderid, receiverid):
        super().__init__(senderid, receiverid)
    
class ModelResponseMessage(Message):
    def __init__(self, senderid, receiverid, modelweights, local_sample_num):
        super().__init__(senderid, receiverid)        
        self.modelweights = modelweights
        self.local_sample_num = local_sample_num

    def get_model_weights(self):
        return self.modelweights
    
    def get_local_sample_num(self):
        return self.local_sample_num

    

    
    