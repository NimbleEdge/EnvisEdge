import os
import io
import json
import pickle
from abc import ABC, abstractmethod
from json import dumps, loads

from fedrec.utilities import registry
from fedrec.data_models.messages import JobResponseMessage, JobSubmitMessage
from fedrec.serialization.abstract_serializer import SerializationStrategy


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
        return dumps(obj, indent=4).encode('utf-8')

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
        
        return loads(obj)
