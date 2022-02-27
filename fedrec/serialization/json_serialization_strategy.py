from json import dumps, loads

from fedrec.serialization.abstract_serializer import SerializationStrategy
from fedrec.utilities import registry


@registry.load("serialization", "json")
class JSONSerialization(SerializationStrategy):
    """Uses json serialization strategy for objects.

    Attributes:
    ----------
    serializer: str
        The serializer to use.
    """

    def parse(self, obj):
        """Serializes a python object to json.

        Parameters:
        -----------
        obj: object
            The object to serialize.
        Returns:
        --------
        str
        """
        return loads(obj)


    def unparse(self, obj):
        """Deserializes the json object to python object
         as per the `type` mentioned in the json dictionary.

        Parameters:
        -----------
        obj: object
            The object to deserialize.
        Returns:
        --------
        object
        """
        return dumps(obj, indent=4)