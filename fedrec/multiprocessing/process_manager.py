import atexit
import logging
from abc import ABC
from collections import defaultdict
from typing import Any, DefaultDict, Dict

import ray
from fedrec.utilities import registry


class ProcessManager(ABC):
    """
    This class is used to manage the child processes. It is used to start,
    shutdown and check the status of the child processes for executing the
    job.

    A ProcessManager is a class that manages the processes that are spawned
    for multiprocessing. During multiprocessing, the ProcessManager is
    responsible for starting the processes that will be required for executing
    the job. It is also responsible for shutting down the processes that are
    spawned and also responsible for checking the status of the processes that
    have been spawned.

    Attributes
    -----------
    workers: dict
        Dictionary that contains the workers.
    
    Methods
    -----------
    start()
        Initialize the child processes for executing the job.
    shutdown()
        Shutdown the child processes for executing the job.
    is_alive()
        Check if the process is alive.
    get_status()
        Get the results of the child processes.
    
    Example
    -----------
    >>> from fedrec.utilities.process_manager import ProcessManager
    >>> pm = ProcessManager() # Create a ProcessManager object
    >>> pm.start() # Start the processes
    >>> pm.shutdown() # Shutdown the processes
    >>> pm.is_alive() # Check if the processes are alive
    >>> pm.get_status() # Get the results of the processes
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
    """
    The RayProcessManager class manages the processes that are spawned
    for multiprocessing. It uses the Ray library to manage the processes that
    are spawned.

    The RayProcessManager class inherits from the ProcessManager class and
    overrides the distribute, start, shutdown, is_alive, and get_status methods.
    """

    def __init__(self) -> None:
        super().__init__()
        ray.init()
        atexit.register(self.shutdown)

    def distribute(self, runnable,
                   type: str,
                   num_instances: int,
                   *args, **kwargs) -> None:
        """
        Allocates child processes to separate Python worker to be
        executed asynchronously
        
        Parameters
        ----------
        runnable : callable
            the callable to be allocated for asynchronous processing
        type : str
            Name or type of runnable, acts as an identifier for the runnable
        num_instances : int
            Number of instances of the runnable to be processed asynchronously
        *args :
            Variable length keyword argument list.
        **kwargs :
            Arbitrary keyword arguments: refer to ray.remote
            documentation for a list of all possible arguments.
        """

        dist_runnable = ray.remote(runnable)
        new_runs = [dist_runnable.remote(*args, **kwargs)
                    for _ in range(num_instances)]
        self.workers[type] += new_runs

    def start(self, runnable_type, method, *args, **kwargs) -> None:
        """
        Executes asychronous processing of child processes
        
        Parameters
        ----------
        runnable_type : str
            Name or type of runnable, acts as an identifier for the runnable
        method : callable
            the callable to be executed asynchronously
        *args :
            Variable length keyword argument list.
        **kwargs :
            Arbitrary keyword arguments: refer to ray.remote
            documentation for a list of all possible arguments.
        """
        if callable(method):
            method = method.__name__
        for runnable in self.workers[runnable_type]:
            getattr(runnable, method).remote(*args, **kwargs)

    def shutdown(self) -> None:
        """
        Disconnects workers and terminates processes
        """
        ray.shutdown()

    def get_status(self) -> Any:
        """
        Get the results of child processes.
        The function will wait until all results are available in sequence.
        
        Returns
        -------
        Results of Callable: Any
            A Python object or a list of Python objects containing results
            of callable asynchronous processing
        """
        return ray.get(self.workers)
