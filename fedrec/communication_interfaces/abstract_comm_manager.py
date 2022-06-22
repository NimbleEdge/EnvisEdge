import ast
import asyncio
from abc import ABC, abstractmethod

from fedrec.serialization.serializable_interface import Serializable
from fedrec.serialization.serializer_registry import (deserialize_attribute,
                                                      serialize_attribute)
from fedrec.utilities import registry


class AbstractCommunicationManager(ABC):
    """
    This class works effectively on commuting messages between workers and job executors , and also performs different message operations like sending, receiving,serializing and deserializing.

    Serialization is the process of converting a data object into a format that can be reused later. It helps in reconstructing the object later and helps in obtaining the exact structure/object which makes it easy to use instead of reconstructing the object from scratch.

    Deserialization is the reverse process of serialization. It reconstructs the data object from a set of formats.

    """
    def __init__(self, srl_strategy):
        self.queue = asyncio.Queue()
        self.srl_strategy = registry.construct(
            "serialization",
            srl_strategy
        )

    @abstractmethod
    def send_message(self, message):
        raise NotImplementedError('communication interface not defined')

    @abstractmethod
    def receive_message(self):
        raise NotImplementedError('communication interface not defined')

    @abstractmethod
    def finish(self):
        pass

    def serialize(self, obj):
        """
        Serializes a message.

        Parameters
        -----------
        obj: object
            The message to serialize.

        Returns
        --------
        message: str
            The serialized message.
        """
        out = str(serialize_attribute(obj)).encode('utf-8')
        return out

    def deserialize(self, message):
        """
        Deserializes a message.

        Parameters
        -----------
        message: str
            The message to deserialize.

        Returns
        --------
        message: object
            The deserialized message.
        """
        message = ast.literal_eval(message.decode('utf-8'))
        return deserialize_attribute(message)
