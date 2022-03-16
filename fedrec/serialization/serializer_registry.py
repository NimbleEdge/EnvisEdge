from collections import defaultdict
from typing import Dict, List, Tuple
from fedrec.utilities import registry
from defusedxml import NotSupportedError
from fedrec.utilities.registry import Registrable
from fedrec.serialization.serializable_interface import (Serializable,
                                                         is_primitives)


def get_deserializer(serialized_obj_name):
    # find the deserializer from registry
    # given object name.
    return Registrable.lookup_class_ref(serialized_obj_name)


def serialize_attribute(obj):
    # TODO : make a single global function 
    # for this method.
    ## location : [envis_base_module.py]
    # Then recusively call serialize_attribute on each
    # attribute in the dict.
    if isinstance(obj, Dict):
        return {k: serialize_attribute(v) for k, v in obj.items()}
    # Then recusively call serialize_attribute on each
    # attribute in the [List, Tuple]
    elif isinstance(obj, (List, Tuple)):
        return [serialize_attribute(v) for v in obj]
    # check for primitives
    elif is_primitives(obj):
        return obj
    else:
        assert isinstance(obj, Serializable), "Object must be serializable"
        return obj.serialize()


def deserialize_attribute(obj: Dict):
    # TODO : make a single global function 
    # for this method.
    ## location : [envis_base_module.py]
    # Initially take in dict from abstract comm manager 
    # from kafka consumer.
    # check for primitives
    if is_primitives(obj):
        return obj
    # check for __type__ in dictonary 
    elif "__type__" in obj:
        type_name = obj["__type__"]
        data = obj["__data__"]
        # Then recusively call deserialize_attribute on each
        # attribute in the dict.
        return get_deserializer(type_name).deserialize(data)
    elif isinstance(obj, Dict):
        return {k: deserialize_attribute(v) for k, v in obj.items()}
    # Then recusively call serialize_attribute on each
    # attribute in the [List, Tuple]
    elif isinstance(obj, (List, Tuple)):
        return [deserialize_attribute(v) for v in obj]
    else:
        raise ValueError("Object is not serializable")
