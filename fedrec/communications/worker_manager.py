import logging
import json
import asyncio
from federated_worker import FederatedWorker
from fedrec.communications.worker_manager import WorkerComManager
from fedrec.communications.comm_manager import (CommunicationManager,
                                               tag_reciever)
from fedrec.utilities.serialization import serialize_object
from fedrec.communications.messages import ProcMessage, JobSubmitMessage, ModelRequestMessage

class WorkerComManager(CommunicationManager):
    def __init__(self, trainer, worker_id, config_dict):
        super().__init__(config_dict=config_dict)
        self.trainer = trainer
        self.round_idx = 0
        self.id = worker_id
        self.receiverid = ''
        self.queue = asyncio.Queue()


    def run(self):
        super().run()

    # TODO should come from topology manager

    def receive_message(self, message):
        self.receiverid = message.get_sender_id()

    def send_model(self, weights, local_sample_num):
        message = JobSubmitMessage(self.id, self.receiverid)
        message.add_modelweights(weights)
        message.aadd_local_sample_num(local_sample_num)
        self.send_message(message)

    async def send_job(self, receive_id, job_type):
        if job_type == 'train':
            message = JobSubmitMessage(job_type, self.id, receive_id, json.dumps(FederatedWorker.serialise()))
            to_block = True
        elif job_type == 'test':
            message = JobSubmitMessage(job_type, self.id, receive_id, json.dumps(FederatedWorker.serialise()))
            to_block = False
        else:
            raise ValueError(f"Invalid job type: {job_type}")

        logging.info(f"Submitting job to global process manager of type: {job_type}")
        return await self.send_message(message, block=to_block)
    
    def request_model(self, receive_id):
        message = ModelRequestMessage(self.id, receive_id)
        self.send_message(message)
