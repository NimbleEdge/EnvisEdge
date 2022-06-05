from functools import wraps
from multiprocessing.sharedctypes import Value
import tracemalloc


def errorhandler(func):

    """
        Usage:
            This is a generic error handler decorator.
            To use this, just import it as :
                from fedrec.utilities.error_handler import errorhandler
            and add as decorator above the function.

        When To Use:
            Since this is generic error handler, it should only be used
            when you wish to handle the error silently i.e without
            causing the system to exit.
    
    """

    @wraps(func)
    def wrapper(*args, **kwargs):
        tracemalloc.start()

        try:
            return func(*args, **kwargs)

        
        except NotImplementedError as ner:
            print("NotImplementedError: ", ner)
            return None
        except ValueError as ver:
            print("ValueError: ", ver)
            return None
        except OSError as osr:
            print("OSError: ", osr)
            return None
        except ReferenceError as rfe:
            print("Reference Error: ", rfe)
            return None
        # Implement different Error/Exceptions as required.

        except Exception as e:
            print("Exception: ", e)
            return None
            
        tracemalloc.stop()
    
    return wrapper

"""
    Can be extended further as required.
"""

