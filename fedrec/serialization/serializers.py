"""
Defines custom serializers and deserializers for different objects
"""

import os
import io
import json
import pickle
from abc import ABC, abstractmethod
from json import dumps, loads

import torch
from fedrec.utilities import registry
from fedrec.utilities.serialization import load_tensor, save_tensor


class AbstractSerializer(ABC):
    """Abstract class for serializers and deserializers.

    Attributes:
    -----------
    serializer: str
        The serializer to use.

    Methods:
    --------
    serialize(obj):
        Serializes an object.
    deserialize(obj):
        Deserializes an object.
    """

    @classmethod
    def generate_message_dict(cls, obj):
        """Generates a dictionary from an object and
         appends type information for finding the appropriate serialiser.

        Parameters:
        -----------
        obj: object
            The object to serialize.

        Returns:
        --------
        dict:
            The dictionary representation of the object.
        """
        return {
            "__type__": obj.__type__,
            "__data__": obj.__dict__,
        }

    @classmethod
    @abstractmethod
    def serialize(cls, obj, file=None):
        """
        Serializes an object.

        Parameters:
        -----------
        obj: object
            The object to serialize.
        file: file
            The file to write to.

        Returns:
        --------
        pkl_str: str
            The serialized object.
        """
        threshold = int(1e7)
        # Override this method for custom implementation for a class.
        pkl_str = io.BytesIO()
        with open(file, "wb"):
            pickle.dump(obj, pkl_str)
        # The pkl string is too long to pass
        # to the kafka message queue, write the string
        # to the file and upload it to the cloud.
        if file and len(list(pkl_str)) > threshold:
            with open(file, "wb") as fd:
                fd.write(pkl_str.read())
            return file

        return pkl_str

    @classmethod
    @abstractmethod
    def deserialize(cls, obj):
        """
        Deserializes an object.

        Parameters:
        -----------
        obj: object
            The object to deserialize.

        Returns:
        --------
        object
            The deserialized object.
        """

        # Override this method for custom implementation for a class.
        pkl_str = io.BytesIO(obj)
        with open(file, "wb") as fd:
            deserialized_obj = pickle.load(pkl_str)
        return deserialized_obj


@registry.load("serializer", torch.Tensor.__name__)
class TensorSerializer(AbstractSerializer):
    """
    TensorSerializer serializes and deserializes torch tensors.

    Attributes:
    ----------
    serializer: str
        The serializer to use.
    """

    @classmethod
    def serialize(cls, obj, file=None):
        """
        Serializes a tensor object.

        Parameters:
        -----------
        obj: object
            The object to serialize.
        file: file
            The file to write to.

        Returns:
        --------
        pkl_str: io.BytesIO
            The serialized object.

        """
        if file:
            # if file is provided, save the tensor
            # to the file and return the file path.
            save_tensor(obj, file)
            return file
        else:
            # create a buffer Bytes object,
            # which can be used to write to the file.
            buffer = io.BytesIO()
            save_tensor(obj, buffer)
            return buffer

    @classmethod
    def deserialize(cls, obj):
        """
        Deserializes a tensor object.

        Parameters:
        -----------
        obj: object
            The object to deserialize.

        Returns:
        --------
        deserialized_obj: object
            The deserialized object.
        """
        data_file = None
        if is_s3_file(obj):
            # This is most likely to be a link of s3 storage.
            # Copy the file locally and then deserialize it.
            data_file = download_s3_file(obj)
        if isinstance(obj, io.BytesIO):
            data_file = obj

        try:
            # This should be the path to the tensor object.
            tensor = load_tensor(obj, device=None)
        except Exception as e:
            raise ValueError(
                "the filename specified to load the tensor from"
                + "could not be accessed,Please make sure the"
                + "path has correct permissions")
        else:
            return tensor


@registry.load("serializer", "json")
class JSONSerializer(AbstractSerializer):
    """Uses json serialization strategy for objects.

    Attributes:
    ----------
    serializer: str
        The serializer to use.
    """

    @classmethod
    def serialize(cls, obj):
        """Serializes a python object to json.

        Parameters:
        -----------
        obj: object
            The object to serialize.
        Returns:
        --------
        str:
            The serialized object.
        """
        obj = cls.generate_message_dict(obj)
        print(obj, type(obj))
        return json.dumps(obj, indent=4).encode('utf-8')

    @classmethod
    def deserialize(cls, obj):
        """Deserializes the json object to python object
         as per the `type` mentioned in the json dictionary.

        Parameters:
        -----------
        obj: object
            The object to deserialize.

        Returns:
        --------
        deserialized_obj: object
            The deserialized object.

        """
        obj = json.loads(obj)
        print(obj, type(obj))
        return registry.construct("serializer",
                                  obj["__type__"],
                                  unused_keys=(),
                                  **obj["__data__"])


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
