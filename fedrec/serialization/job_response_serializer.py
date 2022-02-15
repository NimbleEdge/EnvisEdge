from typing import Dict
from fedrec.serialization.abstract_serializer import AbstractSerializer
from fedrec.utilities.serialization_utils import serializer_of
from fedrec.data_models.job_response_model import JobResponseMessage



@serializer_of(JobResponseMessage)
class JobResponseSerializer(AbstractSerializer):

    def __init__(self, serialization_strategy):
        super().__init__(serialization_strategy)

    def serialize(self, obj):
        response_dict = {}
        response_dict["job_type"] = obj.job_type
        response_dict["senderid"] = self.serialize_attribute(
            obj.senderid)
        response_dict["receiverid"] = self.serialize_attribute(
            obj.receiverid)
        response_dict["results"] = self.serialize_attribute(
            obj.results)

        return self.serialization_strategy.unparse(response_dict)

    def deserialize(self, obj: Dict):
        senderid = self.deserialize_attribute(obj['senderid'])
        receiverid = self.deserialize_attribute(obj['senderid'])
        

        return JobResponseMessage(obj["job_type"],
                                  senderid,
                                  receiverid)
