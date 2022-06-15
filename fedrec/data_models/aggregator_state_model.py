from typing import Dict, List

import attr
from fedrec.data_models.base_actor_state_model import ActorState
from fedrec.data_models.state_tensors_model import StateTensors
from fedrec.serialization.serializable_interface import Serializable
from fedrec.serialization.serializer_registry import (deserialize_attribute,
                                                      serialize_attribute)
from fedrec.utilities.registry import Registrable


@Registrable.register_class_ref
class Neighbour(Serializable):
    """A class that represents a new Neighbour instance.

    Parameters
    ----------
    id : str
        Unique identifier for the worker
    model : Dict
        Model weights of the worker
    sample_num : int
        Number of datapoints in the neighbour's local dataset
    last_sync : int
        Last cycle when the models were synced
    """
    
    def __init__(
        self,
        worker_index: str,
        model_state: StateTensors,
        sample_num,
        last_sync=0
    ) -> None:
        self.worker_index = worker_index
        self.model_state = model_state
        self.sample_num = sample_num
        self.last_sync = last_sync

    @property
    def model(self):
        return self.model_state.get_torch_obj()

    def update(self, kwargs):
        for k, v in kwargs:
            if k == 'id' and v != self.id:
                return
            if hasattr(self, k):
                setattr(self, k, v)

    def serialize(self):
        response_dict = {}
        response_dict["worker_index"] = self.worker_index
        response_dict["last_sync"] = self.last_sync
        response_dict["model_state"] = serialize_attribute(self.model_state)
        response_dict["sample_num"] = self.sample_num
        return self.append_type(response_dict)

    @classmethod
    def deserialize(cls, obj: Dict):
        worker_index = obj["worker_index"]
        last_sync = obj["last_sync"]
        model_state = deserialize_attribute(obj["model_state"])
        sample_num = obj["sample_num"]

        return cls(
            worker_index=worker_index,
            last_sync=last_sync,
            model_state=model_state,
            sample_num=sample_num,
        )

@Registrable.register_class_ref
@attr.s(kw_only=True)
class AggregatorState(ActorState):
    """Construct a AggregatorState object to reinstatiate a worker when needed.

    Attributes
    ----------
    id : str
        Unique worker identifier
    round_idx : int
        The number of local training cycles finished
    state_dict : dict
        A dictionary of state dicts storing model weights and optimizer dicts
    storage : str
        The address for persistent storage
    neighbours :
        {"in_neigh" : List[`Neighbour`], "out_neigh" : List[`Neighbour`]]
        The states of in_neighbours and out_neighbours of the
        worker when last synced
    """

    in_neighbours=attr.ib()
    out_neighbours=attr.ib(factory=dict)

    def serialize(self):
        # pack the arguments from the objects to response dict
        response_dict = {}
        response_dict["worker_index"] = self.worker_index
        response_dict["round_idx"] = self.round_idx
        response_dict["state_dict"] = serialize_attribute(
            self.state_dict)
        response_dict["storage"] = self.storage
        response_dict["in_neighbours"] = serialize_attribute(
            self.in_neighbours)
        response_dict["out_neighbours"] = serialize_attribute(
            self.out_neighbours)
        return self.append_type(response_dict)

    @classmethod
    def deserialize(cls, obj: Dict):
        # unpack the response dict to create the object
        state_dict = deserialize_attribute(
            obj['state_dict'])
        in_neighbours = deserialize_attribute(
            obj['in_neighbours'])
        out_neighbours = deserialize_attribute(
            obj['out_neighbours'])

        return cls(
            worker_index=obj['worker_index'],
            round_idx=obj['round_idx'],
            state_dict=state_dict,
            storage=obj['storage'],
            in_neighbours=in_neighbours,
            out_neighbours=out_neighbours
        )
