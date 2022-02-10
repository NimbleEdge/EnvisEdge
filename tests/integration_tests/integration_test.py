import sys
import collections
from abc import abstractproperty
from typing import Callable, Dict

import experiments
import fedrec
import fl_strategies
import yaml
from fedrec.data_models.job_submit_model import JobSubmitMessage
from fedrec.data_models.job_response_model import JobResponseMessage
from fedrec.python_executors.aggregator import Aggregator, Neighbour
from fedrec.python_executors.base_actor import BaseActor
from fedrec.python_executors.trainer import Trainer
from fedrec.utilities import registry
from fedrec.utilities.logger import NoOpLogger


class AbstractTester():
    def __init__(self,
                 config: Dict) -> None:
        self.config = config

        self.comm_manager = registry.construct(
            "communications",
            config=config["multiprocessing"]["communications_interfaces"])
        self.logger = NoOpLogger()

    def send_message(self, message):
        return self.comm_manager.send_message(message)

    @abstractproperty
    def worker(self) -> BaseActor:
        print("Not implimented")

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
        super().__init__(config)

    @property
    def worker(self):
        return Trainer(worker_index=0,
                       config=self.config,
                       logger=self.logger)

    def test_training_method(self):
        # create JobSubmitMessage with Job_type="train"
        response: JobResponseMessage = self.submit_message(
            senderid=self.worker.worker_index,
            receiverid=self.worker.worker_index,
            job_type="train",
            job_args=None,
            job_kwargs=None
        )
        # check response message
        if response.status:
            worker_state = response.results
            self.worker.load_worker(worker_state)
            print(f"Worker state {response.get_worker_state()}")

    def test_testing_method(self):
        response: JobResponseMessage = self.submit_message(
            senderid=self.worker.worker_index,
            receiverid=self.worker.worker_index,
            job_type="test",
            job_args=None,
            job_kwargs=None
        )
        if response.status:
            worker_state = response.results
            self.worker.load_worker(worker_state)
            print(f"Worker State {response.get_worker_state()}")


class TestAggregator(AbstractTester):
    """Test fl_startegies module methods
    """

    def __init__(self,
                 config: Dict,
                 in_neighbours: Dict[int, Neighbour] = None,
                 out_neighbours: Dict[int, Neighbour] = None):
        super().__init__(config)
        self.in_neighbours = in_neighbours
        self.out_neighbours = out_neighbours

    @property
    def worker(self):
        return Aggregator(worker_index=0, config=config,
                          logger=self.logger,
                          in_neighbours=self.in_neighbours,
                          out_neighbours=self.out_neighbours)

    def test_aggregation(self):
        response: JobResponseMessage = self.submit_message(
            senderid=self.worker.worker_index,
            receiverid=self.worker.worker_index,
            job_type="aggregate",
            job_args=None,
            job_kwargs=None
        )
        # check response message
        if response.status:
            worker_state = response.results
            self.worker.load_worker(worker_state)
            print(f"Worker State {response.get_worker_state()}")

    def test_sample_client(self,
                       round_idx,
                       client_num_per_round):
        response: JobResponseMessage = self.submit_message(
            senderid=self.worker.worker_index,
            receiverid=self.worker.worker_index,
            job_type="sample_clients",
            job_args=None,
            job_kwargs=None
        )
        if response.status:
            assert len(response.results) == client_num_per_round
            assert len(response.results) <= len(self.in_neighbours)


if __name__ == "__main__":

    with open("../../configs/dlrm_fl.yml", 'r') as cfg:
        config = yaml.load(cfg, Loader=yaml.FullLoader)

    print(config['model'])
    # start trainer
    test_trainer = TestTrainer(config=config)
    test_trainer.test_training_method()
    test_trainer.test_testing_method()
    # start aggregator
    test_aggregator = TestAggregator(config=config)
    test_aggregator.test_aggregation()
    test_aggregator.test_sample_client()


