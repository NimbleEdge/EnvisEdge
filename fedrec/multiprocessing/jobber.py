from fedrec.trainers.base_trainer import BaseTrainer
from fedrec.utilities.serialization import deserialize_object, serialize_object
from fedrec.communications.messages import JobCompletions
import json
class Jobber:
    """
    Jobber class only handles job requests based on job type
    """
    def __init__(self, trainer, logger) -> None:
        self.logger = logger
        self.trainer: BaseTrainer = trainer
        self.trainer_funcs = [func  for func in dir(self.trainer) if callable(getattr(self.trainer, func))]

    def run(self, message):
        job_type = message.JOB_TYPE
        if job_type in self.trainer_funcs:
            job_args = [deserialize_object(i) for i in json.loads(message.MSG_ARG_JOB_ARGS)]
            job_kwargs = {key: deserialize_object(val) for key, val in json.loads(message.MSG_ARG_JOB_KWARGS)}
            result_message = JobCompletions()
            result_message.SENDER_ID = message.SENDER_ID
            try:
                job_result = getattr(self.trainer, job_type)(*job_args, **job_kwargs)
                result_message.STATUS = True
                serialized_results = {key: serialize_object(val) for key, val in job_result}
                result_message.add_params(result_message.RESULTS, json.dumps(serialized_results))
            except Exception as e:
                result_message.STATUS = False
                result_message.add_params(result_message.ERRORS, str(e))
            return result_message
        else:
            raise ValueError(f"Job type not part of trainer functions: {job_type}")
