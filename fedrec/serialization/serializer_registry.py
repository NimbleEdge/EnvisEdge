from typing import Dict, List, Tuple

from fedrec.serialization.serializable_interface import (Serializable,
                                                         is_primitives)
from fedrec.utilities.registry import Registrable


def get_deserializer(serialized_obj_name):
    """
    Receives deserializer from registry module.

    Parameters
    -----------
    serialized_obj_name: str
        The object name of serializer.
    Returns
    --------
    obj
    """
    # find the deserializer from registry
    # given object name.
    return Registrable.lookup_class_ref(serialized_obj_name)


def serialize_attribute(obj):
    """
    This method recursively calls serialize_attribute on each
    attributes such as list,Tuple,Dict and checks for primitives
    as well to serialize the object.

    Parameters
    -----------
    obj: object
        The object to serialize.
    Returns
    --------
    obj
    """
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
        assert hasattr(obj, "serialize"), "Object must be serializable"
        return obj.serialize()


def deserialize_attribute(obj: Dict):
    """
    Receives deserializer from registry module.

    Parameters
    -----------
    obj: object
        Its a dictionary taken from the abstract common manager.
    Returns
    --------
    obj
    """
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
