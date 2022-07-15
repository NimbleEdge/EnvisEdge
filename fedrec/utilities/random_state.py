import random
import sys
import attr
from typing import Dict
import numpy as np
import torch


class RandomState:
    """
    RandomState sets random values using the random, NumPy, and PyTorch
    modules.

    It returns the current internal state of the Random Number
    Generators (RNGs) of the random, NumPy, and PyTorch modules.

    ...

    Attributes
    ----------
    random_mod_state: object
        The current state of the generator.
    np_state: tuple
        The current state of the internal generator.
    torch_cpu_state: tuple
        The state of the random number state generator of the CPU
    torch_gpu_states: list
        List containing the state of the random number state generator
        of the GPU for each device.

    Method
    -------
    restore()
        Sets and restores the state for Numpy, Torch, & Torch RNGs
    """

    def __init__(self):
        self.random_mod_state = random.getstate()
        self.np_state = np.random.get_state()
        self.torch_cpu_state = torch.get_rng_state()
        self.torch_gpu_states = [
            torch.cuda.get_rng_state(d)
            for d in range(torch.cuda.device_count())
        ]

    def restore(self):
        random.setstate(self.random_mod_state)
        np.random.set_state(self.np_state)
        torch.set_rng_state(self.torch_cpu_state)
        for d, state in enumerate(self.torch_gpu_states):
            torch.cuda.set_rng_state(state, d)


class RandomContext:
    """
    RandomContext makes the RNGs reproducible by setting the seed values
    for the random, numpy, and torch modules
    
    It uses the object methods of the random, numpy, and torch modules
    to set the state for the RNGs by using a seed value and then proceeds
    to save and restore the state for the RNGs.
    
    ...

    Arguments
    ----------
    seed: optional
        The seed value to use for the generation of the random number
        (default is None). Useful when seed is called in order to reset
        the RNG which makes the random numbers predictable.

    Attributes
    ----------
    outside_state: array
        Sets the state of the generator.
    inside_state: array
        Sets the state of the internal generator.
    _active: bool
        Sets the active state of the RandomContext to False.

    Methods
    -------
    __enter__()
        Ensures the RandomContext is active if it is inactive, such that
        the values are set only once.
    __exit__()
        Makes the RandomContext inactive. It also includes parameters
        that describe exceptions that will cause the exit of the
        RandomContext.
    """

    def __init__(self, seed=None):
        outside_state = RandomState()

        random.seed(seed)
        np.random.seed(seed)
        if seed is None:
            torch.manual_seed(random.randint(-sys.maxsize - 1, sys.maxsize))
        else:
            torch.manual_seed(seed)
        self.inside_state = RandomState()

        outside_state.restore()

        self._active = False

    def __enter__(self):
        if self._active:
            raise Exception('RandomContext can be active only once')
        self.outside_state = RandomState()
        self.inside_state.restore()
        self._active = True

    def __exit__(self, exception_type, exception_value, traceback):
        self.inside_state = RandomState()
        self.outside_state.restore()
        self.outside_state = None

        self._active = False


@attr.s
class RandomizationConfig:
    """
    RandomizationConfig sets the seed values that the RNGs will use for
    randomizing the training data, model initialization, or model
    computation.
    """
    data_seed = attr.ib(default=None)
    init_seed = attr.ib(default=None)
    # Seed for RNG used in computing the model's training loss.
    # Only relevant with internal randomness in the model, e.g. with dropout.
    model_seed = attr.ib(default=None)


class Reproducible(object):
    """
    This class reproduces the random values that the RNGs will use
    for randomizing the training data, model initialization, or model
    computation.
    ...

    Argument
    ----------
    config: dict
        The configuration for the randomization of the training data,
        model initialization, or model computation.
    
    Method
    -------
    __init__()
        Initializes the Reproducible class.
    """
    def __init__(self, config: Dict) -> None:
        self.data_random = RandomContext(
            config["data_seed"])
        self.model_random = RandomContext(
            config["model_seed"])
        self.init_random = RandomContext(
            config["init_seed"])
