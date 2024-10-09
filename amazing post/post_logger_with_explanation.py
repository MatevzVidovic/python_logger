

from typing import Union

import functools
import logging

LET_LOGGER_CRASH_PROGRAM = False

logging.basicConfig(level = logging.DEBUG)
# logger = logging.getLogger()

class MyLogger:
    def __init__(self):
        logging.basicConfig(level=logging.DEBUG)

    def get_logger(self, name=None):
        return logging.getLogger(name)

def get_default_logger():
    return MyLogger().get_logger()



# This logger covers 5 scenarios.

# 1. No logger is passed to the decorator.
# Here we create a MyLogger() class.

# 2. A logger class called MyLogger() is passed to the decorator.
# 3. An actual logger is passed to the decorator.
# Here we simply use what was passed.

# 4. An actual logger OR a logger class called MyLogger() is passed as an argument to the decorated function.
# 5. An actual logger OR a logger class called MyLogger() is the classes attribute.
# Here we use what was passed to the decorated function as a parameter first,
# and if it wasn't, we look for any such thing in the class's attributes,
# and if nothing is there, we do the 1. case and create MyLogger().


def log(_func=None, *, my_logger: Union[MyLogger, logging.Logger] = None):
    def decorator_log(func):
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            logger = get_default_logger()

            # This try is meant to not crash the code in production.
            # When using it for development, I would rather have it crash.
            # To do that, I would set LET_LOGGER_CRASH_PROGRAM to True.
            try:
                if my_logger is None:

                    # This tries to see it the logger was passed as an argument.
                    first_args = next(iter(args), None)  # capture first arg to check for `self`
                    logger_params = [  # does kwargs have any logger
                        x
                        for x in kwargs.values()
                        if isinstance(x, logging.Logger) or isinstance(x, MyLogger)
                    ] + [  # # does args have any logger
                        x
                        for x in args
                        if isinstance(x, logging.Logger) or isinstance(x, MyLogger)
                    ]

                    # This tries to see if this is a method in a class that has a logger attribute.
                    if hasattr(first_args, "__dict__"):  # is first argument `self`
                        logger_params = logger_params + [
                            x
                            for x in first_args.__dict__.values()  # does class (dict) members have any logger
                            if isinstance(x, logging.Logger)
                            or isinstance(x, MyLogger)
                        ]
                    

                    # Here we make our own logger if no logger was passed.
                    # logger_params is a list of loggers.
                    # If the function has a logger in its arguments, it will be used, because it is first in this list.
                    # If not and the class has a logger, it will be used.
                    # Otherwise logger_params is empty and out own MyLogger() is used.
                    h_logger = next(iter(logger_params), MyLogger())  # get the next/first/default logger
                
                else:
                    h_logger = my_logger  # logger is passed explicitly to the decorator


                # We allowed MyLogger() to be passed as a logger.
                # If it was, we need to get its actual logger here.
                if isinstance(h_logger, MyLogger):
                    logger = h_logger.get_logger(func.__name__)
                else:
                    logger = h_logger





                # Now comes what we do with the logger:

                args_repr = [repr(a) for a in args]
                kwargs_repr = [f"{k}={v!r}" for k, v in kwargs.items()]
                signature = ", ".join(args_repr + kwargs_repr)
                logger.debug(f"function {func.__name__} called with args {signature}")
            except Exception:
                if LET_LOGGER_CRASH_PROGRAM:
                    pass
                else:
                    raise Exception("Logger crashed the program.")


            try:
                result = func(*args, **kwargs)
                return result
            except Exception as e:
                logger.exception(f"Exception raised in {func.__name__}. exception: {str(e)}")
                raise e
        return wrapper

    if _func is None:
        return decorator_log
    else:
        return decorator_log(_func)




if __name__ == "__main__":
    


    # no logger is passed

    @log
    def sum(a, b=10):
        return a+b
    sum(10, 20)



    # logger class is passed

    @log(my_logger=MyLogger())
    def sum(a, b=10):
        return a + b
    sum(10)

    
    # actual logger is passed

    lg = MyLogger().get_logger()

    @log(my_logger=lg)
    def sum(a, b=10):
        return a + b
    sum(10)

    
    
    # logger is passed as an argument to the decorated function
    @log
    def foo(a, b, logger):
        pass

    @log
    def bar(a, b=10, logger=None): # Named parameter
        pass

    foo(10, 20, MyLogger())  # OR foo(10, 20, MyLogger().get_logger())
    bar(10, b=20, logger=MyLogger())  # OR bar(10, b=20, logger=MyLogger().get_logger())




    # logger is the classes attribute

    class Foo:
        def __init__(self, logger):
            self.lg = logger

        @log
        def sum(self, a, b=10):
            return a + b

    Foo(MyLogger()).sum(10, b=20)  # OR Foo(MyLogger().get_logger()).sum(10, b=20)
