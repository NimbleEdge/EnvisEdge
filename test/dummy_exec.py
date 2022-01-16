from typing import Callable, Dict
from abc import abstractproperty
import collections
import yaml
import experiments
import fedrec
import fl_strategies
from fedrec.communications.messages import JobResponseMessage, JobSubmitMessage
from fedrec.python_executors.aggregator import Aggregator, Neighbour
from fedrec.python_executors.base_actor import BaseActor
from fedrec.python_executors.trainer import Trainer
from fedrec.utilities import registry
from fedrec.utilities.logger import NoOpLogger
import sys
sys.path.append("/home/ramesht.shuklae/fed/RecoEdge")


class AbstractTester():
    def __init__(self,
                 config: Dict) -> None:
        self.config = config

        self.comm_manager = registry.construct(
            "communications", config=config["multiprocessing"]["communications"])
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

    def TestTraining(self):
        # create JobSubmitMessage with Job_type="train"
        response: JobResponseMessage = self.submit_message(senderid=self.worker.worker_index,
                                                           receiverid=self.worker.worker_index,
                                                           job_type="train",
                                                           job_args=None,
                                                           job_kwargs=None)
        # check response message
        if response.status:
            worker_state = response.results
            self.worker.load_worker(worker_state)
            print(f"Worker state {response.get_worker_state()}")

    def TestTesting(self):
        response: JobResponseMessage = self.submit_message(senderid=self.worker.worker_index,
                                                           receiverid=self.worker.worker_index,
                                                           job_type="test",
                                                           job_args=None,
                                                           job_kwargs=None)
        if response.status:
            worker_state = response.results
            self.worker.load_worker(worker_state)
            print(f"Worker State {response.get_worker_state()}")


class TestFedAvg(AbstractTester):
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

    def testagg(self):
        response: JobResponseMessage = self.submit_message(senderid=self.worker.worker_index,
                                                           receiverid=self.worker.worker_index,
                                                           job_type="aggregate",
                                                           job_args=None,
                                                           job_kwargs=None)
        # check response message
        if response.status:
            worker_state = response.results
            self.worker.load_worker(worker_state)
            print(f"Worker State {response.get_worker_state()}")

    def testsampclient(self,
                       round_idx,
                       client_num_per_round):
        response: JobResponseMessage = self.submit_message(senderid=self.worker.worker_index,
                                                           receiverid=self.worker.worker_index,
                                                           job_type="sample_clients",
                                                           job_args=None,
                                                           job_kwargs=None)
        if response.status:
            assert len(response.results) == client_num_per_round
            assert len(response.results) <= len(self.in_neighbours)


if __name__ == "__main__":

    with open("../configs/dlrm_fl.yml", 'r') as cfg:
        config = yaml.load(cfg, Loader=yaml.FullLoader)

    print(config['model'])
    test_trainer = TestTrainer(config=config)
    test_trainer.TestTesting()
