from typing import Dict
import torch

from fedrec.serialization.serializable_interface import Serializable
from fedrec.utilities.io_utils import load_tensors, save_tensors, save_proto, load_proto
from fedrec.utilities.registry import Registrable
from fedrec.envisproto.state.model_state_pb2 import State
from fedrec.envisproto.state.state_tensor_pb2 import StateTensor
from fedrec.envisproto.tensors.parameter_pb2 import Parameter
from fedrec.envisproto.tensors.tensor_data_pb2 import TensorData
from fedrec.envisproto.tensors.torch_tensor_pb2 import TorchTensor
from fedrec.envisproto.execution.plan_pb2 import Plan
from fedrec.envisproto.commons.id_pb2 import Id


@Registrable.register_class_ref
class EnvisTensors(Serializable):

    def __init__(
            self,
            storage,
            tensor : torch.Tensor) -> None:
        super().__init__()
        self.storage = storage
        self.tensor = tensor
        self.tensor_type = tensor.dtype.__repr__()
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

    @classmethod
    def from_proto_object(cls, storage, proto_object):
        """
        Creates a EnvisTensors object from a proto object.

        Parameters
        -----------
        storage: str
            The storage path to the tensor.
        proto_object: object
            The proto object.

        Returns
        --------
        tensor: EnvisTensors
            The EnvisTensors object.

        """
        return EnvisTensors(storage, cls._from_tensor_data(proto_object.contents_data))

    @classmethod
    def _from_tensor_data(cls, tensor_data: TensorData):
        return torch.tensor(tensor_data.contents_float64, dtype=tensor_data.dtype).reshape(tensor_data.shape.dims)

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
        EnvisTensors: EnvisTensors
            The deserialized object.
        """
        path = obj["tensor_path"]
        tensor = TorchTensor()
        load_proto(path, tensor)

        storage = "/".join(path.split("/")[:-1])

        return cls(storage, cls.from_proto_object(storage, tensor))
