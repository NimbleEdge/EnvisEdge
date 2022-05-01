import argparse
import os
from collections.abc import Iterable
import torch

def load_tensors(path):
    """
    This function is used to load the tensors 
    from the path passed as parameter.
    --------------------------------------------
    If a valid path is set as parameter then the
    tensors are loaded and returned. Otherwise 
    ValueError is thrown.
    """
    if os.path.isfile(path) == True:
        tensors = torch.load(path)
        return tensors
    else:
        raise ValueError("Path does not exist.")


def to_dict_with_sorted_values(d, key=None):
    """
    This function is used to convert the given 
    datastructure which is passed as parameter 
    to a dictionary. 
    The dictionary is returned in the end.
    -------------------------------------------
    The key and value pairs are extracted from 
    the given datastructure to convert into a
    dictionary format.
    """
    return {k: sorted(v, key=key) for k, v in d.items()}


def to_dict_with_set_values(d):
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
    This function is used to save the tensors 
    that were loaded and passed as parameters.
    ------------------------------------------
    If the path is a valid path then the tensors
    are saved and the path is returned. Otherwise
    multiple file paths are logically joined 
    after OS Module interacts with the OS to 
    form a correct path and then the tensors are
    saved and the correct path is returned.
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
    vals = value.split("-")
    for val in vals:
        try:
            float(val)
        except ValueError:
            raise argparse.ArgumentTypeError(
                "%s is not a valid dash separated list of floats" % value
            )

    return value
