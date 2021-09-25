
from fedrec.communications.messages import JobSubmission, ProcMessage, send_model
import logging
import json

from federated_worker import FederatedWorker
from fedrec.communications.worker_manager import WorkerComManager
from fedrec.communications.comm_manager import (CommunicationManager,
                                               tag_reciever)
from fedrec.utilities.serialization import serialize_object
from fedrec.communications.messages import test_JobSubmission, train_JobSubmission, get_model, send_model, 

class WorkerComManager(CommunicationManager):
    def __init__(self, trainer, worker_id, config_dict):
        super().__init__(config_dict=config_dict)
        self.trainer = trainer
        self.round_idx = 0
        self.id = worker_id
        self.recieverid = ''
        self.fl_com_manager = WorkerComManager(
            trainer=base_trainer, id=worker_index, config_dict=com_dict)

    def run(self):
        super().run()

    # TODO should come from topology manager

    def receive_message(self, message):
        self.recieverid = message.get_sender_id()

    def send_model(self, weights, local_sample_num):
        message = send_model(self.id, self.recieverid, weights,  local_sample_num)
        self.send_message(message)

    async def send_job(self, receive_id, job_type, *args, **kwargs):
        # serialized_args = [serialize_object(i) for i in args]
        # message.add_params(MyMessage.MSG_ARG_JOB_ARGS, json.dumps(serialized_args))

        # serialized_kwargs = {key: serialize_object(val) for key, val in kwargs}
        # message.add_params(MyMessage.MSG_ARG_JOB_KWARGS, json.dumps(serialized_kwargs))

        if job_type == 'train':
            message = train_JobSubmission(self.id, receive_id, json.dumps(FederatedWorker.serialise()))
            to_block = True
        elif job_type == 'test':
            message = test_JobSubmission(self.id, receive_id, json.dumps(FederatedWorker.serialise()))
            to_block = False
        else:
            raise ValueError(f"Invalid job type: {job_type}")

        logging.info(f"Submitting job to global process manager of type: {job_type}")
        return await self.send_message(message, block=to_block)
    
    def request_model(self, receive_id):
        message = get_model(self.id, receive_id)
        self.send_message(message)

    # dumps message into the manager queue
    def add_to_message_queue(self, message):
        self.fl_com_manager.queue.put(message)
