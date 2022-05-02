from typing import Dict

from fedrec.data_models.tensors_model import EnvisTensors
from fedrec.utilities.io_utils import load_tensors, save_tensors
from fedrec.utilities.registry import Registrable


@Registrable.register_class_ref
class StateTensors(EnvisTensors):
    def __init__(
            self,
            storage,
            worker_id,
            round_idx,
            tensors,
            tensor_type,
            suffix=""):
        super().__init__(storage, tensors, tensor_type)
        self.worker_id = worker_id
        self.round_idx = round_idx
        self.suffix = suffix

    def get_name(self) -> str:
        """
        Creates a name for the tensor using the
            worker_id, round_idx, and tensor_type.

        Returns:
        --------
        name: str
            The name of the tensor.
        """
        return "_".join(
            [str(self.worker_id),
             str(self.round_idx),
             self.tensor_type])

    def get_path(self) -> str:
        """
        Creates path to save tensor the
            storage and get name method and suffix.

        Returns:
        --------
        path: str
            The path to the tensor.
        """
        return "{}/{}{}.pt".format(
            str(self.storage),
            str(self.get_name()),
            self.suffix)

    @staticmethod
    def split_path(path):
        """
        Splits the path into the worker id, round idx, and tensor type.

        Parameters:
        -----------
        path: str
            The path to the tensor.

        Returns:
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

    def serialize(self):
        """
        Serializes a tensor object.

        Parameters:
        -----------
        obj: object
            The object to serialize.
        file: file
            The file to write to.

        Returns:
        --------
        pkl_str: io.BytesIO
            The serialized object.

        """
        # if file is provided, save the tensor
        # to the file and return the file path.
        path = save_tensors(self.get_torch_obj(), self.get_path())
        return self.append_type({
            "storage": path
        })

    @classmethod
    def deserialize(cls, obj: Dict):
        """
        Deserializes a tensor object.

        Parameters:
        -----------
        obj: object
            The object to deserialize.

        Returns:
        --------
        deserialized_obj: object
            The deserialized object.
        """
        path = obj['storage']
        # load tensor from the path
        tensors = load_tensors(path)
        worker_id, round_idx, tensor_type = cls.split_path(path)
        return StateTensors(
            path, worker_id, round_idx, tensors, tensor_type
        )
