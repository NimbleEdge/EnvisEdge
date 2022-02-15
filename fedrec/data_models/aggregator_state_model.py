
import attr
from fedrec.data_models.base_actor_state_model import ActorState


@attr.s(kw_only=True)
class AggregatorState(ActorState):
    """Construct a AggregatorState object to reinstatiate a worker when needed.

    Attributes
    ----------
    id : int
        Unique worker identifier
    round_idx : int
        The number of local training cycles finished
    state_dict : dict
        A dictionary of state dicts storing model weights and optimizer dicts
    storage : str
        The address for persistent storage
    neighbours :
        {"in_neigh" : List[`Neighbour`], "out_neigh" : List[`Neighbour`]]
        The states of in_neighbours and out_neighbours of the
        worker when last synced
    """
    in_neighbours = attr.ib(dict)
    out_neighbours = attr.ib(dict)
