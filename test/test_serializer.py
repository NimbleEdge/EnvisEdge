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


def test_json_serialize(job_type, job_args, job_kwargs,
                        senderid, receiverid, workerstate):
    """test JSOMSerializer method
    """
    message_dict_submit = JobSubmitMessage(job_type, job_args,
                                           job_kwargs, senderid,
                                           receiverid, workerstate)
    message_dict_response = JobResponseMessage(job_type, senderid, receiverid)
    serilized_submit_msg = JSONSerializer.serialize(message_dict_submit)
    serilized_response_msg = JSONSerializer.serialize(message_dict_response)
    response_submit_msg = json.loads(serilized_submit_msg)
    response_response_msg = json.loads(serilized_response_msg)
    assert response_submit_msg['__type__'] == message_dict_submit.__type__
    assert response_submit_msg['__data__'] == message_dict_submit.__dict__
    assert response_response_msg['__type__'] == message_dict_response.__type__
    assert response_response_msg['__data__'] == message_dict_response.__dict__


def test_json_deserialize(job_type, job_args, job_kwargs,
                          senderid, receiverid, workerstate):
    """test JSOMdeserialize method
    """
    message_dict_submit = JobSubmitMessage(job_type, job_args,
                                           job_kwargs, senderid,
                                           receiverid, workerstate)
    message_dict_response = JobResponseMessage(job_type, senderid, receiverid)
    submit_msg_serialize = JSONSerializer.serialize(message_dict_submit)
    reponse_msg_serialize = JSONSerializer.serialize(message_dict_response)
    response_deserialize_msg = JSONSerializer.deserialize(submit_msg_serialize)
    submit_deserialize_msg = JSONSerializer.deserialize(reponse_msg_serialize)
    assert response_deserialize_msg.__type__ == message_dict_submit.__type__
    assert response_deserialize_msg.__dict__ == message_dict_submit.__dict__
    assert submit_deserialize_msg.__type__ == message_dict_response.__type__
    assert submit_deserialize_msg.__dict__ == message_dict_response.__dict__
