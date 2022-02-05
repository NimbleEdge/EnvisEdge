import os
import pickle

from fedrec.utilities import registry
from fedrec.utilities.serialization import load_tensor, save_tensor
from fedrec.serialization.abstract_serializer import AbstractSerializer
from fedrec.data_models.messages import JobResponseMessage, JobSubmitMessage

DELIMITER = "$"*30


@registry.load("serializer", "JobSubmitMessageSerializer")
class JobSubmitMessageSerializer(AbstractSerializer):
    """
    This dumps the data into pkl format, if the file
    is specified the workerstate data is pickled
    into the specified file, as workerstate might be
    large.
    The deserializer handles both the longer pkl
    string as well as the pkl dumped into the
    file format.
    """
    @classmethod
    def serialize(cls, obj, file=None):
        assert type(obj) is JobSubmitMessage
        # JobSubmitMessage needs to be serialized
        # before getting sent to the Kafka
        # queue.
        if file:
            worker_state = obj.workerstate
            obj.workerstate = None
            pkl_string = pickle.dumps(obj)
            pkl_string_workerstate = pickle.dumps(worker_state)
            # if file is provided dump the workerstate to the file.
            with open(file, "wb") as fd:
                fd.write(pkl_string_workerstate)
            return pkl_string + (DELIMITER + str(file)).encode()
        else:
            # No file provided, simply return the pickle string
            return pickle.dumps(obj)

    @classmethod
    def deserialize(cls, obj):
        if DELIMITER.encode() in obj:
            pkl_string, file = obj.split(DELIMITER.encode())
            file = file.decode()
            assert os.path.exists(file)
            with open(file, "rb") as fd:
                pkl_string_workerstate = fd.read()
            workerstate = pickle.loads(pkl_string_workerstate)
            message = pickle.loads(pkl_string)
            assert isinstance(message, JobSubmitMessage)
            message.workerstate = workerstate
        else:
            message = pickle.loads(obj)
            assert isinstance(message, JobSubmitMessage)
        return message
