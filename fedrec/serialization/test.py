import yaml
import json
import numpy as np
from json import dumps, loads
from kafka import KafkaProducer, KafkaConsumer
from fedrec.communications.messages import JobSubmitMessage
from fedrec.utilities import registry

with open("configs/dlrm_fl.yml", 'r') as cfg:
    config = yaml.load(cfg, Loader=yaml.FullLoader)

def init_kafka(config):
    producer_url = "{}:{}".format(
        config["producer_url"], config["producer_port"])
    return KafkaProducer(
        bootstrap_servers=[producer_url])

serializer = registry.construct("serializer", "json")
# config = config["multiprocessing"]["communications"]

producer = init_kafka(config["multiprocessing"]["communications"])
producer.send('job-request-trainer', value=serializer.serialize(JobSubmitMessage("test_run",[1,2],{},"id1","id2",None)))
producer.send('job-request-aggregator', value=serializer.serialize(JobSubmitMessage("test_run",[1,2],{},"id1","id2",None)))
with open("configs/dlrm_fl.yml", 'r') as cfg:
    config = yaml.load(cfg, Loader=yaml.FullLoader)

ag_config = {
        # Seed for RNG used in shuffling the training data.
    "data_seed" : 100,
    # Seed for RNG used in initializing the model.
    "init_seed" : 100,
    # Seed for RNG used in computing the model's training loss.
    # Only relevant with internal randomness in the model, e.g. with dropout.
    "model_seed" : 100}
from fedrec.python_executors.aggregator import Aggregator
from fedrec.utilities.logger import NoOpLogger
import experiments
import fl_strategies

agg = Aggregator(0, config, NoOpLogger())
st = agg.serialize()
message = JobSubmitMessage("test_run",[1,2],{},"id1","id2",st)
from fedrec.serialization.serializers import JobSubmitMessageSerializer
pst1 = JobSubmitMessageSerializer.serialize(message)
pst2 = JobSubmitMessageSerializer.serialize(message, file="/tmp/ser_des_test.pkl")
m1 = JobSubmitMessageSerializer.deserialize(pst1)
m2 = JobSubmitMessageSerializer.deserialize(pst2)
assert len(pst1) > len(pst2) # Since the file has the pkl representation of the workerstate.
assert isinstacnce(m1, JobSubmitMessage)
assert isinstace(m2, JobSubmitMessage)
assert m1.workerstate.__dict__['model']
m2_weight = np.array(m2.workerstate.state_dict["model"]["emb_l.0.weight"])
m1_weight = np.array(m1.workerstate.state_dict["model"]["emb_l.0.weight"])
assert np.all(m2_weight = m1_weight)
