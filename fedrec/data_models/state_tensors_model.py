from typing import Dict, List

from torch import Tensor

from fedrec.data_models.tensors_model import EnvisTensors
from fedrec.serialization.serializable_interface import Serializable
from fedrec.utilities.io_utils import load_proto, save_proto
from fedrec.utilities.registry import Registrable
from fedrec.envisproto.state.model_state_pb2 import State
from fedrec.envisproto.state.state_tensor_pb2 import StateTensor
from fedrec.envisproto.tensors.parameter_pb2 import Parameter
from fedrec.envisproto.commons.id_pb2 import Id


@Registrable.register_class_ref
class StateTensors(Serializable):
    def __init__(
            self,
            storage : str,
            tensors : Dict[str, Tensor],
            suffix=""):
        self.storage = storage
        self.tensors = tensors
        self.suffix = suffix
        self.envistensors = {name: EnvisTensors(
            self.storage, tensor) for name, tensor in tensors.items()}

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
            ["remove_this_1223432344232",self.suffix])

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
        storage: str

        """
        return "/".join(path.split("/")[:-1])

    # def _create_parameter(self, name: str, tensor: EnvisTensors):
    #     tensor._create_tensor
    #     parameter = Parameter()
    #     id = Id()
    #     id.id_str = name
    #     parameter.id.CopyFrom(id)
    #     parameter.tensor.CopyFrom(tensor.get_proto_object())
    #     return parameter

    def _create_state_tensor(self, name: str, tensor: EnvisTensors):
        state = StateTensor()
        state.torch_tensor.CopyFrom(tensor.get_proto_object())
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
        StateTensor: StateTensor
            The deserialized object.
        """
        path = obj['storage']
        # load tensor from the path
        state = State()
        load_proto(path, state)

        storage = "/".join(path.split("/")[:-1])

        tensors = {
            state_tensor.torch_tensor.id.id_str: EnvisTensors.from_proto_object(storage, state_tensor.torch_tensor) for state_tensor in state.tensors
        }

        return StateTensors(
            storage, tensors
        )
