from typing import Dict, List, Tuple

from fedrec.serialization.serializable_interface import (Serializable,
                                                         is_primitives)
from fedrec.utilities.registry import Registrable


def get_deserializer(serialized_obj_name):
  """
  This function is used to check if the parameter passed 
  is present in the list of classes present in the memory
  during execution.
  
  Arguments
  ----------
  serialized_obj_name : str
  
  
  Returns
  ---------
  The value corresponding to that class name in the memory : str
  
 
  Raises
  ---------
  KeyError 
    If the class name is not found in the class map.
 
  """
    # find the deserializer from registry
    # given object name.
    return Registrable.lookup_class_ref(serialized_obj_name)


def serialize_attribute(obj):
    """
    This function is used to serialize an attribute
    over the obj parameter.
    
    
    Arguments
    ---------- 
    obj 
    
   
    Returns
    ----------
    Key-value pairs within the obj : dict
      If obj is a dictionary.
    
    Elements of obj : list or tuple
      If obj is list or tuple.
    
    obj : str, int, float or bool
      If obj is string, integer, float or boolean.
    
    obj.serialize() 
      If the object has an attribute named serialize.
     
    "Object must be serializable" : str
      If the object does not have an attribute named serialize.
    
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
    Arguments
    ---------- 
    obj : dict
   
    
    Returns
    ---------
    obj : dict
      If obj is a string, integer, float or boolean.
    
    The value corresponding to that class name in the memory : str
      If __type__ is in the dictionary obj, the type of the object is 
      called in the get_deserializable function.
    
    dictionary
      key 
        keys of obj.
      value 
        deserialize_attribute() is called recursively on each value in obj.
      If obj is a dictionary.
      
    list or tuple
      if obj is list or tuple, deserialize_attribute() is called recursively 
      on each attribute in obj.
      
    
    Raises
    ---------
    ValueError
      If none of the conditions are satisfied.
    
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
