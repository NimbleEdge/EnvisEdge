import zmq
from time import sleep
from abc import ABC, abstractmethod
from fedrec.utilities import registry
import asyncio

class AbstractComManager(ABC):

    @abstractmethod
    def send_message(self):
        pass

    @abstractmethod
    def handle_message(self):
        pass
@registry.load("communications", "ZeroMQ")
class ZeroMQ(AbstractComManager):
    def __init__(self, is_subscriber):
        self.context = zmq.Context()
        self.queue = asyncio.Queue()
        if is_subscriber:            
            self.subscriber = self.context.socket(zmq.SUB)
        else:
            self.publisher = self.context.socket(zmq.PUB)
        if self.publisher:
            print("Connecting to Port . . . . ./n")
            self.publisher.connect('tcp://127.0.0.1:2000')

        async def handle_message(self):
            if self.subscriber:
                print('Connecting to port . . . . ./n')
                self.subscriber.bind('tcp://127.0.0.1:2000')
                self.subscriber.setsockopt(zmq.SUBSCRIBE, b'')

                while True:
                    # Here I am assuming the message is a form of dictionary 
                    # where it has sender_id and receiver_id are there as Key
                    message = self.subscriber.recv_pyobj() 
                    await self.queue.put(message)

        def get_queue(self):
            return self.queue
                
        def send_message(message):
            print("Sending Message . . . . . /n")
            self.publisher.send_pyobj(message)

        def close(self):
            if self.publisher:
                self.publisher.close()
            elif self.subscriber:
                self.subscriber.close()
            self.context.term()
            

            

  

  


