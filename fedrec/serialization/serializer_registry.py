from typing import Dict, List, Tuple

from fedrec.serialization.serializable_interface import (Serializable,
                                                         is_primitives)
from fedrec.utilities.registry import Registrable


def get_deserializer(serialized_obj_name):
  """
  This function is used to check if the parameter passed 
  is present in the list of classes present in the memory
  during execution.
  -------------------------------------------------------
  If the class is not found in the class map, a KeyError is 
  thrown.
  Else, the value corresponding to that class in the memory
  is returned.
  
  """
    # find the deserializer from registry
    # given object name.
    return Registrable.lookup_class_ref(serialized_obj_name)


def serialize_attribute(obj):
    """
    This function is broadly used to serialize an attribute
    over the obj parameter.
    -------------------------------------------------------
    The if condition checks if obj is a Dictionary.
    If yes, it returns the key-value pairs within the dictionary
    obj using dictionary comprehension.
    Here, the for the value, the function is called recursively
    on each attribute.
    -------------------------------------------------------
    The first elif condition checks if the prarameter obj is 
    a List or Tuple. If the condition is satisfied, the serialize_attribute
    function is called recursively on each attribute in (List, Tuple).
    -------------------------------------------------------
    The second elif condition checks if the obj parameter is a string, integer, 
    float or boolean. If it is, the parameter is returned to the function as it is.
    -------------------------------------------------------
    The else statement first asserts if the object has an attribute named serialize,
    if it is so, it returns the value of obj.serialize(), else it returns the 
    statement, "Object must be serializable". 
    
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
    This function takes in the parameter obj which is of
    type Dictionary. 
    -----------------------------------------------------
    The if condition checks if obj contains a string, integer, float
    or boolean. If the condition is satisfied, it returns 
    the obj parameter.
    -----------------------------------------------------
    The first elif condition checks if __type__ is in the
    dictionary obj. If it is present, the type of the object is called 
    in the get_deserializable function which returns if the corresponding
    class is found in the class_map. The attribute of this class is deserialized
    on the data of obj.
    -----------------------------------------------------
    The second elif condition checks if obj is a Dictionary.
    If yes, it returns the key-value pairs within the dictionary
    obj using dictionary comprehension.
    Here, the for the value, the function is called recursively
    on each attribute.
    ------------------------------------------------------
    The third elif condition checks if the prarameter obj is 
    a List or Tuple. If the condition is satisfied, the deserialize_attribute
    function is called recursively on each attribute in (List, Tuple). 
    This has been done using dictionary comprehension.
    ------------------------------------------------------
    If none of these conditions are satisfied, a ValueError is thrown.
    
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
