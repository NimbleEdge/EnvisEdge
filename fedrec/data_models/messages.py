from dataclasses import dataclass
from fedrec.utilities.serialization_utils import Serializable



@dataclass
class Message(Serializable):
    '''
    Base class that is inherited by other Message classes

    Attributes:
    -----------
        senderid : str
            id of sender
        receiverid : str
            id of receiver
    '''

    def __init__(self, senderid, receiverid):
        self.senderid = senderid
        self.receiverid = receiverid

    def get_sender_id(self):
        '''Returns senderid from Message Object'''
        return self.senderid

    def get_receiver_id(self):
        '''Returns senderid from Message Object'''
        return self.receiverid
