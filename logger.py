

import functools
import logging

import inspect
from typing import Any, Callable, TypeVar, Union

import datetime
import os





# !!!!!!!!!!!!! Please read to a line of dashes, such as this one, before using the code !!!!!!!!!!!!! 
# ----------------------------------------------------------------------------------------------------------------------------



# How to use:

# import log_module

# Create your own logger and create a file handler
"""
logging.basicConfig(level=logging.DEBUG) # means all logs are logged. This it the least severe log level.
MY_LOGGER = logging.getLogger(__name__)

# Create a file handler
current_time = datetime.datetime.now()
log_file_name = f"log_{current_time.strftime('%Y-%m-%d_%H-%M-%S')}.log"
file_handler = logging.FileHandler(log_file_name)
file_handler.setLevel(logging.DEBUG)

# Create a formatter and set it for the file handler
formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
file_handler.setFormatter(formatter)

# Add the file handler to the logger
MY_LOGGER.addHandler(file_handler)

# Add a StreamHandler for stdout - if you want to keep the stdout logging
stream_handler = logging.StreamHandler()
stream_handler.setLevel(logging.DEBUG)  # You can set a different level for stdout
stream_handler.setFormatter(formatter)
MY_LOGGER.addHandler(stream_handler)
"""



# Add @log(passed_logger=YOUR_LOGGER) above functions you want to log.

# This will log the function name and its arguments when the function is called.

# It will check if the type hints match the passed parameters.
# If not, it logs a critical message.
# If ASSERT_TYPES == True, throw assertion error if types don't match.
ASSERT_TYPES = True

# In production, we don't want the logger to crash the program.
# If this is false, the assertion errors will go unnoticed.
LET_LOGGER_CRASH_PROGRAM = True

# These automatic logs all contain " @autolog " in their printout.




# Add log_locals(YOUR_LOGGER) above every return.
# This will log all local variables of the function at that point.
# log_locals() contains " @log_locals " in its printout instead.



# !!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!
# Important VS code regex trick:

# Since we need to add @log(our_logger) before every function, this is tedious.
# We can instead use Ctrl+F with regex.
# Find: ^( *)def
# Replace: $1@log(our_logger)\n$1def
# Do the same for log_locals() and return.

# Explanation:
# ^ means start of line,

# $k means the k-th capture group.
# A capture group is whatever is in parentheses ()





# Possibly add @log_for_class(passed_logger=YOUR_LOGGER) above your classes. This can:

# if ADD_CLASS_AUTOLOG == True
# - set @log decorator to all the class's methods. The problem is, it's not just your methods. It's also __init__ and other methods.
ADD_CLASS_AUTOLOG = True

# If ADD_AUTOMATIC_STR_METHOD == True
# - add a __str__ method to the class, which prints all its attributes.
ADD_AUTOMATIC_STR_METHOD = True
# This is important for logging, because when you have an object of such class in your code,
#  you want it to be logged with the attributes, not just the pointer to the object - that's useless.





# Above we described a scenario, where we pass a logger object to the decorator. 
# This code, however, supports 4 more options:
# 1. No logger is passed to the decorator. Here we create a default logger.

# 2. A logger class called MyLogger() is passed to the decorator.
# (Useful for teams collaborating on a project, so the logger created is always standardized.)
# MyLogger() is a class that has a method get_logger(name=None) that returns a logger.
# It is a toy class we used in this code. You can just go into this code and rename MyLogger() to your logger class. 

# Useful in some cases:
# 3. An actual logger OR a logger class called MyLogger() is passed as an argument to the decorated function.
# 4. An actual logger OR a logger class called MyLogger() is the classes attribute.



# ----------------------------------------------------------------------------------------------------------------------------


















# !!!!!!!!!!!!!
# Important VS code trick:
# Since we need to add @log(our_logger) before every function, this is tedious.
# We can instead use Ctrl+F with regex.
# Find: ^( *)def
# Replace: $1@log(our_logger)\n$1def
# Do the same for log_locals() and return.

# (Explanation:
# ^ means start of line,

# $k means the k-th capture group.
# A capture group is whatever is in parentheses ()
# $0 refers to the entire matched string.

# In the find part, we can use \k to refer to the k-th capture group,
#  meaning that group repeating exactly.     

# And there is a bunch more tricks. Ask ChatGPT.)





# This log_module:
# - Logs the function name and its arguments when the function is called.
# - Checks if its type hints are correct. Can crash program if ASSERT_TYPES is True and LET_LOGGER_CRASH_PROGRAM is True.
# - Enables simple logging for classes. Enables an automatic addition of __str__ method to classes.
# - Although simple logging for classes adds the logging for all methods called on it, like __init__ and other things as well,
# so adding @log to the methods in the class instead is a good idea.
# - Handles loggging shutdown upon SIGINT (ctrl-c interrupt)
# - Offers the function log_locals(logger), which logs all local variables of a function.  


# This is the logger that is used if no logger is passed to the decorator, like @log(my_own_logger).
# When logging, it is best to pass your logger of that file.
# # in theory you could also just change DEFAULT_LOGGER after importing. 

logging.basicConfig(level=logging.DEBUG) # means all logs are logges. This it the least severe log level.
DEFAULT_LOGGER = logging.getLogger(__name__)

# To create a log file, create a log handler.
# An example of this is done below in __main__.
# Do not forget to .close() the file handler after you are done with it.










# More functions can happen if SIGINT is received in Python. So we aren't overriding anything.
import signal
import sys

def sigint_handler(signum, frame):
    print("Received SIGINT. Closing logger...")
    logging.shutdown()
    sys.exit(0)

signal.signal(signal.SIGINT, sigint_handler)
# It performs an orderly shutdown of the logging system by flushing and closing all handlers, not loggers per se.





def log_locals(logger=DEFAULT_LOGGER):
    """
    Log all local variables in the current frame.
    
    :param logger: The logger to use (defaults to DEFAULT_LOGGER)
    """
    # Get the current frame (one level up from this function)
    frame = inspect.currentframe().f_back

    # This would also work. It's faster, but lower level.
    # And if I use inspect elsewhere, I'll use it here too.
    # frame = sys._getframe(1)


    # Get local variables from the frame
    local_vars = frame.f_locals

    # Get additional information from the frame
    full_path = frame.f_code.co_filename
    filename = os.path.basename(full_path)
    line_number = frame.f_lineno
    function_name = frame.f_code.co_name
    
    
    # Log each local variable
    logger.debug(f" @local_log Filename: {filename} Function: {function_name} Line: {line_number} Local variables: '{local_vars}'")
    
    # Break potential reference cycle 
    del frame













# This log_module covers 5 scenarios.

# 1. No logger is passed to the decorator.
# Here we create a default logger.

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






def log(_func=None, *, passed_logger: Union[MyLogger, logging.Logger] = None):
    def decorator_log(func):
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            logger = DEFAULT_LOGGER

            # This try is meant to not crash the code in production.
            # When using it for development, I would rather have it crash.
            # To do that, I would set LET_LOGGER_CRASH_PROGRAM to True.
            try:
                if passed_logger is None:

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
                    h_logger = next(iter(logger_params), DEFAULT_LOGGER)  # get the next/first/default logger
                
                else:
                    h_logger = passed_logger  # logger is passed explicitly to the decorator


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
                            assert param_type == type(arg_value), f"Type mismatch for parameter {param}. Expected {param_type}, got {type(arg_value)}"
                            # raise TypeError(f"Type mismatch for parameter {param}. Expected {param_type}, got {type(arg_value)}")



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



def log_for_class(_cls=None, *, passed_logger: Union[MyLogger, logging.Logger] = None):

    def decorator(cls):
        # Add automatic __str__ method if requested
        if ADD_AUTOMATIC_STR_METHOD:
            def auto_str(self):
                attrs = vars(self)
                return f"{cls.__name__}({', '.join(f'{key}={value}' for key, value in attrs.items())})"
            cls.__str__ = auto_str

        if ADD_CLASS_AUTOLOG:
            # Wrap each method with the log decorator
            for name, member in inspect.getmembers(cls):
                if inspect.isfunction(member):
                    setattr(cls, name, log(member, passed_logger=passed_logger))

        return cls
    

    if _cls is None:
        # This happens in the general use of the decorator.
        return decorator
    else:
        # This happens if you use the function not as a decorator, but as a function. e.g. log_for_class(MyClass)
        return decorator(_cls) 

# Older version of log_for_class.
# I think creating object from class decorated would this would have type(object) == WrapperClass.
# Maybe this could be solved with @functools.wraps(cls) in the WrapperClass.
# But I like the current solution.
"""
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
            # Below this is performed: cls.func_name = log(class.func_name)
            # Which is what is in the background of using @log above a function.
            setattr(WrapperClass, name, log(getattr(cls, name)))
    
    return WrapperClass
"""


if __name__ == "__main__":




    logging.basicConfig(level=logging.DEBUG) # means all logs are logged. This it the least severe log level.
    MY_LOGGER = logging.getLogger(__name__)

    # Create a file handler
    current_time = datetime.datetime.now()
    log_file_name = f"log_{current_time.strftime('%Y-%m-%d_%H-%M-%S')}.log"
    file_handler = logging.FileHandler(log_file_name)
    file_handler.setLevel(logging.DEBUG)

    # Create a formatter and set it for the file handler
    formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
    file_handler.setFormatter(formatter)

    # Add the file handler to the logger
    MY_LOGGER.addHandler(file_handler)

    # Add a StreamHandler for stdout - if you want to keep the stdout logging
    stream_handler = logging.StreamHandler()
    stream_handler.setLevel(logging.DEBUG)  # You can set a different level for stdout
    stream_handler.setFormatter(formatter)
    MY_LOGGER.addHandler(stream_handler)



    # Testing logger for class

    @log_for_class(passed_logger=MY_LOGGER)
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




    # Testing logger in a class without log_for_class

    class MyClass:
        def __init__(self, x: int, y: str):
            self.x = x
            self.y = y
        
        @log(passed_logger=MY_LOGGER)
        def add(self, z: int) -> int:
            return self.x + z
        
        @log(passed_logger=MY_LOGGER)
        def concat(self, s: str) -> str:
            return self.y + s
    
    obj = MyClass(5, "Hello")
    print(obj.add(3))
    print(obj.concat(" World"))
    print(obj)
    

    
    # actual logger is passed

    @log(passed_logger=MY_LOGGER)
    def sum(a, b=10):
        return a + b
    sum(10)

    
    
    # MY_LOGGER is passed as an argument to the decorated function
    @log
    def foo(a, b, logger):
        pass

    @log
    def bar(a, b=10, logger=None): # Named parameter
        pass

    foo(10, 20, MY_LOGGER)
    bar(10, b=20, logger=MY_LOGGER)




    # logger is the classes attribute

    class Foo:
        def __init__(self, logger):
            self.lg = MY_LOGGER

        @log
        def sum(self, a: int, b: int =10):
            hejhoj = 5
            log_locals(MY_LOGGER)
            return a + b

    Foo(MY_LOGGER).sum(10, b=20)



    inp = input("Enter 'c' to close file_handler. Anything else to continue.")

    if inp == "c":
        file_handler.close()


    inp = input("Enter 'c' to crash due to type mismatch. Anything else to continue.")

    if inp == "c":

        # Testing type assertion
        @log(passed_logger=MY_LOGGER)
        def sum(a: int, b=10):
            return a+b
        sum(1.25, 20)

    input("Press enter to continue.")























    input("Enter 'D' to test the default logger also:")


    # Testing DEFAULT_LOGGER:


    # Create a file handler
    current_time = datetime.datetime.now()
    log_file_name = f"log_{current_time.strftime('%Y-%m-%d_%H-%M-%S')}.log"
    file_handler = logging.FileHandler(log_file_name)
    file_handler.setLevel(logging.DEBUG)

    # Create a formatter and set it for the file handler
    formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
    file_handler.setFormatter(formatter)

    # Add the file handler to the logger
    DEFAULT_LOGGER.addHandler(file_handler)

    # Add a StreamHandler for stdout - if you want to keep the stdout logging
    stream_handler = logging.StreamHandler()
    stream_handler.setLevel(logging.DEBUG)  # You can set a different level for stdout
    stream_handler.setFormatter(formatter)
    DEFAULT_LOGGER.addHandler(stream_handler)



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

    @log(passed_logger=MyLogger())
    def sum(a, b=10):
        return a + b
    sum(10)

    
    # actual logger is passed

    lg = MyLogger().get_logger()

    @log(passed_logger=lg)
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
            log_locals(DEFAULT_LOGGER)
            return a + b

    Foo(MyLogger()).sum(10, b=20)  # OR Foo(MyLogger().get_logger()).sum(10, b=20)



    input("Enter 'c' to close file_handler. Anything else to continue (to the crash).")

    if input() == "c":
        file_handler.close()


    # Testing type assertion
    @log
    def sum(a: int, b=10):
        return a+b
    sum(1.25, 20)

    input()




