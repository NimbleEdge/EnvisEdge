from fedrec.communications.messages import JobResponseMessage, JobSubmitMessage
from fedrec.python_executors.base_actor import BaseActor
from fedrec.utilities.serialization import deserialize_object, serialize_object


class Jobber:
    """
    Jobber class only handles job requests based on job type
    """

    def __init__(self, worker, logger) -> None:
        self.logger = logger
        self.worker: BaseActor = worker
        self.worker_funcs = {func.__name__: func for func in dir(
            self.worker) if callable(getattr(self.worker, func))}

    def run(self, message: JobSubmitMessage):
        if message.job_type in self.worker_funcs:
            job_args = [
                deserialize_object(i) for i in message.job_args.items()]
            job_kwargs = {
                key: deserialize_object(val)
                for key, val in message.job_kwargs.items()}
            result_message = JobResponseMessage(
                job_type=message.job_type,
                senderid=message.receiverid,
                receiverid=message.senderid)
            try:
                job_result = self.worker_funcs[message.job_type](
                    *job_args, **job_kwargs)
                result_message.results = {key: serialize_object(
                    val) for key, val in job_result}
            except Exception as e:
                result_message.errors = e
            return result_message
        else:
            raise ValueError(
                f"Job type <{message.job_type}> not part of worker <{self.worker.__class__.__name__}> functions")
