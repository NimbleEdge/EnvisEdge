from typing import Dict
import torch

from fedrec.data_models.tensors_model import EnvisTensors
from fedrec.serialization.serializable_interface import Serializable
from fedrec.utilities.io_utils import load_proto, load_tensors, save_tensors, load_proto
from fedrec.utilities.registry import Registrable
from envisproto.state.model_state_pb2 import State
from envisproto.state.state_tensor_pb2 import StateTensor
from envisproto.tensors.parameter_pb2 import Parameter
from envisproto.tensors.tensor_data_pb2 import TensorData
from envisproto.tensors.torch_tensor_pb2 import TorchTensor
from envisproto.commons.id_pb2 import Id


@Registrable.register_class_ref
class StateTensors(Serializable):
    def __init__(
            self,
            storage,
            worker_id,
            round_idx,
            tensors,
            tensor_type,
            suffix=""):
        self.worker_id = worker_id
        self.round_idx = round_idx
        self.storage = storage
        self.tensors = tensors
        self.tensor_type = tensor_type
        self.suffix = suffix
        self.envistensors = {name: EnvisTensors(
            self.storage, tensor, self.tensor_type) for name, tensor in tensors.items()}

    def get_name(self) -> str:
        """
        Creates a name for the tensor using the
            worker_id, round_idx, and tensor_type.

        Returns
        --------
        name: str
            The name of the tensor.
        """
        return "_".join(
            [str(self.worker_id),
             str(self.round_idx),
             self.tensor_type])

    @staticmethod
    def split_path(path):
        """
        Splits the path into the worker id, round idx, and tensor type.

        Parameters
        -----------
        path: str
            The path to the tensor.

        Returns
        --------
        worker_id: int
            The worker id.
        round_idx: int
            The round idx.
        tensor_type: str
            The tensor type.

        """
        path_split = path.split("/")
        info = path_split[-1].split("_")
        worker_id = int(info[0])
        round_idx = int(info[1])
        tensor_type = info[2]
        return worker_id, round_idx, tensor_type

    def _create_parameter(self, name: str, tensor: EnvisTensors):
        parameter = Parameter()
        id = Id()
        id.id_str = name
        parameter.id.CopyFrom(id)
        parameter.tensor.CopyFrom(tensor.get_proto_object())
        return parameter

    def _create_state_tensor(self, name: str, tensor: EnvisTensors):
        state = StateTensor()
        state.torch_param.CopyFrom(self._create_parameter(name, tensor))
        return state

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
        state = State()
        state.tensors.extend([self._create_state_tensor(name, tensor)
                              for name, tensor in self.envistensors.items()])

        # TODO : add logic to save the state to a file.
        proto_path = save_proto(self.storage, self.get_name(), state)
        return self.append_type({
            "storage": proto_path
        })

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
        path = obj['storage']
        # load tensor from the path
        tensors = TorchTensor()
        tensors = load_proto(path, tensors)
        worker_id, round_idx, tensor_type = cls.split_path(path)
        return StateTensors(
            path, worker_id, round_idx, tensors, tensor_type
        )
