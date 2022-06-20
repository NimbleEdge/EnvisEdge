import argparse
import os
from collections.abc import Iterable
import torch


def load_tensors(path):
    if os.path.isfile(path) == True:
        tensors = torch.load(path)
        return tensors
    else:
        raise ValueError("Path does not exist.")


def to_dict_with_sorted_values(d, key=None):
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

def save_proto(storage, name, state):
    proto_path = os.path.join(storage, name) + '.pb'
    with open(proto_path, 'wb') as f:
        f.write(state.SerializeToString())

    return proto_path

def load_proto(proto_path, tensors):
    if os.path.isfile(proto_path):
        with open(proto_path, 'rb') as f:
            tensors.ParseFromString(f.read())
    else:
        raise ValueError("Path does not exist.")