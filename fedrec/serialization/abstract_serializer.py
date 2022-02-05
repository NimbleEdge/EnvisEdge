"""
Defines custom serializers and deserializers for different objects
"""

import os
import io
import json
import pickle
from abc import ABC, abstractmethod, abstractproperty
from json import dumps, loads
from xml.dom import NotSupportedErr

from fedrec.utilities import registry
from fedrec.utilities.serialization import load_tensor, save_tensor
from fedrec.data_models.messages import JobResponseMessage, JobSubmitMessage
from collections import defaultdict

class Serializable(object):

    @classmethod
    def type_name(cls):
        return cls.__name__


SERIALIZER_MAP = defaultdict(dict)
ACTIVE_SERIALIZERS = defaultdict(dict)

def serializable_with(serializer_name):
    
    def decorator(serialized_class):
        assert issubclass(serialized_class, Serializable), NotSupportedErr()

        SERIALIZER_MAP[serialized_class.type_name()] = serializer_name
        return serialized_class
    return decorator

def get_serializer(serialized_obj, srl_strategy):
    cls = None
    if isinstance(serialized_obj, str):
        cls = SERIALIZER_MAP[serialized_obj]
    elif isinstance(serialized_obj, Serializable):
        cls = SERIALIZER_MAP[serialized_obj.type_name()]
    else:
        raise NotSupportedErr()

    if cls not in ACTIVE_SERIALIZERS:
        ACTIVE_SERIALIZERS[cls] = cls(srl_strategy)
    
    ACTIVE_SERIALIZERS[cls].serialization_strategy = srl_strategy
    return ACTIVE_SERIALIZERS[cls]

class SerializationStrategy(ABC):

    @abstractmethod
    def parse(self, obj):
        raise NotImplementedError()

    @abstractmethod
    def unparse(self, obj):
        raise NotImplementedError()


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

    def __init__(self, serialization_strategy) -> None:
        super().__init__()
        self.serialization_strategy = serialization_strategy

    def get_class_serializer(self, obj):
        return get_serializer(obj, self.serialization_strategy)

    def serialize_attribute(self, obj):
        serializer = self.get_class_serializer(obj)
        return serializer.serialize(obj)

    def deserialize_atttribute(self, obj):
        deserializer = self.get_class_serializer(obj)
        return deserializer.deserialize(obj)

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

    @abstractmethod
    def serialize(self):
        raise NotImplementedError()

    @abstractmethod
    def deserialize(self):
        raise NotImplementedError()
