from abc import ABC, abstractmethod
from json import dumps, loads

from fedrec.utilities import registry


class SerializationStrategy(registry.Registrable, ABC):
    """"
    This class is an abstract class for serialization strategies. It inherits
    from the Registrable class to allow for registration of serialization
    strategies.
    
    Methods
    --------
    parse(obj):
        Parses an object into a dictionary.
    unparse(obj):
        Unparses a dictionary into an object.
    """

    @abstractmethod
    def parse(self, obj):
        raise NotImplementedError()

    @abstractmethod
    def unparse(self, obj):
        raise NotImplementedError()


@registry.load("serialization", "json")
class JSONSerialization(SerializationStrategy):
    """
    This class is used to serialize and deserialize objects. It is used by the
    Serializable class to serialize and deserialize objects to and from json.
    
    The registry is used to register the serialization strategy with the
    Serializable class. The Serializable class uses the registry to find the
    appropriate serialization strategy for the object being serialized and
    deserialized respectively.

    Attributes
    ----------
    serializer: str
        The serializer to use.

    Methods
    --------
    parse(obj):
        Serializes an object to json.
    unparse(obj):
        Deserializes an object from json.
    """

    def parse(self, obj):
        return loads(obj)

    def unparse(self, obj):
        return dumps(obj, indent=4)
