import zmq
from time import sleep
from abc import ABC, abstractmethod
import asyncio

class AbstractComManager(ABC):

    @abstractmethod
    def send(self):
        pass

    @abstractmethod
    def handle_message(self):
        pass

class ZeroMQ(AbstractComManager):
    def __init__(self, is_subscriber):
        self.context = zmq.Context()
        self.message = {}
        if is_subscriber:            
            self.subscriber = self.context.socket(zmq.SUB)
        else:
            self.publisher = self.context.socket(zmq.PUB)

        def handle_message(self):
            print('Connecting to port . . . . ./n')
            self.subscriber.bind('tcp://127.0.0.1:2000')
            self.subscriber.setsockopt(zmq.SUBSCRIBE, b'')

            while True:
                # Here I am assuming the message is a form of dictionary 
                # where it has sender_id and receiver_id are there as Key
                self.message = self.subscriber.recv_pyobj() 

            return self.message
                
        def send(message):
            print("Connecting to Port . . . . ./n")
            self.publisher.connect('tcp://127.0.0.1:2000')
            print("Sending Message . . . . . /n")
            while True:
                sleep(2)
                self.publisher.send_pyobj(message)

        def close(self):
                self.publisher.close()
                self.subscriber.close()
                self.context.term()
            

            

  

  


