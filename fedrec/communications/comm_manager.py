from collections import defaultdict
from types import FunctionType
from abstract_comm_manager import ZeroMQ
from fedrec.utilities import registry
from global_comm_stream import CommunicationStream
from time import sleep
import asyncio

MESSAGE_HANDLER_DICT = defaultdict(dict)


def tag_reciever(message_type):

    def register_handler(func: FunctionType):
        if func.__name__ in registry:
            raise LookupError('{} already present {}'.format(
                message_type, func.__name__))
        MESSAGE_HANDLER_DICT[message_type] = func
        return func 

    return register_handler


class CommunicationManager:

    def __init__(self, config_dict):
        self.com_manager = registry.construct('communications', config_dict)
        self.com_manager.add_observer(self)
        self.message_handler_dict = dict()
        self.message_token = dict()

    def run(self):
        self.com_manager.handle_receive_message()

    async def send_message(self, message, block=False):
        # message includes reciever id and sender id
        ZeroMQ.send(message)
        if block:
            return await self.com_manager.recieve()
        else:
            return
                
    async def recieve(self):
        queue = CommunicationStream.handle_message()  
        while True:
            self.message_token = await queue.get()
            # process the token received from a producer
            await sleep(3)
            queue.task_done()
            print("Token Consumed . . ./n")
        
    def finish(self):
        self.com_manager.stop_receive_message()
