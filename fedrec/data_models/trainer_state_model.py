from typing import Dict

import attr
from fedrec.data_models.base_actor_state_model import ActorState
from fedrec.serialization.serializer_registry import (deserialize_attribute,
                                                      serialize_attribute)
from fedrec.utilities.registry import Registrable


@Registrable.register_class_ref
@attr.s(kw_only=True)
class TrainerState(ActorState):
    """Construct a workerState object to reinstatiate a worker when needed.

    Attributes
    ----------
    woker_index : str
        Unique worker identifier
    model_preproc : `Preprocessor`
        The local dataset of the worker
    round_idx : int
        The number of local training cycles finished
    state_dict : dict
        A dictionary of state dicts storing model weights and optimizer dicts
    storage : str
        The address for persistent storage
    """
    model_preproc = attr.ib()
    local_sample_number = attr.ib()
    local_training_steps = attr.ib()

    def serialize(self):
        # creates a dictionary of attributes to serialize
        response_dict = {}
        response_dict["worker_index"] = self.worker_index
        response_dict["round_idx"] = self.round_idx
        response_dict["state_dict"] = serialize_attribute(
            self.state_dict)
        response_dict["storage"] = self.storage
        response_dict["model_preproc"] = serialize_attribute(
            self.model_preproc)
        response_dict["local_sample_number"] = self.local_sample_number
        response_dict["local_training_steps"] = self.local_training_steps
        return self.append_type(response_dict)

    @classmethod
    def deserialize(cls, obj: Dict):
        # Takes in dictionary of attributes and returns a new object.
        state_dict = deserialize_attribute(
            obj['state_dict'])
        model_preproc = deserialize_attribute(
            obj['model_preproc'])

        return cls(
            worker_index=obj["worker_index"],
            round_idx=obj["round_idx"],
            state_dict=state_dict,
            storage=obj["storage"],
            model_preproc=model_preproc,
            local_sample_number=obj["local_sample_number"],
            local_training_steps=obj["local_training_steps"])
