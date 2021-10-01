from collections import defaultdict
from types import FunctionType
from communication_interfaces import ZeroMQ
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
        self.queue = asyncio.Queue()       

    def register_queue(self, receving_id):
        dic = CommunicationStream.get_global_hash_map()
        if receving_id in dic:
            raise LookupError('{} already present in hash_map'.format(receving_id))
        else:
            dic[receving_id] = self.queue
    
    def run(self):
        self.loop = asyncio.get_current_loop()
        self.loop.create_task(message_handler())

    async def send_message(self, message, block=False):
        # message includes reciever id and sender id
        self.com_manager.send(message)
        if block:
            return await self.com_manager.recieve(message.request_id)
        else:
            return

    async def recieve(self, request_id):
        loop = asyncio.get_current_loop() 
        future = loop.create_future()
        self.message_handler_dict[request_id] = future
        return await future

    def finish(self):
        self.loop.stop()
        self.com_manager.close()

    async def message_handler(self):
        while True:
            message = await self.queue.get()
            if message.get_request_id() in self.message_handler_dict:
                future = self.message_handler_dict[message.get_request_id()]
                future.set_result(message)
            else:
                raise LookupError('{} not in the message dictionary'.format(message.get_request_id()))  

    def add_to_message_queue(self, message):
        self.queue.put(message)

