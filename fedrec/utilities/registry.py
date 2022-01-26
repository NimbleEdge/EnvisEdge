import collections
import collections.abc
import inspect
import sys

LOOKUP_DICT = collections.defaultdict(dict)  # a defaultdict provides default values for non-existent keys.


def load(kind, name):
    '''
    A decorator function to record callable object definitions for models,trainers,workers etc.     
    '''
    registry = LOOKUP_DICT[kind]

    def decorator(obj):
        if name in registry:
            raise LookupError('{} already present'.format(name, kind)) 
        registry[name] = obj
        return obj

    return decorator


def lookup(kind, name):
    '''
    Returns the callable object definition stored in registry.
    '''
    if isinstance(name, collections.abc.Mapping):  # check if 'name' argument is a dictionary.
        name = name['name']

    if kind not in LOOKUP_DICT:
        raise KeyError('Nothing registered under "{}"'.format(kind))
    return LOOKUP_DICT[kind][name]


def construct(kind, config, unused_keys=(), **kwargs):
    '''
    Returns an object instance by loading defintion from registry, 
    and arguments from configuration file.   
    '''
    if isinstance(config, str):  # check if 'config' argument is a string.
        config = {'name': config}
    return instantiate(
        lookup(kind, config),
        config,
        unused_keys + ('name',),
        **kwargs)


def instantiate(callable, config, unused_keys=(), **kwargs):
    '''
    Instantiates an object after verifying the parameters.

    Arguments
    ----------
    callable:    callable
                 Definition of object to be instantiated.
    config:      dict
                 Arguments to construct the object.
    unused_keys: tuple
                 Unneccassary keys in config that callable does not require. 
    **kwargs:    dict, optional
                 Extra arguments to pass.
                 
    Returns
    ----------
    object
                 Instantiated object by the parameters passed in config and **kwargs.
    '''
    merged = {**config, **kwargs} # merge config arguments and kwargs in a single dictionary.

    # check if callable has valid parameters.
    signature = inspect.signature(callable) 
    for name, param in signature.parameters.items():
        if param.kind in (inspect.Parameter.POSITIONAL_ONLY,
                          inspect.Parameter.VAR_POSITIONAL):
            raise ValueError('Unsupported kind for param {}: {}'.format(
                name, param.kind))

    if any(param.kind == inspect.Parameter.VAR_KEYWORD
           for param in signature.parameters.values()):
        return callable(**merged)

    # check and warn if config has unneccassary arguments that 
    # callable does not require and are not mentioned in unused_keys.
    missing = {}
    for key in list(merged.keys()):
        if key not in signature.parameters:
            if key not in unused_keys:
                missing[key] = merged[key]
            merged.pop(key)
    if missing:
        print('WARNING {}: superfluous {}'.format(
            callable, missing), file=sys.stderr)
    return callable(**merged)
