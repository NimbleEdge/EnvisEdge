from fedrec.serialization.serializable_interface import Serializable
from fedrec.data_models.state_tensors_model import StateTensors
from torch.optim import optimizer

class TorchOptimizer(Serializable):

    def __init__(self, optimzer) -> None:
        self.optimizer = optimzer
        super().__init__()


    def serialize(self):
        return
