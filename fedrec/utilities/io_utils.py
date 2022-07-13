import argparse
import os
from collections.abc import Iterable
import torch


def load_tensors(path):
   """
   Checks if the file path is true, if yes then it
   loads the path to tensor and returns it else raises
   a value error if the path doesn't exist.
   """
    if os.path.isfile(path) == True:
        tensors = torch.load(path)
        return tensors
    else:
        raise ValueError("Path does not exist.")


def to_dict_with_sorted_values(d, key=None):
    """
    Takes dictionary d as parameter and returns dict
    with v values sorted.
    """
    return {k: sorted(v, key=key) for k, v in d.items()}


def to_dict_with_set_values(d):
    """
    Returns the result in set by checking the type
    of values being passed through the parameter d.
    """
    result = {}
    for k, v in d.items():
        hashable_v = []
        for v_elem in v:
            if isinstance(v_elem, list):
                hashable_v.append(tuple(v_elem))
            else:
                hashable_v.append(v_elem)
        result[k] = set(hashable_v)
    return result


def save_tensors(tensors, path) -> str:
    """
    Checks if the file path is true then it returns
    the tensor path else the path is joined to
    "completeName" which is further returned.

    Example
    -------
    >>> import tensorflow

      # creating object and asigning location
    >>> model=tensorflow.keras.Model()
    >>> path='Model_folder/Files'

      # saving model to specified path
    >>> model.save_weights(path)

    """

    if os.path.isfile(path) == True:
        torch.save(tensors, path)
        return path
    else:
        completeName = os.path.join(path)
        file1 = open(completeName, "wb")
        torch.save(tensors, file1)
        return completeName


def tuplify(dictionary):
    if dictionary is None:
        return tuple()
    assert isinstance(dictionary, dict)
    def value(x): return dictionary[x]
    return tuple(key for key in sorted(dictionary, key=value))


def dictify(iterable):
    assert isinstance(iterable, Iterable)
    return {v: i for i, v in enumerate(iterable)}


def dash_separated_ints(value):
    """
    This method takes a list of int as input
    and returns the dash-seperated list of values.

    Example
    -------
    >>> value = "2-3-4"
    >>> x = value.split("-")
    >>> print(x)
    ['2','3','4']

    """
    vals = value.split("-")
    for val in vals:
        try:
            int(val)
        except ValueError:
            raise argparse.ArgumentTypeError(
                "%s is not a valid dash separated list of ints" % value
            )

    return value


def dash_separated_floats(value):
    """
    This method takes a list of float values as input
    and returns the dash-seperated list of values.

    Example
    -------
    >>> value = "1.0-1.0"
    >>> x = value.split("-")
    >>> print(x)
    ['1.0','1.0']

    """
    vals = value.split("-")
    for val in vals:
        try:
            float(val)
        except ValueError:
            raise argparse.ArgumentTypeError(
                "%s is not a valid dash separated list of floats" % value
            )

    return value
