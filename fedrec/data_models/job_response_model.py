from dataclasses import dataclass
from typing import Dict

from fedrec.data_models.messages import Message
from fedrec.serialization.serializer_registry import (deserialize_attribute,
                                                      serialize_attribute)
from fedrec.utilities.registry import Registrable


@Registrable.register_class_ref
@dataclass
class JobResponseMessage(Message):
    '''
    Creates message objects for job response message

    Attributes:
    -----------
        job_type : str
            type of job (train/test)
        senderid : str
            id of sender
        receiverid : str
            id of receiver
        results : dict
            dict of results obtained from job completion
        errors : null
    '''

    def __init__(
            self,
            job_type,
            senderid,
            receiverid,
            results={},
            errors=None
    ):
        super().__init__(senderid, receiverid)
        self.job_type: str = job_type
        self.results = results
        self.errors = errors

    @property
    def status(self):
        '''
        Check if errors is None and returns response
        message status accordingly
        '''
        if self.errors is None:
            return True
        else:
            return False

    def serialize(self):
        """
        Converts the data objects (job response message) to a dictionary
        format that allows for the storage or transmission of this data.
        (i.e in our case this data is published on kafka.)

        Returns
        -------
        `Serialized Response`
            The serialized class object to be written
            to JSON or persisted into the file.
        """
        response_dict = {}
        response_dict["job_type"] = self.job_type
        response_dict["senderid"] = self.senderid
        response_dict["receiverid"] = self.receiverid
        response_dict["results"] = serialize_attribute(
            self.results)
        return self.append_type(response_dict)

    @classmethod
    def deserialize(cls, obj: Dict):
        """
        Recreates the response message objects from data that is published
        no kafka by unpacking the values and creating a class object.

        Parameters
        ----------
        cls : tuple
            the returned output that holds the deserialized objects.
        obj : dict
            dict of the serialized objects.

        Returns
        -------
        `Deserialised Response`
            Deserialises the serialized response(dict)
            and returns it as an object(tuple).
        """
        return cls(obj["job_type"],
                   obj["senderid"],
                   obj["receiverid"],
                   deserialize_attribute(obj["results"]))
