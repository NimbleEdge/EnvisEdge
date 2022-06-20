import os
import random
from typing import Dict
import torch

from fedrec.serialization.serializable_interface import Serializable
from fedrec.utilities.io_utils import load_tensors, save_tensors, save_proto, load_proto
from fedrec.utilities.registry import Registrable
from envisproto.state.model_state_pb2 import State
from envisproto.state.state_tensor_pb2 import StateTensor
from envisproto.tensors.parameter_pb2 import Parameter
from envisproto.tensors.tensor_data_pb2 import TensorData
from envisproto.tensors.torch_tensor_pb2 import TorchTensor
from envisproto.execution.plan_pb2 import Plan
from envisproto.commons.id_pb2 import Id


@Registrable.register_class_ref
class EnvisTensors(Serializable):

    def __init__(
            self,
            storage,
            tensor,
            tensor_type) -> None:
        super().__init__()
        self.storage = storage
        self.tensor = tensor
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

    def _create_tensor_data(self, tensor: torch.Tensor):
        tensor_data = TensorData()
        tensor_data.dtype = tensor.dtype.__repr__()
        tensor_data.shape.dims.extend(tensor.shape)
        tensor_data.contents_float64.extend(tensor.view(-1).tolist())
        return tensor_data

    def _create_tensor(self, name: str, tensor: torch.Tensor):
        t_tensor = TorchTensor()
        id = Id()
        id.id_str = name
        t_tensor.id.CopyFrom(id)
        t_tensor.contents_data.CopyFrom(self._create_tensor_data(tensor))
        return t_tensor

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
        # tensor_type, suffix = name.split("_")
        return storage, name

    def get_proto_object(self):
        """
        Returns the proto object.

        Returns
        --------
        proto_object: object
            The proto object.

        """
        return self._create_tensor(self.get_name(), self.tensor)

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
        # TODO: add saving function for proto file
        proto_path = save_proto(self.storage, self.get_name(), self._create_tensor(self.get_name(), self.tensor))
        return self.append_type({"tensor_path": proto_path})

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
        tensors = TorchTensor()
        tensors = load_proto(path, tensors)
        storage, tensor_type = cls.split_path(path)
        return cls(storage, tensors, tensor_type)
