from abc import ABC
from typing import Any, Dict

import ray
from fedrec.utilities import registry


class ProcessManager(ABC):
    """
    A ProcessManager is a class that manages the processes that are spawned
    for multiprocessing.
    """

    def __init__(self, runnable: Any, num_workers: int, **kwargs: Dict):
        """
        Initialize a ProcessManager.

        Args:
            process_config: The configuration of the process.
        """
        self.process_config = kwargs
        self.num_workers = num_workers
        self.runnable = runnable

    def start(self):
        """
        Initialize the child processes for executing the job.
        """
        pass

    def shutdown(self):
        """
        Shutdown the child processes for executing the job.
        """
        pass

    def join(self):
        """
        Join the process.
        """
        pass

    def is_alive(self):
        """
        Check if the process is alive.
        """
        pass

    def get_status(self):
        """
        Get the results of the child processes.
        """
        pass


@registry.load("process_manager", "ray")
class RayProcessManager(ProcessManager):

    def __init__(self,
                 runnable: Any,
                 num_workers: int,
                 **kwargs: Any) -> None:
        super().__init__(runnable, num_workers, **kwargs)
        self.dist_runnable = ray.remote(runnable)
        self.workers = [None] ** num_workers

    def start(self) -> None:
        self.workers = [
            self.dist_runnable.run.remote(**self.process_config)
            for _ in range(self.num_workers)
        ]

    def shutdown(self) -> None:
        ray.shutdown()

    def get_status(self) -> Any:
        return ray.get(self.workers)
