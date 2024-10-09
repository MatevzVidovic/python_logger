import functools
import inspect
import logging

logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

def log_locals(func):
    @functools.wraps(func)
    def wrapper(*args, **kwargs):
        result = func(*args, **kwargs)
        
        # Get the frame of the wrapped function
        frame = inspect.currentframe().f_back
        
        # Log local variables after execution
        logger.debug(f"Local variables of {func.__name__}: {frame.f_locals}")
        
        return result
    
    return wrapper

@log_locals
def example_function(x, y):
    z = x + y
    wikipedija = z * 2
    return wikipedija

result = example_function(2, 3)
print(result)