from collections import defaultdict
from types import FunctionType
from communication_interfaces import ZeroMQ
from fedrec.utilities import registry
from global_comm_stream import CommunicationStream
from threading import Thread
from time import sleep
import asyncio


class CommunicationManager:
    LOOP = asyncio.new_event_loop()
    THREAD = Thread(target=, daemon=True)
    def __init__(self, config_dict):
        self.com_manager = registry.construct('communications', config_dict)
        self.com_manager.add_observer(self)
        self.message_handler_dict = dict()
        self.queue = asyncio.Queue()     

    
    def submit_task(cls):
        asyncio.set_event_loop(cls.LOOP)
        cls.LOOP.create_task(self.message_handler())       

    def run(self):
        asyncio.set_event_loop(self.LOOP)
        self.LOOP.create_task(self.message_handler())


    async def send_message(self, message, block=False):
        self.com_manager.send(message)
        if block:
            return await self.com_manager.recieve()


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

