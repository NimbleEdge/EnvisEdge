import pytest
import json
import yaml
from fedrec.serialization.serializers import AbstractSerializer, JSONSerializer
from fedrec.communications.messages import JobSubmitMessage, JobResponseMessage

with open("test_config.yml", 'r') as cfg:
    config = yaml.load(cfg, Loader=yaml.FullLoader)

def pytest_generate_tests(metafunc):
    fct_name = metafunc.function.__name__
    if fct_name in config:
        params = config[fct_name]
        metafunc.parametrize(params["params"], params["values"])


def test_generate_message_dict(job_type, job_args, job_kwargs,
                               senderid, receiverid, workerstate):
    """test generate_message_dict method
    """
    obj = JobSubmitMessage(job_type, job_args, job_kwargs,
                           senderid, receiverid, workerstate)
    dict = AbstractSerializer.generate_message_dict(obj)
    assert dict['__type__'] == obj.__type__
    assert dict['__data__'] == obj.__dict__


def test_JSON_JobResponseMessage_serialize(job_type, senderid, receiverid):
    """test JSOMSerializer method
    """
    message_dict_response = JobResponseMessage(job_type, senderid, receiverid)
    serilized_response_msg = JSONSerializer.serialize(message_dict_response)
    response_msg = json.loads(serilized_response_msg)
    assert response_msg['__type__'] == message_dict_response.__type__
    assert response_msg['__data__'] == message_dict_response.__dict__

def test_JSON_jobSubmitMessage_serialize(job_type, job_args,
                                           job_kwargs, senderid,
                                           receiverid, workerstate):
    message_dict_submit = JobSubmitMessage(job_type, job_args,
                                           job_kwargs, senderid,
                                           receiverid, workerstate)
    serilized_submit_msg = JSONSerializer.serialize(message_dict_submit)
    response_submit_msg = json.loads(serilized_submit_msg)
    assert response_submit_msg['__type__'] == message_dict_submit.__type__
    assert response_submit_msg['__data__'] == message_dict_submit.__dict__


def test_JSON_JobSubmitMessage_deserialize(job_type, job_args, job_kwargs,
                                      senderid, receiverid, workerstate):
    """test JSOMdeserialize method
    """
    message = JobSubmitMessage(job_type, job_args,
                               job_kwargs, senderid,
                               receiverid, workerstate)
    serilized_msg = JSONSerializer.serialize(message)
    response__msg = JSONSerializer.deserialize(serilized_msg)
    assert response__msg == message


def test_JSON_JobResponseMessage_deserialize(job_type,
                                        senderid, receiverid):
    """test JSOMdeserialize method
    """
    message = JobResponseMessage(job_type, senderid, receiverid)
    serilized_msg = JSONSerializer.serialize(message)
    response__msg = JSONSerializer.deserialize(serilized_msg)
    assert response__msg == message
