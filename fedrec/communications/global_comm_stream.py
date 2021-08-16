from asyncio import queues
from typing import Dict
from communication_interfaces import ZeroMQ
from fedrec.federated_worker import FederatedWorker, WorkerDataset



class CommunicationStream:
    def __init__(self) -> None:
        self.message_stream = {} # TODO decide kafka stream or otherwise
        self.subscriber = ZeroMQ.subscriber() # NOT ClEAR how to initolize subsrciber
        self.Zmq = ZeroMQ()
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
        if self.subscriber:
            worker_list = WorkerDataset()
            while True:
                message = self.Zmq.receive_message()
                if message['receiver_id'] in worker_list:
                    worker = worker_list.get_worker('receiver_id')
                    worker.send_message(message)

    def stop(self):
        ZeroMQ.close()