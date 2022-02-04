'''
The registry class makes it easy and quick to experiment with
different algorithms, model architectures and hyperparameters.

We only need to decorate the class definitions with registry.load
and create a yaml configuration file of all the arguments to pass.

Later, if we want to change any parameter (eg. number of hidden layers,
learning rate, or number of clients per round), we need not change the
code but only change the parameters in yaml configuration file.

for detailed explaination on the use of registry, see:
github.com/NimbleEdge/RecoEdge/blob/main/docs/Tutorial-Part-2-starting_with_nimbleedge.md
'''

import collections
import collections.abc
import inspect
import sys

# a defaultdict provides default values for non-existent keys.
LOOKUP_DICT = collections.defaultdict(dict)


def load(kind, name):
    '''
    A decorator to record callable object definitions
    for models,trainers,workers etc.

    Arguments
    ----------
    kind: str
          Key to store in dictionary, used to specify the
          kind of object (eg. model, trainer).
    name: str
          Sub-key under kind key, used to specify name of
          of the object definition.

    Returns
    ----------
    callable:
          Decorator function to store object definition.

    Examples
    ----------
    >>> @registry.load('model', 'dlrm')
    ... class DLRM_Net(nn.Module): # This class definition gets recorded
    ... def __init__(self, arg):
    ...     self.arg = arg
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

    Arguments
    ----------
    kind: str
          Key to search in dictionary of registry.
    name: str
          Sub-key to search under kind key in dictionary
          of registry.

    Returns
    ----------
    callable:
          Object definition stored in registry under key kind
          and sub-key name.

    Examples
    ----------
    >>> @registry.load('model', 'dlrm')
    ... class DLRM_Net(nn.Module): # This class definition gets recorded
    ... def __init__(self, arg):
    ...     self.arg = arg
    >>> model = lookup('model', 'dlrm') # loads model class from registry
    >>> model  # model is a DLRM_Net object
    __main__.DLRM_Net
    '''

    # check if 'name' argument is a dictionary.
    # if yes, load the value under key 'name'.
    if isinstance(name, collections.abc.Mapping):
        name = name['name']

    if kind not in LOOKUP_DICT:
        raise KeyError('Nothing registered under "{}"'.format(kind))
    return LOOKUP_DICT[kind][name]


def construct(kind, config, unused_keys=(), **kwargs):
    '''
    Returns an object instance by loading definition from registry,
    and arguments from configuration file.

    Arguments
    ----------
    kind:        str
                 Key to search in dictionary of registry.
    config:      dict
                 Configuration dictionary loaded from yaml file
    unused_keys: tuple
                 Keys for values that are not passed as arguments to
                 insantiate the object but are still present in config.
    **kwargs:    dict, optional
                 Extra arguments to pass.

    Returns
    ----------
    object:
        Constructed object using the parameters passed in config and **kwargs.

    Examples
    ----------
    >>> @registry.load('model', 'dlrm')
    ... class DLRM_Net(nn.Module): # This class definition gets recorded
    ... def __init__(self, arg):
    ...     self.arg = arg
    >>> model = construct('model', 'drlm', (), arg = 5)
    >>> model.arg  # model is a DLRM_Net object with arg = 5
    5
    '''

    # check if 'config' argument is a string,
    # if yes, make it a dictionary.
    if isinstance(config, str):
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
                 Keys for values that are not passed as arguments to
                 insantiate the object but are still present in config.
    **kwargs:    dict, optional
                 Extra arguments to pass.

    Returns
    ----------
    object:
        Instantiated object by the parameters passed in config and **kwargs.

    Examples
    ----------
    >>> @registry.load('model', 'dlrm')
    ... class DLRM_Net(nn.Module): # This class definition gets recorded
    ... def __init__(self, arg):
    ...     self.arg = arg
    >>> config = {'name': 'dlrm', 'arg': 5} # loaded from a yaml config file
    >>> call = lookup('model', 'dlrm') # Loads the class definition
    >>> model = instantiate(call, config, ('name'))
    >>> model.arg  # model is a DRLM_Net object with arg = 5
    5
    '''

    # merge config arguments and kwargs in a single dictionary.
    merged = {**config, **kwargs}

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
