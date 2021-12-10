from abc import ABC
import atexit
from collections import defaultdict
from typing import Any, DefaultDict, Dict

import ray
from fedrec.utilities import registry


class ProcessManager(ABC):
    """
    A ProcessManager is a class that manages the processes that are spawned
    for multiprocessing.
    """

    def __init__(self) -> None:
        super().__init__()
        self.workers = defaultdict(list)

    def distribute(self):
        pass

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

    def __init__(self) -> None:
        super().__init__()
        ray.init()
        atexit.register(self.shutdown)

    def distribute(self, runnable, type: str, num_instances: int, *args, **kwargs) -> None:
        dist_runnable = ray.remote(runnable)
        print(args)
        print(kwargs)
        new_runs = [dist_runnable.remote(*args, **kwargs)
                    for _ in range(num_instances)]
        self.workers[type] += new_runs

    def start(self, runnable_type, method, *args, **kwargs) -> None:
        if callable(method):
            method = method.__name__
        for runnable in self.workers[runnable_type]:
            getattr(runnable, method).remote(*args, **kwargs)

    def shutdown(self) -> None:
        ray.shutdown()

    def get_status(self) -> Any:
        return ray.get(self.workers)
