import io

import torch
from fedrec.utilities import registry
from fedrec.serialization.abstract_serializer import AbstractSerializer
from fedrec.utilities.serialization import load_tensor, save_tensor
from fedrec.data_models import job_response_model, job_submit_model


@registry.load("serializer", torch.Tensor.__name__)
class TensorSerializer(AbstractSerializer):
    """
    TensorSerializer serializes and deserializes torch tensors.

    Attributes:
    ----------
    serializer: str
        The serializer to use.
    """

    @classmethod
    def serialize(cls, obj, file=None):
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
        if file:
            # if file is provided, save the tensor
            # to the file and return the file path.
            save_tensor(obj, file)
            return file
        else:
            # create a buffer Bytes object,
            # which can be used to write to the file.
            buffer = io.BytesIO()
            save_tensor(obj, buffer)
            return buffer

    @classmethod
    def deserialize(cls, obj):
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
        data_file = None
        if is_s3_file(obj):
            # This is most likely to be a link of s3 storage.
            # Copy the file locally and then deserialize it.
            data_file = download_s3_file(obj)
        if isinstance(obj, io.BytesIO):
            data_file = obj

        try:
            # This should be the path to the tensor object.
            tensor = load_tensor(obj, device=None)
        except Exception as e:
            raise ValueError(
                "the filename specified to load the tensor from"
                + "could not be accessed,Please make sure the"
                + "path has correct permissions")
        else:
            return tensor
