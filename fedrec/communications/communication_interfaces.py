import zmq
from time import sleep
from abc import ABC, abstractmethod
from fedrec.utilities import registry
from global_comm_stream import CommunicationStream
import asyncio

class AbstractComManager(ABC):

    @abstractmethod
    def send_message(self):
        pass

    @abstractmethod
    def subscribe_method(self):
        pass
@registry.load("communications", "ZeroMQ")
class ZeroMQ(AbstractComManager):
    def __init__(self, is_subscriber):
        self.context = zmq.Context()
        if is_subscriber:            
            self.subscriber = self.context.socket(zmq.SUB)
        else:
            self.publisher = self.context.socket(zmq.PUB)
        if self.publisher:
            print("Connecting to Port . . . . ./n")
            self.publisher.connect('tcp://127.0.0.1:2000')
        if self.subscriber:
            print('Connecting to port . . . . ./n')
            self.subscriber.bind('tcp://127.0.0.1:2000')
            self.subscriber.setsockopt(zmq.SUBSCRIBE, b'')

        def subscribe_method(self):
            if self.subscriber:
                global_dict = CommunicationStream.get_global_hash_map()
                while True:
                    # Here I am assuming the message is a form of dictionary 
                    # where it has sender_id and receiver_id are there as Key
                    message = self.subscriber.recv_pyobj() 
                    if message['receiver_id'] in global_dict:
                        queue = global_dict[message['receiver_id']]
                        # replace the token with the key value name
                        # for the model stored 
                        queue.put(message['token'])

        def send_message(message):
            print("Sending Message . . . . . /n")
            self.publisher.send_pyobj(message)

        def close(self):
            if self.publisher:
                self.publisher.close()
            elif self.subscriber:
                self.subscriber.close()
            self.context.term()
            

            

  

  


