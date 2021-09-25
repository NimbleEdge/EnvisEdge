from asyncio import queues
from typing import Dict
from fedrec.utilities import registry
from fedrec.federated_worker import WorkerDataset

class CommunicationStream:
    def __init__(self, config_dict):
        self.message_stream = {} # TODO decide kafka stream or otherwise
        self.subscriber = registry.construct("communications", config_dict["communications"], is_subscriber=True)
        self.message_routing_dict = dict()
        self.worker_list = WorkerDataset()

    def subscribe(self):
        self.message_stream.subscribe()
    
    def notifiy_subscribers(self):
        self.observers.notify()

    def publish(self):
        self.message_stream.publish()

    def get_global_hash_map(self):
        return self.message_routing_dict

    async def handle_message(self):
        if self.subscriber:
            while True:
                message = await self.subscriber.recieve_message()
                if message.get_receiver_id() in self.worker_list:
                    worker = self.worker_list.get_worker(message.get_receiver_id())
                    worker.add_to_message_queue(message)

    def stop(self):
        self.subscriber.close()