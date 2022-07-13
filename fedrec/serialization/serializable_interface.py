from abc import ABC, abstractmethod
from fedrec.utilities.registry import Registrable

PRIMITIVES_TYPES = (str, int, float, bool)


def is_primitives(obj):
    if obj is None:
        return True
    else:
        return isinstance(obj, PRIMITIVES_TYPES)


class Serializable(Registrable, ABC):
    """
    Serializable is the abstract base class for all the data
    formats that needs to be serialized and deserialized.
    In simple terms, the serializable is converting a
    data object (e.g., Python objects, Tensorflow models)
    into a format that can be stored or transmitted, and
    then recreated using the reverse process of
    deserialization when needed.
    The serialize and deserialize functions first check for the
    base class property i.e whether it is a serializable class or
    not. If they are child classes of serializable then the further
    process is continued.

    Attributes
    -----------
    serializer: str
        The serializer to use.

    Methods
    --------
    serialize(obj):
        Serializes an object.
    deserialize(obj):
        Deserializes an object.
    """

    def __init__(self) -> None:
        super().__init__()

    @abstractmethod
    def serialize(self):
        raise NotImplementedError()

    @abstractmethod
    def deserialize(self):
        raise NotImplementedError()

    def append_type(self, obj_dict):
        """Generates a dictionary from an object and
         appends type information for finding the appropriate serialiser.

        Parameters
        -----------
        obj: object
            The object to serialize.

        Returns
        --------
        dict:
            The dictionary representation of the object.
        """
        return {
            "__type__": self.type_name(),
            "__data__": obj_dict,
        }
