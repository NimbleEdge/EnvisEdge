
from abc import ABC, abstractmethod
from fedrec.utilities.serialization_utils import get_serializer


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
