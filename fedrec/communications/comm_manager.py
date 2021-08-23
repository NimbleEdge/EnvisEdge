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
        self.com_manager.handle_receive_message()

    async def send_message(self, message, block=False):
        # message includes reciever id and sender id
        self.com_manager.send(message)
        if block:
            return await self.com_manager.recieve()
        else:
            return

    async def futures_message_handler(self):
        while True:
            message = await self.queue.get()
            if message["recever_id"] not in self.message_handler_dict.keys():
                self.message_handler_dict[message["recever_id"]] = message
            self.queue.task_done()

    async def recieve(self):
        await self.futures_message_handler()
        
    def finish(self):
        self.com_manager.stop_receive_message()
