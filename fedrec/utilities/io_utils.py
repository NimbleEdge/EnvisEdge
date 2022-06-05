import argparse
import os
from collections.abc import Iterable
import torch
from error_handler import errorhandler
from fedrec.serialization.s3_db import S3Interface
import yaml

global data

"""
    Loads the S3 DB creds from config file
"""
with open(r'./configs/regression.yml') as conf:
  
    data = yaml.load(conf, Loader=yaml.FullLoader)
    conf.close()
# Initialize the S3 service client

global s3_client
s3_client = S3Interface(data['s3']['region'], data['s3']['aws_access_key'], data['s3']['aws_secret_access_key'], data['log_dir']['PATH'])
global storage
storage = data['log_dir']['PATH']

def process_path(path:str) -> str:
    #process the path here 
    return path.replace("//", '/')

@errorhandler
def load_tensors(path):
    path = process_path(path)
    s3_path = path.replace(storage, '')
    file_path = s3_client.download(data['s3']['bucket_name'], s3_path)
    return torch.load(file_path)

@errorhandler
def to_dict_with_sorted_values(d, key=None):
    return {k: sorted(v, key=key) for k, v in d.items()}

@errorhandler
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

@errorhandler
def save_tensors(tensors, path) -> str:
    path = process_path(path)
    torch.save(tensors, path)
    s3_path = path.replace(storage, '')
    s3_client.upload(data['s3']['bucket_name'], path, s3_path)
    return path

@errorhandler
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
