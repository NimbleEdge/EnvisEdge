import time
from abc import abstractproperty
from argparse import ArgumentParser
from copy import deepcopy
from typing import Dict

import datasets
import experiments
import fedrec
import fl_strategies
import torch
import yaml
from fedrec.data_models.job_response_model import JobResponseMessage
from fedrec.data_models.job_submit_model import JobSubmitMessage
from fedrec.data_models.state_tensors_model import StateTensors
from fedrec.python_executors.aggregator import Aggregator, Neighbour
from fedrec.python_executors.base_actor import BaseActor
from fedrec.python_executors.trainer import Trainer
from fedrec.utilities import registry
from fedrec.utilities.logger import NoOpLogger


class AbstractTester():
    def __init__(self,
                 config: Dict,
                 type: str) -> None:
        self.config = deepcopy(config)
        val_1 = "multiprocessing"
        val_2 = "communication_interface"
        com_manager_config = self.config[val_1][val_2]
       # append worker infromation to dictionary

        temp = deepcopy(com_manager_config["producer_topic"])
        com_manager_config["producer_topic"] = com_manager_config[
            "consumer_topic"] + "-" + type

        com_manager_config["consumer_topic"] = temp + "-" + type

        self.comm_manager = registry.construct(
            "communication_interface",
            config=com_manager_config)
        self.logger = NoOpLogger()
        print(com_manager_config)

    def send_message(self, message):
        return self.comm_manager.send_message(message)

    def receive_message(self):
        return self.comm_manager.receive_message()

    def submit_message(self,
                       senderid,
                       receiverid,
                       job_type,
                       job_args,
                       job_kwargs) -> JobResponseMessage:
        # create JobSubmitMessage with Job_type="train"
        message = JobSubmitMessage(job_type=job_type,
                                   job_args=job_args,
                                   job_kwargs=job_kwargs,
                                   senderid=senderid,
                                   receiverid=receiverid,
                                   workerstate=self.worker.serialize())
        # send the meesgae over to kafka using producer
        self.send_message(message)
        # receive message from consumer
        return self.receive_message()


class TestTrainer(AbstractTester):
    """Test train and test methods for DLRM trainer
    """

    def __init__(self,
                 config: Dict) -> None:
        super().__init__(config, "trainer")
        self.worker = Trainer(worker_id="0",
                              config=self.config,
                              logger=NoOpLogger(),
                              client_id=2
                              )

    def test_training_method(self):
        # create JobSubmitMessage with Job_type="train"
        # response = self.submit_message(1,1,"train",[],{})
        response: JobResponseMessage = self.submit_message(
            senderid=self.worker.worker_id,
            receiverid=self.worker.worker_id,
            job_type="train",
            job_args=[],
            job_kwargs={}
        )
        # check response message
        if response.status:
            model_dict = response.results
            self.worker.load_model(model_dict)
            # print(f"Worker state {response.results}")

    def test_testing_method(self):
        response: JobResponseMessage = self.submit_message(
            senderid=self.worker.worker_id,
            receiverid=self.worker.worker_id,
            job_type="test",
            job_args=[],
            job_kwargs={}
        )
        if response.status:
            model_dict = response.results
            print(f"Worker state {response.results}")


class TestAggregator(AbstractTester):
    """Test fl_startegies module methods
    """

    def __init__(self,
                 config: Dict,
                 in_neighbours: Dict[int, Neighbour],
                 out_neighbours: Dict[int, Neighbour] = {}):
        super().__init__(config, "aggregator")
        self.in_neighbours = in_neighbours
        self.out_neighbours = out_neighbours
        self.worker = Aggregator(worker_id=0, config=config,
                                 logger=self.logger,
                                 in_neighbours=self.in_neighbours,
                                 out_neighbours=self.out_neighbours,
                                 )

    def test_aggregation(self):
        response: JobResponseMessage = self.submit_message(
            senderid=self.worker.worker_id,
            receiverid=self.worker.worker_id,
            job_type="aggregate",
            job_args=[],
            job_kwargs={}
        )
        # check response message
        if response.status:
            worker_state = response.results
            self.worker.load_worker(worker_state)
            print(f"Worker State {response.results}")

    def test_sample_client(self,
                           client_num_per_round):
        response: JobResponseMessage = self.submit_message(
            senderid=self.worker.worker_id,
            receiverid=self.worker.worker_id,
            job_type="sample_client",
            job_args=[],
            job_kwargs={}
        )
        if response.status:
            assert len(response.results) == client_num_per_round
            assert len(response.results) <= len(self.in_neighbours)


if __name__ == "__main__":

    parser = ArgumentParser()
    parser.add_argument("--config", type=str, required=True)
    parser.add_argument("--logdir", type=str, default=None)
    args = parser.parse_args()

    with open(args.config, "r") as stream:
        config = yaml.safe_load(stream)

    print("training...")
    # start trainer
    test_trainer = TestTrainer(config=config)
    test_trainer.test_training_method()
    print("testing train model...")
    test_trainer.test_testing_method()
    # start aggregator
    # TODO : HARD coded stuff need to be removed
    # ------------------------------------------------------------
    tensor = StateTensors(
        storage='/home/ramesht/dump_tensor/',
        worker_id=0, round_idx=0,
        tensors=torch.load(
            '/home/ramesht/dump_tensor/test.pt'),
        tensor_type='trainer',
        suffix="41")

    test_aggregator = TestAggregator(
        config=config,
        in_neighbours={
            0: Neighbour(0, tensor, 5)}
    )
    # ------------------------------------------------------------
    print("Test aggregation...")
    test_aggregator.test_aggregation()
    print("testing sampling...")
    test_aggregator.test_sample_client()
