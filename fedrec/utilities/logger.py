from abc import ABC, abstractmethod
import logging
from time import time


class BaseLogger(ABC):
    def __init__(self) -> None:
        super().__init__()

    @staticmethod
    def time(func):
        def decorated(*args, **kwargs):
            start_time = time()
            out = func(*args, **kwargs)
            end_time = time()
            logging.info("aggregate time cost: %d" % (end_time - start_time))
            return out

        return decorated

    @abstractmethod
    def log(*args, **kwargs):
        pass

    @abstractmethod
    def log_gradients(*args, **kwargs):
        pass

    @abstractmethod
    def add_scalar(*args, **kwargs):
        pass

    @abstractmethod
    def add_histogram(*args, **kwargs):
        pass

    @abstractmethod
    def add_graph(*args, **kwargs):
        pass


try:
    from torch.utils.tensorboard import SummaryWriter

    class TBLogger(SummaryWriter, BaseLogger):
        def __init__(self, log_dir, comment="", max_queue=10):
            super().__init__(log_dir=log_dir,
                             comment=comment,
                             max_queue=max_queue)

        def log(self, *args, **kwargs):
            print(*args, **kwargs)

        def log_gradients(self, model, step, to_normalize=True):
            for name, param in model.named_parameters():
                if to_normalize:
                    grad = param.grad.norm()
                    self.add_scalar("grads/"+name, grad, global_step=step)
                else:
                    grad = param.grad
                    self.add_histogram("grads/"+name, grad, global_step=step)

except ImportError:
    UserWarning("Tensorboard not installed. No Tensorboard logging.")


class NoOpLogger(BaseLogger):
    def __init__(self) -> None:
        super().__init__()

    def log(*args, **kwargs):
        pass

    def log_gradients(*args, **kwargs):
        pass

    def add_scalar(*args, **kwargs):
        pass

    def add_histogram(*args, **kwargs):
        pass

    def add_graph(*args, **kwargs):
        pass
