from collections import defaultdict


class WorkerDataset:
    """
    This class represents a dataset of workers and includes methods
    for adding and loading federated workers.

    The WorkerDataset class also allows for the retrieval
    of workers based on their role IDs. This is useful for the
    distributed training process.
    ...

    Attributes
    ----------
    workers: dict
        Dictionary of workers. The key is the worker ID and the
        value is the worker object.
    workers_by_types: dict
        Dictionary of lists of workers. The key is the role ID and
        the value is a list of worker IDs.
    len: int
        Number of federated workers in the dataset.

    Methods
    -------
    add_worker()
        Method to create new federated workers.
    get_worker()
        Method to get a federated worker based on its ID.
    get_workers_by_roles()
        Method to get a list of federated workers based on their
        role IDs.
    """

    def __init__(self) -> None:
        self._workers = {}
        self.workers_by_types = defaultdict(list)
        self._len = 0

    def add_worker(self,
                   trainer,
                   roles,
                   in_neighbours,
                   out_neighbours):

        in_neighbours = [Neighbour(n) for n in in_neighbours]
        out_neighbours = [Neighbour(n) for n in out_neighbours]

        self._workers[self._len] = FederatedWorker(
            self._len, roles, in_neighbours, out_neighbours, trainer)

        for role in roles:
            self.workers_by_types[role] += [self._len]

        self._len += 1

    def get_worker(self, id):
        # TODO We might persist the state in future
        # So this loading will be dynamic.
        # Then would create a new Federated
        # worker everytime from the persisted storage
        return self._workers[id]

    def get_workers_by_roles(self, role):
        return [self._workers[id] for id in self.get_workers_by_roles[role]]

    def __len__(self):
        return self._len
