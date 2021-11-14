import io
import os
import torch
import numpy as np
import pathlib
import attr
from collections.abc import Iterable
import argparse
import pickle
from warnings import warn

def load_tensor(file, device=None):
    t = torch.load(file)
    if device is not None:
        t = t.to(device)
    return t

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


def save_tensor(tensor, file):
    pathlib.Path(file).parent.mkdir(parents=True, exist_ok=True)
    torch.save(tensor, file)


def toJSON(obj):
    ''' 
    Calls this instance in case of serialization failure.
    Assumes the object is attr 
    '''
    if attr.has(obj):
        return attr.asdict(obj)
    elif isinstance(obj, np.int64):
        return int(obj)
    else:
        raise NotImplementedError(
            "serialization obj not attr but {}".format(type(obj)))


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


def copy_s3_file(self, file):
    # TODO: Add aws CLI support like BOTO3, using os.system to copy until then,
    # Once CLI is installed use Stream to store the file.
    # Create a temporary file to copy data and then load it to stream
    extension = file.split(".")[-1]
    rand_nums = "".join([str(random.randint(0,9)) for _ in range(8)])
    tmp_file = "./.tmp.{}.{}".format(rand_nums, extension)
    os.system("aws s3 cp {} {}".format(file, tmp_file))
    return tmp_file


def is_s3_file(self, file):
        import httplib
        from urlparse import urlparse

        def url_exists(url):
            _, host, path, _, _, _ = urlparse(url)
            conn = httplib.HTTPConnection(host)
            conn.request('HEAD', path)
            return conn.getresponse().status < 400

        if "amazon.aws" in str(file) and url_exists(str(file)):
            return True
            # TODO: Make this check more robust.
        return False

# TODO: Take care of serialization for specific objects
def serialize_object(obj, file=None):
    """
    param file: This can either be a local file storage system or a file to be stored in the s3 clod.
    """
    if isinstance(obj, torch.tensor):
        if file:
            # if file is provided, save the tesor to the file and return the file path.
            save_tensor(obj, file)
        else:
            # create a buffer Bytes object, which can be used to write to the file.
            buffer = io.BytesIO()
            save_tensor(obj, buffer)

    if isinstance(obj, str) or isinstance(obj, bytes):
        # TODO : Pickle if bytes else pickled v/s bytes can't be differentiated.
        return obj
    else:
        warn(f"Pickle is being used to serialize object of type: {type(obj)}")
        return pickle.dumps(obj)


def deserialize_object(obj):
    """
    param obj: It can be a file containing tensor the file maybe stream file or a file path or serialized pkl string.
    """
    # the file can be link of s3 storage system:
    if is_s3_file(obj):
        # This is most likely to be a link of s3 storage.
        # Copy the file locally and then deserialize it.
        path = copy_s3_file(obj)

    if  pathlib.Path(obj).exists() or isinstance (obj, io.BytesIO):
        try:
            # This should be the path to the tensor object.
            tensor = load_tensor(obj, device=None)
        except Exception as e:
            if str(e.type) is FileNotFoundError:
                warn("the filename specified to load the tensor from could not be accessed, Please make sure the path has correct permissions")
        else:
            return tensor
    if isinstance(obj, str):
        return obj
    else:
        warn(
            f"Pickle is being used to deserialize object of type: {type(obj)}")
        return pickle.loads(obj)
