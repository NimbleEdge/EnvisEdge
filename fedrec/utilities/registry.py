import collections
import collections.abc
import inspect
import sys

LOOKUP_DICT = collections.defaultdict(dict)


def load(kind, name):
    registry = LOOKUP_DICT[kind]

    def decorator(obj):
        if name in registry:
            raise LookupError('{} already present'.format(name, kind))
        registry[name] = obj
        return obj

    return decorator


def lookup(kind, name):
    if isinstance(name, collections.abc.Mapping):
        name = name['name']

    if kind not in LOOKUP_DICT:
        raise KeyError('Nothing registered under "{}"'.format(kind))
    return LOOKUP_DICT[kind][name]


def construct(kind, config, unused_keys=(), **kwargs):
    if isinstance(config, str):
        config = {'name': config}
    return instantiate(
        lookup(kind, config),
        config,
        unused_keys + ('name',),
        **kwargs)


def instantiate(callable, config, unused_keys=(), **kwargs):
    merged = {**config, **kwargs}
    signature = inspect.signature(callable)
    for name, param in signature.parameters.items():
        if param.kind in (inspect.Parameter.POSITIONAL_ONLY, inspect.Parameter.VAR_POSITIONAL):
            raise ValueError('Unsupported kind for param {}: {}'.format(
                name, param.kind))

    if any(param.kind == inspect.Parameter.VAR_KEYWORD
           for param in signature.parameters.values()):
        return callable(**merged)

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
