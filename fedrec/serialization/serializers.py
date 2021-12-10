"""
Defines custom serializers and deserializers for different objects
"""

import io
import pickle
import torch
from abc import ABC, abstractmethod
import json
from json import dumps, loads
from fedrec.utilities import registry
from fedrec.utilities.serialization import load_tensor, save_tensor



class AbstractSerializer(ABC):

    @classmethod
    def generate_message_dict(cls, obj):
        return {
            "__type__": obj.__type__,
            "__data__": obj.__dict__,
        }

    @classmethod
    @abstractmethod
    def serialize(cls, obj, file=None):
        threshold = int(1e7)
        # Override this method for custom implementation for a class.
        pkl_str = io.BytesIO()
        with open(file, "wb"):
            pickle.dump(obj, pkl_str)
        # The pkl string is too long to pass to the kafka message queue, write the string
        # to the file and upload it to the cloud.
        if file and len(list(pkl_str)) > threshold:
            with open(file, "wb") as fd:
                fd.write(pkl_str.read())
            return file

        return pkl_str

    @classmethod
    @abstractmethod
    def deserialize(cls, obj):
        # Override this method for custom implementation for a class.
        pkl_str = io.BytesIO(obj)
        with open(file, "wb") as fd:
            deserialized_obj = pickle.load(pkl_str)
        return deserialized_obj


@registry.load("serializer", torch.Tensor.__name__)
class TensorSerializer(AbstractSerializer):

    @classmethod
    def serialize(cls, obj, file=None):
        if file:
            # if file is provided, save the tensor to the file and return the file path.
            save_tensor(obj, file)
            return file
        else:
            # create a buffer Bytes object, which can be used to write to the file.
            buffer = io.BytesIO()
            save_tensor(obj, buffer)
            return buffer

    @classmethod
    def deserialize(cls, obj):
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
            raise ValueError("the filename specified to load the tensor from could not be accessed,Please make sure the path has correct permissions")
        else:
            return tensor

@registry.load("serializer", "json")
class JSONSerializer(AbstractSerializer):

    @classmethod
    def serialize(cls, obj):
        obj = cls.generate_message_dict(obj)
        print(obj, type(obj))
        return json.dumps(obj, indent=4).encode('utf-8')
    
    @classmethod
    def deserialize(cls, obj):
        obj = json.loads(obj)
        print(obj, type(obj))
        return registry.construct("serializer", obj["__type__"], unused_keys=(),**obj["__data__"])

