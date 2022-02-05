from abc import ABC, abstractmethod
import asyncio

class AbstractCommunicationManager(ABC):
    def __init__(self):
        self.queue = asyncio.Queue()
    
    @abstractmethod
    def send_message(self, message):
        raise NotImplementedError('communication interface not defined')

    @abstractmethod
    def receive_message(self):
        raise NotImplementedError('communication interface not defined')

    @abstractmethod
    def finish(self):
        pass


