import os
import random
from typing import Dict

from fedrec.serialization.serializable_interface import Serializable
from fedrec.utilities.io_utils import load_tensors, save_tensors
from fedrec.utilities.registry import Registrable


@Registrable.register_class_ref
class EnvisTensors(Serializable):

    def __init__(
            self,
            storage,
            tensors,
            tensor_type) -> None:
        super().__init__()
        self.storage = storage
        self.tensors = tensors
        self.tensor_type = tensor_type
        self.SUFFIX = 0

    def get_name(self) -> str:
        """
        Creates a name of the tenosr using the
            tensor_type and SUFFIX.

        Returns
        --------
        name: str
            The name of the tensor.
        """
        self.SUFFIX += 1
        return "_".join([str(self.tensor_type), str(self.SUFFIX)])

    def get_path(self):
        """
        Creates path to save tensor the storage and get name method.

        Returns
        --------
        path: str
            The path to the tensor.
        """
        return "{}/{}.pt".format(str(self.storage), str(self.get_name()))

    def get_torch_obj(self):
        return self.tensors

    @staticmethod
    def split_path(path):
        """
        Splits the path into the storage, tensor_type.

        Parameters
        -----------
        path: str
            The path to the tensor.

        Returns
        --------
        storage: int
            The storage path to the tensor.
        tensor_type: str
            The tensor type.

        """
        storage = "/".join(path.split("/")[:-1])
        name = path.split("/")[-1]
        tensor_type, suffix = name.split("_")
        return storage, tensor_type

    def serialize(self):
        """
        Serializes a tensor object.

        Parameters
        -----------
        obj: object
            The object to serialize.
        file: file
            The file to write to.

        Returns
        --------
        pkl_str: io.BytesIO
            The serialized object.

        """
        path = save_tensors(self.tensors, self.get_path())
        return self.append_type({"tensor_path": path})

    @classmethod
    def deserialize(cls, obj: Dict):
        """
        Deserializes a tensor object.

        Parameters
        -----------
        obj: object
            The object to deserialize.

        Returns
        --------
        deserialized_obj: object
            The deserialized object.
        """
        path = obj["tensor_path"]
        tensors = load_tensors(path)
        storage, tensor_type = cls.split_path(path)
        return cls(storage, tensors, tensor_type)
