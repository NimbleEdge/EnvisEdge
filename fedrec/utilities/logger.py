import logging
from abc import ABC, abstractmethod
from time import time


class BaseLogger(ABC):
    """
    The 'BaseLogger' performs the logging messages and
    visualization activities.

    The logging module in python is a way to store information
    about the script and track events that occur. Similarly
    here, logging.info() helps in printing the aggregated time cost.

    Visualization activities are being performed by Tensorboard by
    importing SummaryWriter.Tensorboard is a suite of web applications
    for inspecting and understanding model metrics and graphs. It supports
    totally five visualizations i.e scalars, images, graphs, audio and
    histograms.

    Example
    -------

    >>> import logging

    >>> logging.basicConfig(filename="myfile.log",
                    format='%(asctime)s %(message)s',
                    filemode='w')
    >>> logger = logging.getLogger()
    >>> logger.setLevel(logging.DEBUG)

    >>> logger.debug("Safe debug Message")
    >>> logger.info("It's an information")
    >>> logger.warning("Its a Red Alert")
    >>> logger.error("Did you try to divide by zero")
    >>> logger.critical("Internet is down")

    """
    def __init__(self) -> None:
        super().__init__()

    @staticmethod
    def time(func):

        def decorated(*args, **kwargs):
            """
            Prints the logging info message i.e aggregated time cost
            on the screen.
            """
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
        """
        Helps in visualizing the data through the tensorboard
        class. Tensorboard logger class is implemented using
        SummaryWriter and BaseLogger.As mentioned previously,
        summary writer helps visualize graphs and histograms.
        Whereas, Baselogger is used to inherit the properties
        to the TBLogger in order to avoid reimplementing basic
        functions.

        Example
        -------

        >>> from torch.utils.tensorboard import SummaryWriter

        >>> writer = SummaryWriter()
        >>> x = range(100)
        >>> for i in x:
                writer.add_scalar('y=2x', i * 2, i)
        >>> writer.close()

        >>> from torch.utils.tensorboard import SummaryWriter
        >>> writer = SummaryWriter()
        >>> r = 5
        >>> for i in range(100):
        >>> writer.add_scalars('run_14h', {'xsinx':i*np.sin(i/r),
                                    'xcosx':i*np.cos(i/r),
                                    'tanx': np.tan(i/r)}, i)
        >>> writer.close()

        """
        def __init__(self, log_dir, comment="", max_queue=10):
            super().__init__(log_dir=log_dir,
                             comment=comment,
                             max_queue=max_queue)

        def log(self, *args, **kwargs):
            print(*args, **kwargs)

        def log_gradients(self, model, step, to_normalize=True):
            """
            Returns a scalar or histogram on the basis of bool value
            given to to_normalize.

            """
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
