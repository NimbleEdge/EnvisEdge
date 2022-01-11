import pytest
import json
from fedrec.serialization.serializers import AbstractSerializer, JSONSerializer
from fedrec.communications.messages import JobSubmitMessage, JobResponseMessage

response_message_test = JobResponseMessage("test", "00", "00")
response_message_train = JobResponseMessage("train", "01", "01")
submit_message_test = JobSubmitMessage("test", "00", "00", "00", "00", "00")
submit_message_train = JobSubmitMessage("train", "01", "01", "01", "01", "01")


@pytest.mark.parametrize(
    "obj, type, data",
    [(response_message_test,
     response_message_test.__type__, response_message_test.__dict__),
     (response_message_train,
      response_message_train.__type__, response_message_train.__dict__),
     (submit_message_test,
      submit_message_test.__type__, submit_message_test.__dict__),
     (submit_message_train,
      submit_message_train.__type__, submit_message_train.__dict__)]
)
def test_json_serialize(obj, type, data):
    ans = JSONSerializer.serialize(obj)
    ans = json.loads(ans)
    assert ans['__type__'] == type
    assert ans['__data__'] == data


@pytest.mark.parametrize(
    "message_dict, type, data",
    [(response_message_test,
     response_message_test.__type__, response_message_test.__dict__),
     (response_message_train,
      response_message_train.__type__, response_message_train.__dict__),
     (submit_message_test,
      submit_message_test.__type__, submit_message_test.__dict__),
     (submit_message_train,
      submit_message_train.__type__, submit_message_train.__dict__)]
)
def test_json_deserialize(message_dict, type, data):
    obj = JSONSerializer.serialize(message_dict)
    ans = JSONSerializer.deserialize(obj)
    assert ans.__type__ == type
    assert ans.__dict__ == data
