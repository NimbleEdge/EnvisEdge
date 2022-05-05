import ast
import asyncio
from abc import ABC, abstractmethod

from fedrec.serialization.serializable_interface import Serializable
from fedrec.serialization.serializer_registry import (deserialize_attribute,
                                                      serialize_attribute)
from fedrec.utilities import registry


class AbstractCommunicationManager(ABC):
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
