from abc import ABC, abstractmethod
from fedrec.utilities import registry
from fedrec.serialization.abstract_serializer import get_serializer
import asyncio


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

        Parameters:
        -----------
        obj: object
            The message to serialize.

        Returns:
        --------
        message: str
            The serialized message.
        """
        return get_serializer(
            obj,
            self.srl_strategy
        ).serialize(obj)

    def deserialize(self, message):
        """
        Deserializes a message.

        Parameters:
        -----------
        message: str
            The message to deserialize.

        Returns:
        --------
        message: object
            The deserialized message.
        """
        return get_serializer(
            message,
            self.srl_strategy
        ).deserialize(message)
