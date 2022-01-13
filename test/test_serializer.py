import pytest
import json
from fedrec.serialization.serializers import AbstractSerializer, JSONSerializer
from fedrec.communications.messages import JobSubmitMessage, JobResponseMessage

response_message_test = JobResponseMessage("test", "00", "00")
response_message_train = JobResponseMessage("train", "01", "01")
submit_message_test = JobSubmitMessage("test", "00", "00", "00", "00", "00")
submit_message_train = JobSubmitMessage("train", "01", "01", "01", "01", "01")

# test class for generate message dict method


class test_dict:
    __type__ = "test"

    def __init__(self, name, id, number) -> None:
        self.name = name
        self.id = id
        self.number = number

# test generate_message_dict method


@pytest.mark.parametrize(
    "obj",
    [test_dict("test", "00", "00"),
     test_dict("train", "01", "01")]
)
def test_generate_message_dict(obj):
    dict = AbstractSerializer.generate_message_dict(obj)
    assert dict['__type__'] == obj.__type__
    assert dict['__data__'] == obj.__dict__


# test JSOMSerializer method
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

# test JSOMdeserialize method


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
