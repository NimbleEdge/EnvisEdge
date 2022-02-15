from collections import defaultdict

from defusedxml import NotSupportedError


SERIALIZER_MAP = defaultdict(dict)
ACTIVE_SERIALIZERS = defaultdict(dict)


class Serializable(object):

    @classmethod
    def type_name(cls):
        return cls.__name__


def serializer_of(serialized_class):
    assert issubclass(serialized_class, Serializable), NotSupportedError(serialized_class)

    cls_type_name = serialized_class.type_name()
    def decorator(serializer_name):
        if cls_type_name in SERIALIZER_MAP:
            raise LookupError('{} already present'.format(cls_type_name))
        SERIALIZER_MAP[cls_type_name] = serializer_name
        return serialized_class
    return decorator


def get_serializer(serialized_obj, srl_strategy):
    cls = None
    print(ACTIVE_SERIALIZERS)
    if isinstance(serialized_obj, Serializable):
        cls = serialized_obj.type_name()
    elif isinstance(serialized_obj, str):
        cls = serialized_obj
    else:
        raise NotSupportedError(serialized_obj)

    if cls in SERIALIZER_MAP:
        if cls not in ACTIVE_SERIALIZERS:
            ACTIVE_SERIALIZERS[cls] = SERIALIZER_MAP[cls](srl_strategy)
        ACTIVE_SERIALIZERS[cls].serialization_strategy = srl_strategy
    else:
        raise LookupError('{} class not present'.format(cls))
    
    return ACTIVE_SERIALIZERS[cls]
