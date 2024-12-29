

import functools
import logging


from typing import Union





DEFAULT_LOGGER = logging.getLogger(__name__)
DEFAULT_LOGGER.setLevel(logging.DEBUG)



def file_handler_setup(logger, path_to_python_logger_folder, add_stdout_stream: bool = False):
    return


def log_locals(passed_logger=DEFAULT_LOGGER, list_with_limiting_number=[], check_attributes=True, attr_sets=["size"], added_attribute_names=[]):
    return


def log_stack(passed_logger=DEFAULT_LOGGER, check_attributes=True, attr_sets=["size"], added_attribute_names=[]):
    return


def log_manual(passed_logger=DEFAULT_LOGGER, *args, **kwargs):
    return


def log_time(passed_logger=DEFAULT_LOGGER, immutable_id=""):
    return






class MyLogger:
    def __init__(self):
        logging.basicConfig(level=logging.DEBUG)

    def get_logger(self, name=None):
        return logging.getLogger(name)




def autolog(_func=None, *, passed_logger: Union[MyLogger, logging.Logger] = None, assert_types=True, let_logger_crash_program=True, log_stack_on_exception=False):
    def decorator_log(func):
        @functools.wraps(func)


        def wrapper(*args, **kwargs):    
            result = func(*args, **kwargs)
            return result
        
        return wrapper

    if _func is None:
        return decorator_log
    else:
        return decorator_log(_func)



def log_for_class(_cls=None, *, passed_logger: Union[MyLogger, logging.Logger] = None, add_automatic_str_method=True, add_automatic_repr_method=True, add_class_autolog=True):

    def decorator(cls):
        return cls
    

    if _cls is None:
        # This happens in the general use of the decorator.
        return decorator
    else:
        # This happens if you use the function not as a decorator, but as a function. e.g. log_for_class(MyClass)
        return decorator(_cls) 
