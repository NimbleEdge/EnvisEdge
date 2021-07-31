from asyncio import queues
from typing import Dict
from communication_interfaces import ZeroMQ
from fedrec.federated_worker import FederatedWorker



class CommunicationStream:
    def __init__(self) -> None:
        self.message_stream = {} # TODO decide kafka stream or otherwise
        self.subscriber = ZeroMQ.subscriber() # NOT ClEAR how to initolize subsrciber
        self.message_routing_dict = dict()

    def subscribe(self):
        self.message_stream.subscribe()
    
    def notifiy_subscribers(self):
        self.observers.notify()

    def publish(self):
        self.message_stream.publish()

    def get_global_hash_map(self):
        return self.message_routing_dict

    def handle_message(self):
        queue = ZeroMQ.get_queue()
        return queue

    def stop(self):
        ZeroMQ.close()