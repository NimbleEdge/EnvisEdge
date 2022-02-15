from typing import Dict

from fedrec.data_models.messages import Message
from fedrec.serialization.abstract_serializer import AbstractSerializer
from fedrec.utilities.serialization_utils import serializer_of
from fedrec.data_models.job_submit_model import JobSubmitMessage


@serializer_of(JobSubmitMessage)
class JobSubmitSerializer(AbstractSerializer):

    def __init__(self, serialization_strategy):
        super().__init__(serialization_strategy)

    def serialize(self, obj):
        print(obj.job_args)
        response_dict = {}
        response_dict["job_type"] = obj.job_type
        response_dict["job_args"] = [self.serialize_attribute(arg)
                                     for arg in obj.job_args]
        response_dict["job_kwargs"] = {kwarg_name: self.serialize_attribute(kwarg)
                                       for kwarg_name, kwarg in obj.job_kwargs.items()}
        response_dict["worker_state"] = self.serialize_attribute(
            obj.workerstate)

        return self.serialization_strategy.unparse(response_dict)

    def deserialize(self, obj):
        obj_dict = self.serialization_strategy.parse(obj)
        job_args = [self.deserialize_attribute(arg)
                    for arg in obj["job_args"]]
        job_kwargs = {kwarg_name: self.deserialize_attribute(kwarg)
                      for kwarg_name, kwarg in obj["job_kwargs"].items()}
        worker_state = self.deserialize_attribute(obj["workerstate"])

        return JobSubmitMessage(obj["job_type"],
                                job_args,
                                job_kwargs,
                                worker_state)
