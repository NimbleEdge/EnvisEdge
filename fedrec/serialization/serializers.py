"""
Defines custom serializers and deserializers for different objects
"""

import pickle
from abc import ABC, abstractmethod
from fedrec.utilities.serialization import load_tensor, save_tensor
from fedrec.utilities.saver_utilities import download_s3_file, is_s3_file

SERIALIZER_REGISTRY = {}

#TODO: For objects if the serialization takes a substantial amount of data 
# store it in a pkl file and upload it to the cloud, and while deserializing 
# it download at deserialize, so as to not put stress on kafka events handlers.


class AbstractSerializerDeserializer(ABC):
    def __init__(self, obj):
        self.obj = obj

    @abstractmethod
    def serialize(self, file=None):
        pkl_str = io.BytesIO()
        with open(file, "wb"):
            pickle.dump(pkl_str, file)
        if file and len(list(pkl_str) > threshold:
            # The pkl string is too long to pass to the kafka message queue, write the string to the file and upload 
            # it to the cloud.
            with open(file, "wb") as fd:
                fd.write(pkl_str.read())
            return file
        return pkl_str


    @abstractmethod
    def deserializer(self):
        # Override this method for custom implementation for a class.
        pkl_str = io.BytesIO(obj)
        with open(file, "wb") as fd:
            deserialized_obj = pickle.load(pkl_str)
        return deserialized_obj



class SerializeDeserializeTensor(AbstractSerializerDeserializer):
    def __init__(self, obj):
        # Obj to serialize or deserialize.
        self.obj = obj

    def serialize(self, file=None):
        if file:
            # if file is provided, save the tesor to the file and return the file path.
            save_tensor(obj, file)
            return file
        else:
            # create a buffer Bytes object, which can be used to write to the file.
            buffer = io.BytesIO()
            save_tensor(self.obj, buffer)
            return buffer

    def deserialize(self):
        data_file = None
        if is_s3_file(self.obj):
            # This is most likely to be a link of s3 storage.
            # Copy the file locally and then deserialize it.
            data_file = download_s3_file(self.obj)
        if isinstance(self.obj, io.BytesIO):
            data_file = self.obj

        try:
            # This should be the path to the tensor object.
            tensor = load_tensor(self.obj, device=None)
        except Exception as e:
            raise ValueError("the filename specified to load the tensor from could not be accessed,Please make sure the path has correct permissions")
        else:
            return tensor

# Update the registry        
SERIALIZER_REGISTRY[torch.tensor] = SerializerDeserializerTensor


