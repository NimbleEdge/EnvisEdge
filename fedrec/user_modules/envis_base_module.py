from re import A
from typing import Dict

from attr import attr

from fedrec.serialization.serializable_interface import is_primitives
from fedrec.utilities.random_state import Reproducible


class EnvisBase(Reproducible):
    """
    Base class for Envis.
    """

    def __init__(self, config: Dict):
        super().__init__(config["random"])
        self.config = config
        self.storage = self.config["log_dir"]["PATH"]

        self._storables = None

    def _get_default_state(self, obj, check_envis = True):
        # TODO : make a single global function
        # for this method.
        # location : [serializer_registry.py]
        
        if hasattr(obj, "serialize") and check_envis:
            setattr(obj, "storage", self.storage)
            return obj
        if isinstance(obj, dict):
            return {
                k: self._get_default_state(v)
                for k, v in obj.items()
            }
        elif isinstance(obj, (list, tuple)):
            return (
                self._get_default_state(v)
                for v in obj
            )
        elif is_primitives(obj):
            return obj
        # elif hasattr(obj, "envis_state"):
        #     return obj.envis_state
        # if None of the above them open the
        # object state and recursively iterate
        # upon it.
        else:
            return {
                k: self._get_default_state(v)
                for k, v in obj.__dict__.items()
            }

    def _set_state(self, obj, state: Dict):
        # TODO : make a single global function
        # for this method.
        # location : [serilizer_registry.py]
        # check if the item is wrapped for
        # envis edge module.
        # eg. for torch.nn.module, torch.optim.optimizer etc.
        for k, v in state.items():
            attribute = getattr(obj, k)
            if isinstance(attribute, dict):
                value = {
                    sub_k: self._set_state(attribute[sub_k], sub_v)
                    for sub_k, sub_v in v.items()
                }
            elif isinstance(attribute, (list, tuple)):
                value = (
                    self._set_state(attribute[idx], sub_v)
                    for idx, sub_v in enumerate(v)
                )
                if isinstance(attribute, list):
                    value = list(value)
            elif is_primitives(attribute):
                value = v
            elif hasattr(attribute, "envis_state"):
                attribute.load_envis_state(v)
                value = attribute
            elif hasattr(attribute, "serialize"):
                attribute = v
            # if None of the above them open the
            # object state and recursively iterate
            # upon it.
            else:
                for sub_k, sub_v in attribute.__dict__.items():
                    self._set_state(sub_v, v[sub_k])
                value = attribute
            setattr(obj, k, value)

        return obj

    def store_state(self):
        return None

    @property
    def envis_state(self):
        # check if self._storables is None
        # if yes, then add all the attributes of the object
        # to the dict.


        if self._storables is None and (self.store_state() is None):

            self._storables = {
                "envis_state": self._get_default_state(self, False)
            }
        else:
            a=self.store_state()
            self._storables = self._get_default_state(self.store_state())

        return self._storables

    def update(self, state: Dict):
        self._set_state(self, state)
        self._storables = state
