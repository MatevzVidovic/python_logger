

import functools
import logging

import inspect
from typing import Any, Callable, TypeVar, Union

import datetime





# Logs the function name and its arguments when the function is called.
# Checks if its type hints are correct. Can crash program if ASSERT_TYPES is True and LET_LOGGER_CRASH_PROGRAM is True.
# Enables simple logging for classes. Enables an automatic addition of __str__ method to classes.
# Although simple logging for classes adds the logging for all methods called on it, like __init__ and other things as well,
# so adding @log to the methods in the class instead is a good idea.

# These automatic logs all contain " @autolog " in their printout.


ADD_AUTOMATIC_STR_METHOD = True  # Global variable to control automatic __str__ method addition to classes.

# In production, we don't want the logger to crash the program.
LET_LOGGER_CRASH_PROGRAM = True

ASSERT_TYPES = True  # Global variable to control type assertions




# This is the logger that is used if no logger is passed to the decorator, like @log(my_own_logger).
# When logging, it is best to pass your logger of that file.
# # in theory you could also just change DEFAULT_LOGGER after importing. 

logging.basicConfig(level=logging.DEBUG) # means all logs are logges. This it the least severe log level.
DEFAULT_LOGER = logging.getLogger(__name__)

# To create a log file, create a log handler.
# An example of this is done below in __main__.
# Do not forget to .close() the file handler after you are done with it.






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






# Initial idea:
"""
# Za logging decorator bi tako lahko ustvaril decorator, ki pred in po klicu funkcije izpiše njene lokalne spremenljivke (does not work).
# Lahko bi tudi avtomatsko preveril, če so parametri pravilnega tipa glede na type hints. Tako bi, če niso,
#  lahko naredil critical log, da niso bili. Lahko bi tudi imel glocalno spremenljivko ASSERT_TYPES=True,
#  in ob njej tudi assertal vse tipe, akr je fajn when developping.
# Najboljše je, da je te dekoratorje tako preprosto dodat: preprosto control F-aš def in ga nadomestiš z @nekaj\ndef.
# Lahko bi tudi naredil dekorator za classe, ki avtomatsko vsem njegovim metodam doda ta funkcijski decorator,
#  in ga tako pišeš samo nad definicijo classa.
# Ta class decorator bi lahko tudi avtomatsko ustvaril __str__ metodo, ki bi izpisala vrednosti vseh spremenljivk classa. 


# Logging local variables of a function does not work.
# You can only log wrapper() or module.
# This only makes sense, since in the decorateor, we are never in the function.
# Another logging mechanism has to be created for that.
"""












# This logger is adapted from https://ankitbko.github.io/blog/2021/04/logging-in-python/

# It loggs the function name and its arguments when the function is called.
# It also logs the exception raised in the function, if any.


# It covers options of passing a logger to the decorator, passing a logger to the decorated function,
# or having a logger in the method's class's attributes.

# It also covers the case of passing a logger generating class, here named MyLogger(),
# but could be anything your project uses - just rename MyLogger in this code.

# If no logger is passed, it uses the default logger.










class MyLogger:
    def __init__(self):
        logging.basicConfig(level=logging.DEBUG)

    def get_logger(self, name=None):
        return logging.getLogger(name)

# Was used before in place of DEFAULT LOGGER 
# def get_default_logger():
#     return MyLogger().get_logger()






def log(_func=None, *, my_logger: Union[MyLogger, logging.Logger] = None):
    def decorator_log(func):
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            logger = DEFAULT_LOGER

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
                    # Otherwise logger_params is empty and BASIC_LOGGER is used.
                    h_logger = next(iter(logger_params), DEFAULT_LOGER)  # get the next/first/default logger
                
                else:
                    h_logger = my_logger  # logger is passed explicitly to the decorator


                # We allowed MyLogger() to be passed as a logger.
                # If it was, we need to get its actual logger here.
                if isinstance(h_logger, MyLogger):
                    logger = h_logger.get_logger(func.__name__)
                else:
                    logger = h_logger





                # Now comes what we do with the logger before function call:

                signature = inspect.signature(func)
                bound_args = signature.bind(*args, **kwargs)
                bound_args.apply_defaults()

                # Log function call
                printable_args = [f"{k}={v!r}" for k, v in bound_args.arguments.items()]
                logger.debug(f" @autolog Function {func.__name__} called with arguments: {', '.join(printable_args)}")

                # Initial weird way
                """
                print(signature)
                print(args, kwargs)
                print(bound_args.arguments)
                
                # Log function call
                args_repr = [repr(arg) for arg in args]
                kwargs_repr = [f"{k}={v!r}" for k, v in kwargs.items()]
                logger.debug(f"Function {func.__name__} called with arguments: {', '.join(args_repr + kwargs_repr)}")
                """
                

                # Type checking
                for param, arg_value in bound_args.arguments.items():
                    param_type = signature.parameters[param].annotation
                    if param_type != inspect.Parameter.empty and not isinstance(arg_value, param_type):
                        logger.critical(f" @autolog Type mismatch for parameter '{param}'. Expected {param_type}, got {type(arg_value)}")
                        if ASSERT_TYPES:
                            raise TypeError(f"Type mismatch for parameter {param}. Expected {param_type}, got {type(arg_value)}")



            except Exception as e:
                if LET_LOGGER_CRASH_PROGRAM:
                    raise e


            try:
                result = func(*args, **kwargs)
                return result
            except Exception as e:
                logger.exception(f" @autolog Exception raised in {func.__name__}. exception: {str(e)}")
                raise e
        return wrapper

    if _func is None:
        return decorator_log
    else:
        return decorator_log(_func)


def log_for_class(cls):
    class WrapperClass(cls):
        def __init__(self, *args, **kwargs):
            super().__init__(*args, **kwargs)
        
        if ADD_AUTOMATIC_STR_METHOD:
            def __str__(self):
                attrs = vars(self)
                return f"{cls.__name__}({', '.join(f'{key}={value}' for key, value in attrs.items())})"
    
    for name, member in inspect.getmembers(cls):
        if inspect.isfunction(member):
            setattr(WrapperClass, name, log(getattr(cls, name)))
    
    return WrapperClass



if __name__ == "__main__":


    # Create a file handler
    current_time = datetime.datetime.now()
    log_file_name = f"log_{current_time.strftime('%Y-%m-%d_%H-%M-%S')}.log"
    file_handler = logging.FileHandler(log_file_name)
    file_handler.setLevel(logging.DEBUG)

    # Create a formatter and set it for the file handler
    formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
    file_handler.setFormatter(formatter)

    # Add the file handler to the logger
    DEFAULT_LOGER.addHandler(file_handler)

    # Add a StreamHandler for stdout - if you want to keep the stdout logging
    stream_handler = logging.StreamHandler()
    stream_handler.setLevel(logging.DEBUG)  # You can set a different level for stdout
    stream_handler.setFormatter(formatter)
    DEFAULT_LOGER.addHandler(stream_handler)



    # Testing logger for class

    @log_for_class
    class MyClass:
        def __init__(self, x: int, y: str):
            self.x = x
            self.y = y
        
        def add(self, z: int) -> int:
            return self.x + z
        
        def concat(self, s: str) -> str:
            return self.y + s
    
    obj = MyClass(5, "Hello")
    print(obj.add(3))
    print(obj.concat(" World"))
    print(obj)
    



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
        def sum(self, a: int, b: int =10):
            hejhoj = 5
            return a + b

    Foo(MyLogger()).sum(10, b=20)  # OR Foo(MyLogger().get_logger()).sum(10, b=20)





    file_handler.close()


    # Testing type assertion
    @log
    def sum(a: int, b=10):
        return a+b
    sum(1.25, 20)

    input()




