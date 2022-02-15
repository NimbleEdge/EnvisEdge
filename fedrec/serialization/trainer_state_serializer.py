from typing import Dict

from fedrec.serialization.abstract_serializer import AbstractSerializer
from fedrec.data_models.aggregator_state_model import TrainerState


class TrainerStateSerializer(AbstractSerializer):

    def __init__(self, serialization_strategy):
        super().__init__(serialization_strategy)

    def serialize(self, obj):
 
        response_dict = {}
        response_dict["id"] = obj.id
        response_dict["round_idx"] = obj.round_idx
        response_dict["state_dict"] = self.serialize_attribute(
            obj.state_dict)
        response_dict["storage"] = obj.storage
        response_dict["model_preproc"] = self.serialize_attribute(
            obj.model_preproc)
        response_dict["local_sample_number"] = obj.local_sample_number
        response_dict["local_training_steps"] = obj.local_training_steps

        return self.serialization_strategy.unparse(response_dict)

    def deserialize(self, obj: Dict):

        state_dict = self.deserialize_attribute(
            obj['state_dict'])
        model_preproc = self.deserialize_attribute(
            obj['model_preproc'])

        return TrainerState(id=obj["id"],
                            obj["round_idx"],
                            state_dict,
                            obj["storage"],
                            model_preproc=model_preproc,
                            local_sample_number=obj["local_sample_number"],
                            local_training_steps=obj["local_training_steps"])
