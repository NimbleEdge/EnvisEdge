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
    -------------------------------------------
    The key and value pairs are extracted from 
    the given datastructure to convert into a
    dictionary format.
    """
    return {k: sorted(v, key=key) for k, v in d.items()}


def to_dict_with_set_values(d):
    """
    This function is used to create a dictionary by 
    key,value pairs but by conversion to a set first
    to remove the duplicate elements.
    ---------------------------------------------
    The key,value pairs in datatstucture passed as
    parameter is iterated and then checked if the 
    values are lists then only they are appended to 
    the new list created in tuple format. 
    And if they are not lists then they are directly
    appended to the new list.
    In the end the values in the new list is 
    converted to set values to remove duplicacy. 
    And finally they are put inside a new
    dictionary which is returned in the end.
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
    """
    This function is used to convert dictionary
    passed as parameter to a tuple.
    -------------------------------------------
    If the dictionary is empty then an empty tuple
    is returned. Otherwise it checks if the given
    dictionary is a valid dictionary or not and 
    the keys of the dictionary is stored in the 
    tuple and then it is returned in the end.
    """
    if dictionary is None:
        return tuple()
    assert isinstance(dictionary, dict)
    def value(x): return dictionary[x]
    return tuple(key for key in sorted(dictionary, key=value))


def dictify(iterable):
    """
    This function is used to convert an iterable 
    datastructure to a dictionary.
    --------------------------------------------
    A checking is done if the object passed as
    parameter is an iterable object or not. If it
    is an iterable object then key,value pairs are
    stored after every iterations in the dictionary.
    It is then returned in the end.
    """
    assert isinstance(iterable, Iterable)
    return {v: i for i, v in enumerate(iterable)}


def dash_separated_ints(value):
    """
    This function is used to convert the integer
    numbers in a string format to integer values.
    ----------------------------------------------
    The elements in the string passed as parameter 
    is spilt on basis of '-' character and stored 
    in a list. After that on every iteraration in
    the list each element of the list is tried to
    convert to integer format if it a proper object
    to get converted. Otherwise ValueError is thrown.
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
    This function is used to convert the float
    numbers in a string format to integer values.
    ----------------------------------------------
    The elements in the string passed as parameter 
    is spilt on basis of '-' character and stored 
    in a list. After that on every iteraration in
    the list each element of the list is tried to
    convert to float format if it a proper object
    to get converted. Otherwise ValueError is thrown.
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
