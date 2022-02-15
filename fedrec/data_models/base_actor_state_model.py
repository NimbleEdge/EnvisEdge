import attr
from fedrec.utilities.serialization_utils import Serializable

@attr.s(kw_only=True)
class ActorState(Serializable):
    """Construct a ActorState object to reinstatiate an actor when needed.

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
    """
    id = attr.ib()
    round_idx = attr.ib(0)
    state_dict = attr.ib(None)
    storage = attr.ib(None)
