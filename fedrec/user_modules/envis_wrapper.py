import torch
from typing import Any, Dict
from fedrec.data_models.tensors_model import EnvisTensors
from fedrec.utilities.registry import Registrable
from fedrec.serialization.serializer_registry import (deserialize_attribute,
                                                      serialize_attribute)



def create_serializer_hooks(class_ref):
    # TODO : refactor the code, make a single
    # function to call these methods.
    def type_name(cls):
        return cls.__module__ + "." + cls.__name__

    def append_type(self, obj_dict):
        """Generates a dictionary from an object and
         appends type information for finding the appropriate serialiser.

        Parameters:
        -----------
        obj: object
            The object to serialize.

        Returns:
        --------
        dict:
            The dictionary representation of the object.
        """
        return {
            "__type__": self.__class__.type_name(),
            "__data__": obj_dict,
        }

    def serialize(self):
        # TODO decide how to fill storage from config
        response_dict = {}
        response_dict["class_ref_name"] = serialize_attribute(
            self.__class__.type_name())
        response_dict["state"] = serialize_attribute(self.envis_state)
        return self.append_type(response_dict)

    def deserialize(cls, obj: Dict):
        state = deserialize_attribute(obj["state"])
        return state

    setattr(class_ref, "serialize", serialize)
    setattr(class_ref, "deserialize", classmethod(deserialize))
    setattr(class_ref, "append_type", append_type)
    setattr(class_ref, "type_name", classmethod(type_name))


def create_envis_state_hooks(class_ref):
    
    def envis_state(self: Any):
        return EnvisTensors(
                storage=self.storage,
                tensors=self.state_dict(),
                tensor_type="user-module"
            )

    def load_envis_state(self, state: Dict):
        self.load_state_dict(state.tensors)

    setattr(class_ref, "envis_state", property(envis_state))
    setattr(class_ref, "load_envis_state", load_envis_state)


def add_envis_hooks(class_ref):
    setattr(class_ref,"storage", None)
    Registrable.register_class_ref(
        class_ref, Registrable.get_name(class_ref))
    create_serializer_hooks(class_ref)
    create_envis_state_hooks(class_ref)


add_envis_hooks(torch.optim.Optimizer)
add_envis_hooks(torch.nn.Module)
add_envis_hooks(torch.nn.ModuleDict)
