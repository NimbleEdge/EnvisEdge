from typing import Dict

from fedrec.serialization.abstract_serializer import AbstractSerializer
from fedrec.data_models.aggregator_state_model import AggregatorState
from fedrec.utilities.serialization_utils import serializer_of

@serializer_of(AggregatorState)
class AggregatorStateSerializer(AbstractSerializer):

    def __init__(self, serialization_strategy):
        super().__init__(serialization_strategy)

    def serialize(self, obj):
 
        response_dict = {}
        response_dict["id"] = obj.id
        response_dict["round_idx"] = obj.round_idx
        response_dict["state_dict"] = self.serialize_attribute(
            obj.state_dict)
        response_dict["storage"] = obj.storage
        response_dict["in_neighbours"] = self.serialize_attribute(
            obj.in_neighbours)
        response_dict["out_neighbours"] = self.serialize_attribute(
            obj.out_neighbours)

        return self.serialization_strategy.unparse(response_dict)

    def deserialize(self, obj: Dict):
        obj = self.serialization_strategy.parse(obj)

        state_dict = self.deserialize_attribute(
            obj['state_dict'])
        in_neighbours = self.deserialize_attribute(
            obj['in_neighbours'])
        out_neighbours = self.deserialize_attribute(
            obj['out_neighbours'])

        return AggregatorState(id=obj['id'],
                               round_idx=obj['round_idx'],
                               state_dict=state_dict,
                               storage=obj['storage'],
                               in_neighbours=in_neighbours,
                               out_neighbours=out_neighbours)
