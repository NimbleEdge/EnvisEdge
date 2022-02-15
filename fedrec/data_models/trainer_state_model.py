import attr
from fedrec.data_models.base_actor_state_model import ActorState


@attr.s(kw_only=True)
class TrainerState(ActorState):
    """Construct a workerState object to reinstatiate a worker when needed.

    Attributes
    ----------
    id : int
        Unique worker identifier
    model_preproc : `Preprocessor`
        The local dataset of the worker
    round_idx : int
        The number of local training cycles finished
    state_dict : dict
        A dictionary of state dicts storing model weights and optimizer dicts
    storage : str
        The address for persistent storage
    """
    model_preproc = attr.ib()
    local_sample_number = attr.ib()
    local_training_steps = attr.ib()
