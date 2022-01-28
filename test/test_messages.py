import json

import pytest
import yaml
from fedrec.communications.messages import JobSubmitMessage, JobResponseMessage

from fedrec.python_executors.base_actor import ActorState

with open("test_config.yml", 'r') as cfg:
    config = yaml.load(cfg, Loader=yaml.FullLoader)


def pytest_generate_tests(metafunc):
    fct_name = metafunc.function.__name__
    if fct_name in config:
        params = config[fct_name]
        metafunc.parametrize(params["params"], params["values"])


def test_job_type(job_type, job_args , job_kwargs,senderid, receiverid, workerstate):

    obj = JobSubmitMessage(job_type, job_args, job_kwargs,
                           senderid, receiverid, workerstate)

    assert type(obj.get_job_type()) == str
    assert obj.get_job_type() == job_type

def test_jobresponse_status(job_type, senderid, receiverid):
    
    obj = JobResponseMessage(job_type, senderid, receiverid)

    assert(type(obj.status) == bool)

def test_jobsubmitmessage(job_type, job_args , job_kwargs,senderid, receiverid, workerstate):

    obj = JobSubmitMessage(job_type, job_args, job_kwargs,
                           senderid, receiverid, workerstate)

    assert obj.__type__ == obj.__class__.__name__

def test_jobresponsemessage(job_type, senderid, receiverid):

    obj = JobResponseMessage(job_type, senderid, receiverid)
                           
    assert obj.__type__ == obj.__class__.__name__
