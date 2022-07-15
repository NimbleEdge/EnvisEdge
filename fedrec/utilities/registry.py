"""
The registry class makes it easy and quick to experiment with
different algorithms, model architectures and hyperparameters.

We only need to decorate the class definitions with registry.load
and create a yaml configuration file of all the arguments to pass.

Later, if we want to change any parameter (eg. number of hidden layers,
learning rate, or number of clients per round), we need not change the
code but only change the parameters in yaml configuration file.

for detailed explaination on the use of registry, see:
github.com/NimbleEdge/EnvisEdge/blob/main/docs/Tutorial-Part-2-starting_with_nimbleedge.md
"""

import collections
import collections.abc
import inspect
import sys

# a defaultdict provides default values for non-existent keys.
LOOKUP_DICT = collections.defaultdict(dict)


def load(kind, name):
    """
    This function returns a decorator function to store object
    definitions for models, trainers, workers, etc., in the registry.
    
    It also validates the object definition before the definition
    gets loaded in the registry. That, when the name of the object
    definition is not in the registry, it raises an error.

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
    decorator: func
          Decorator function to store object definitions.

    Examples
    ----------
    >>> @registry.load('model', 'dlrm')
    ... class DLRM_Net(nn.Module): # This class definition gets recorded
    ... def __init__(self, arg):
    ...     self.arg = arg
    """

    assert kind != "class_map", "reserved keyword for kind \"class_map\""
    registry = LOOKUP_DICT[kind]
    class_ref = LOOKUP_DICT["class_map"]

    def decorator(obj):
        if name in registry:
            raise LookupError('{} already present'.format(name, kind))
        registry[name] = obj
        class_ref[obj.__module__ + "." + obj.__name__] = obj
        return obj
    return decorator


def lookup(kind, name):
    """
    This function returns an object definition by loading the
    stored object definition from the registry and arguments
    from a configuration file.
    
    It also verifies the validity of the object definition
    before the definition gets loaded. If the object definition
    is not valid, it raises an error.

    Arguments
    ----------
    kind: str
          Key to search in dictionary of registry.
    name: str
          Sub-key to search under kind key in dictionary of
          registry.

    Returns
    ----------
    object
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
    """
    # check if 'name' argument is a dictionary.
    # if yes, load the value under key 'name'.
    if isinstance(name, collections.abc.Mapping):
        name = name['name']

    if kind not in LOOKUP_DICT:
        raise KeyError('Nothing registered under "{}"'.format(kind))
    return LOOKUP_DICT[kind][name]


def construct(kind, config, unused_keys=(), **kwargs):
    """
    This function constructs an object after verifying its parameters. It
    is similar to instantiate except that it does not instantiate the
    object. It just constructs the object.

    It is used to construct the object definition from the configuration file.

    Arguments
    ----------
    kind: str
            Key to search in dictionary of registry.
    config: dict
            Dictionary of arguments to construct the object.
    unused_keys: list
            List of keys in the configuration file that are not
            used in the object definition. These keys are ignored.
    kwargs: dict
            Keyword arguments to construct the object. These keyword
            arguments are ignored. This is useful if the object definition
            has some default arguments. For example, if the object definition
            has a default argument of 'num_classes', then the object can be
            constructed by passing the keyword argument 'num_classes' to the
            function.

    Returns
    ----------
    object
            Object definition stored in registry under key kind and sub-key
            name. If the object definition is not valid, it raises an error.

    Examples
    ----------
    >>> @registry.load('model', 'dlrm')
    ... class DLRM_Net(nn.Module): # This class definition gets recorded
    ... def __init__(self, arg):
    ...     self.arg = arg
    >>> model = construct('model', 'drlm', (), arg = 5)
    >>> model.arg  # model is a DLRM_Net object with arg = 5
    5
    """

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
    """
    This function instantiates an object after verifying its parameters.
    It is similar to construct except that it instantiates the object. It
    is used to instantiate the object definition from the configuration file.

    Arguments
    ----------
    callable: object
            Object definition stored in registry under key kind and sub-key
            name. If the object definition is not valid, it raises an error.
    config: dict
            Dictionary of arguments to construct the object. It is used to
            instantiate the object. It is also used to verify the validity
            of the object definition.
    unused_keys: list
            List of keys in the configuration file that are not used in the
            object definition. These keys are ignored. This is useful if the
            object definition has some default arguments.
    kwargs: dict (optional)
            Keyword arguments to construct the object. These keyword arguments
            are ignored. This is useful if the object definition has some
            default arguments.
    
    Returns
    ----------
    object
            Instantiated object by the parameters passed in config and
            \**kwargs.
    
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
    """

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


class Registrable(object):
    """
    This class is used to register an object definition in the registry,
    and check for new class objects. The object definition is stored in
    the registry under the key 'kind' and sub-key 'name' in the dictionary.
    
    The object definition is a dictionary that contains the class object
    and the arguments that are used to construct the object.

    Methods
    -----------
    type_name()
        Returns the type name of the object. This is used to identify the
        object in the registry.
    get_name()
        Returns the name of the object. This is used to identify the object
        in the registry.
    register_class_ref()
        Registers the class object in the registry.
    lookup_class_ref()
        Returns the class object from the registry. This is used to instantiate
        the object.

    """

    def __init__(self) -> None:
        pass
    
    @classmethod
    def type_name(cls):
        return cls.__module__ + "." + cls.__name__

    @staticmethod
    def get_name(obj):
        if not callable(obj):
            obj = obj.__class__
        return obj.__module__ + "." + obj.__name__

    @staticmethod
    def register_class_ref(class_ref, name=None):
        if name is None:
            assert issubclass(class_ref, Registrable), \
                'Annotated class must be a subclass of Registrable'
            name = class_ref.type_name()
        
        LOOKUP_DICT["class_map"][name] = class_ref
        return class_ref

    @staticmethod
    def lookup_class_ref(class_name):
        if class_name not in LOOKUP_DICT["class_map"]:
            raise KeyError('No class found for "{}"'.format(class_name))
        return LOOKUP_DICT["class_map"][class_name]
