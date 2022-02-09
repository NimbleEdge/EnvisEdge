from typing import Dict

from fedrec.data_models.messages import Message
from fedrec.serialization.abstract_serializer import AbstractSerializer
from fedrec.data_models.job_submit_model import JobSubmitMessage


class JobSubmitSerializer(AbstractSerializer):

    def __init__(self, serialization_strategy):
        super().__init__(serialization_strategy)

    def serialize(self, obj):
        response_dict = {}
        response_dict["job_type"] = obj.job_type
        response_dict["job_args"] = [self.serialize_attribute(arg)
                                     for arg in obj.job_args]
        response_dict["job_kwargs"] = [self.serialize_attribute(kwarg)
                                       for kwarg in obj.job_kwargs]
        response_dict["worker_state"] = self.serialize_attribute(
            obj.workerstate)

        return self.serialization_strategy.unparse(response_dict)

    def deserialize(self, obj: Dict):
        job_args = [self.deserialize_attribute(arg)
                    for arg in obj['job_args']]
        job_kwargs = [self.deserialize_attribute(kwarg)
                      for kwarg in obj['job_kwargs']]
        worker_state = self.deserialize_attribute(obj['workerstate'])

        return JobSubmitMessage(obj["job_type"],
                                job_args,
                                job_kwargs,
                                worker_state)
