

import functools
import logging

import inspect
import logging.handlers
from typing import Any, Callable, TypeVar, Union

import random

import datetime
import os

import time




# !!!!!!!!!!!!! Please read the Main info !!!!!!!!!!!!!


# TL;DR:
"""

This code helps you log your code with minimal effort.
Above a function definition, you just add:
@py_log.autolog(passed_logger=MY_LOGGER)
def foo(a: int, b, c: float): ...
This does:
- automatic logging that the function was called and the arguments it was called with
- checking the correctness of type hints of the passed arguments (was the passed c really a float?)
- logging the amount of time that the function needed in its execution
Also:
- logging of local variables (all vars defined in this func) at any point in the code (just write py_log.log_locals(MY_LOGGER))
- logging of all local variables in the entire stack trace (py_log.log_stack(MY_LOGGER))
- logging of time since the last log_time call with a certain immutable_id (py_log.log_time(MY_LOGGER, immutable_id="some string you like"))
- logging of whatever you want (py_log.log_manual(MY_LOGGER, "rocni string", vrba, vrbica_moja=vrba))
- and some other stuff too.
And most importantly:
- you can view all these logs in a nice frontend that is easy to filter.
"""

# Main info:
"""
SETUP:

Add this repo as a submodule:
(I suggest you instead add your fork of the repo)
git submodule add https://github.com/MatevzVidovic/python_logger.git
git commit -m "Add python_logger as a submodule"

When cloning your repo, use:
git clone --recurse-submodules [URL]
This will mean the submodule (python_logger) is cloned as well.

When pulling, use:
git pull --recurse-submodules


To view the latest log_file that has been created do:
cd python_logger
python3 server.py
Make new terminal tab
cd python_logger/log_frontend
npm run dev
And open the localhost that is shown in the terminal in your browser.

You might need to pip3 install flask and flask_cors.
For the frontend, you might need to install node and npm.
Then you might need to install vite (npm install vite --save-dev).
And then your node version might be too old or something, so you need to update nvm or sth,
idk, I just coppied what chatGPT gave when I gave it the error message and it worked.

Sometimes you need to ctrl+C server.py and then run it again.
If logs aren't working, this is the first thing to try.


I suggest you fork the python_logger repo and then add your fork as a submodule instead.
This will allow you to change the python_logger code (like the global variables or some small additions).
It's important you fork so that you can then push and your main repo remembers that you are using the new commit.

If you go change the submodule code:
When doing git add . in your main repo, the code changes in your submodule are never included.
All that your main repo has, is a file that says which commit of the submodule is the right one.
If you want to push the changes of the code in the submodule, you go to the submodule folder in the terminal,
and then commit and push from there. This will commit to the python_logger repo.
And then the main repo changes the file that tracks which submodule commit is the right one.
That file change needs to be commited like any other.






CODE SETUP:

In your main file, above all imports at the top of the file, add this code:
(above all imports so that file_handler_setup() is done before any 
code from importing your other files is run - so all the loggings 
are actually written to the output file.)
{
import logging
import python_logger.log_helper_off as py_log
import python_logger.log_helper as py_log_always_on

MY_LOGGER = logging.getLogger("prototip") # or any string. Mind this: same string, same logger.
MY_LOGGER.setLevel(logging.DEBUG)

py_log_always_on.limitations_setup(max_file_size_bytes=100 * 1024 * 1024)
handlers = py_log_always_on.file_handler_setup(MY_LOGGER)

}
(Quickly on limitations_setup(): 
max_file_size_bytes is the maximum size of the log file in bytes.
After it is reached, the file is backed up and a new log file starts to be written to.
Param backup_num is 1 by default, so only the latest backup is kept. (works like RotatintFileHandler in logging module).
But we made it so that the first backup we make is always saved (it's the one where the program started and probably contains very important logs).
We also have param max_chars_in_one_var if you want to slice long logs which are usually pointless anyways.
And we also have var_blacklist - a list of variable names that will not be logged. This is useful to prevent annoying long logs that keep being logged but aren't useful at all.




In all the other files you are importing, add this code without the file_handler_setup() part:
{
import logging
import python_logger.log_helper_off as py_log
import python_logger.log_helper as py_log_always_on

MY_LOGGER = logging.getLogger("prototip")
MY_LOGGER.setLevel(logging.DEBUG)
}
(In theory adding more file handlers would lead to logs being duplicated.
Although our code is set up so that this doesn't happen even if you mess up.)





IF YOU WANT TO STOP LOGGING:

If you want the logging to stop, you can:
- simply comment out the 2 file_handler_setup lines in your main file.
(the logging is still happening and wasting CPU time, it just isn't written to anywhere)
- You change the line import python_logger.log_helper
to: import python_logger.log_helper_off
in all files where you use this import. Now the logging functions, including file_handler_setup,
 are all empty functions that just return, write nothing anywhere, waste no resources.
(If you don't mind wasting CPU time, all you care about is the log files to not be written,
you can make this _off change in just the file/files where you call file_handler_setup() (same as commenting out the lines).)





USE:

(This is outdated, so do not use it right now.)
Go play with the following repo to get example uses and how they work: https://github.com/MatevzVidovic/pylog_tester.git
It will be easier than just reading this text (although, do that too).
Especially go look for the use of what log_stack returns. 
It could come in really handy in debugging with vizualizations.

(Also outdated. But still, maybe it helps a little bit to get an image of how to use this stuff.)
There is an if __name__ == "__main__": bellow with examples also.





AUTOLOG:

# Add @py_log.autolog(passed_logger=MY_LOGGER) above functions you want to log.
@py_log.autolog(passed_logger=MY_LOGGER)
def foo(a, b, c):
    pass

These automatic logs all contain " @autolog " in their printout.

This logs the function name and its arguments when the function is called.
It checks if the type hints match the passed parameters.

!!! Important !!!
You have your module (file) ConvResourceCalc, which has a class ConvResourceCalc.
You do:
import ConvResourceCalc
in some file. Well, then when you typehint for ConvResourceCalc, you are typehinting for the module, not the class.
And you will get this error:
if param_type != inspect.Parameter.empty and not isinstance(arg_value, param_type):
TypeError: isinstance() arg 2 must be a type, a tuple of types, or a union
So instead, you have to do:
from ConvResourceCalc import ConvResourceCalc

If the types don't match (assertion error), or some other exception happens in logger (possibly due to a bug),
it will crash the code.

You can disable both these behaviours by calling the decorator like so:
@py_log.autolog(passed_logger=MY_LOGGER, assert_types=False, let_logger_crash_program=False)

We also log the time of execution of the function.
However, to time the function, we have to run it first. But we want @autolog to happen right before the
function happens - so we can't put the time in the same log.
For this reason, we created @time_autolog logs.
These logs contain " @time_autolog " in its printout.
These happen right after the function finished.

We also want to log what the function returned. We can't put that in the @autolog log, because the function hasn't run yet.
(And if we were to wait with the autolog until we get the retur, then the autologs wouldn't be in the order of callings of fns, 
but in the order of returns of fns, which is confusing.)
So we put it into the @time_autolog log, which is another nice thing about it.

In a way this is nice, because then in your logs you have a nice encapsulation of the function - the start and the end logs are clear.
It is however less clear for functions that call themselves, because in the logs between the main @autolog and @time_autolog, we have the same encapsulation.
For this reason we add a random number to both the @autolog and @time_autolog logs, so we can actually know which @time_autolog belongs to which @autolog.

If these logs bug you, just regex them away in the log viewer.

See more in TIMING YOUR CODE.







LOG_LOCALS:

Add py_log.log_locals(MY_LOGGER) somewhere in the code.
It will print all the local variables at that point (function scope variables).
Possibly add this above every return.
These logs contain " @log_locals " in its printout.




OBJECT ATTRIBUTE LOGGING:

You are debugging some numpy code. A local variable is a numpy array. It gets logged.
You don't see anything from that log - it's just a cropped printout of the array.
You don't know the shape, the mean, the std, the min, the max, the sum, ...
We can fix that.

E.g. default paramters of log_locals are:
py_log.log_locals(passed_logger=DEFAULT_LOGGER, list_with_limiting_number=[], check_attributes=True, attr_sets=["size"], added_attribute_names=[])
The last three parameters work like so:
if check_attributes=True, you can pass, for example: added_attribute_names=["shape", "mean"].
For each local variable, we will check if it has the attributes shape and mean.
E.g. for shape, that means either .shape() or .shape.
If it has .shape(), we will log its result. If it doesn't, but it has .shape, we will log that.

There are also two predefined attribute sets: "size" and "math".
"size" checks for shape, size, dtype, __len__. O(1) operations.
"math" checks for mean, std, min, max, sum. O(n) operations.

We also have "hist" as an option in attr_sets. (O(n) operation)
(This is not really an attribute set, but it fits here nicely enough, and it's really useful.)
If the val is a np.array or torch.Tensor, we make a count of unique values.
If there are 10 or less unique values, we log them with their counts.
If there are more, we log the min and its count, max and its count, 
and the counts in 10 equal intervals between min and max (the histogram).

You can pass these set names in a list to attr_sets.
By default, this is only ["size"], because math operations take longer to compute.

These three parameters can be used in .log, .log_locals, .log_stack.
Everywhere they are check_attributes=True, attr_sets=["size"], added_attribute_names=[] by default.

They also apply in log_manual. But there, they can't be regular parameters, 
because log_manual wants all the arguments passed as *args and **kwargs.
So to set them, you have to pass them as kwargs:
py_log.log_manual(MY_LOGGER, "rocni string", vrba, vrbica_moja=vrba, check_attributes=True, attr_sets=["size"], added_attribute_names=[])
In log_manual, the default values are:
check_attributes=True, attr_sets=attr_sets=["size", "math", "hist"], added_attribute_names=[].
Because manual logs don't happen much and it sort of makes sense to give you all the info you can get by default.



LOG_MANUAL:

Use py_log.log_manual(MY_LOGGER, *args, **kwargs) to log whatever you want.
You just give anything as arguments and keyword arguments and it will log them.
These logs contain " @log_manual " in its printout.

I suggest using kwargs for better readability - manual log will log 
what keyword you used for the argument, so you can easily be sure what is what in the log.

Possibly use your own @something_something as arguments in your manual logs.
This will allow you to use the regex aspect of the log viewer to filter out only certain manual logs.

Example:
py_log.log_manual(MY_LOGGER, "rocni string", vrba, vrbica_moja=vrba)
(vrba was a variable in that scope)



LOG_STACK:

Use py_log.log_stack(MY_LOGGER) anywhere in the code to log the local vars in the entire stack trace.
These logs contain " @log_stack " in its printout.

py_log.log_stack also returns a list of info dicts, which contain the filename, function name, local vars dict, ...
list_of_info_dicts = py_log.log_stack(MY_LOGGER)
This list can then be used to find the local variables of a function that is not in the current scope. 
This is very useful in except blocks, where you might want to use vizualization functions you imported to this file,
and use them on your objects that are out of scope in this except block.
This except block might be in a func in a class in a file that gets imported by the main file.
And still through this we can get access to an object that is a global var in the main file.

The same Object attribute logging as in log_locals can be used in log_stack.

Suggestion:
Put the entire code of a function in a try block. In the except block, log_stack.
This way, you get the image of the local variables at the time of the exception.
try:
    all_of_function_code
except Exception as e:
    py_log.log_stack(MY_LOGGER)
    raise e




TIMING YOUR CODE:

All loggings of time use time.perf_counter() to measure time.
This means they measure wall-clock time, not CPU time - so if you have sleep() in your code, it will affect the time.
An alternative is time.process_time(). It measures only CPU time, not wall-clock time - so it's not affected by time.sleep().
To change it, change the CURR_TIME_FUNC global variable to time.process_time.

LOG_TIME:
Use py_log.log_time(MY_LOGGER, immutable_id="") to log the time since the last log_time call with that immutable_id.
As immutable_id you can pass any immutable type - like a string, a number, a tuple, ...
These logs contain " @log_time " in its printout.


Most useful way of logging time:
if LOG_TIME_AUTOLOG == True, in autologging with .autolog() we log the time of execution of the decorated function.
In an individual call of .autolog() you can disable the time logging by setting time_log=False.






ENABLING OF LAZINESS:

If you are lazy and don't care about clutter of logs, you can do a find and replace
to add the loggings to all your functions.
(This regex will still duplicate the loggings, so add them one by one in teh find and replace.)
{
To do this easily in VS code, use regex:

^(?!.*@autolog\n)( *)def
Find: ^( *)def
Replace: $1@py_log.autolog(passed_logger=MY_LOGGER)\n$1def

and

Find: ^( *)return
Replace: $1log_locals(passed_logger=MY_LOGGER)\n$1return
}





USING LOG VIEWER REGEX:

You can use the regex bar to filter the logs.
Example usage: You write " @autolog " in the input field.
The button beside the field says contain.
You click Add Regex.
You then click Send Current Regex.
Then you click on Refresh Logs.

The new logs should be only the ones, which contain " @autolog " somewhere in their text.

You could also have toggled the contain button to not-contain.
Then the logs that remained in the view would be only those that 
do not contain " @autolog " anywhere in their text.

You can use more than one regex contain/not-contain at a time.
All the conditions must hold for a log to be kept in view.

And you can use actual regex in the input field, not just basic words, 
although mostly you just use basic words to filter to what you are interested in.




USING SERVER_PY:

If you just do:
python3 server.py
You can view the latest log file that was created.
You can also manually pass the name of the logfile in /logs/ to view that log file.

You can do:
python3 server.py log_57-44-22_2024-11-15.log
or
python3 server.py logs/log_57-44-22_2024-11-15.log

I suggest the second way, so that you can use autocomplete.

If you are choosing the logs manually, I suggest that when it seems appropriate,
you delete the folder /logs.
This is perfectly fine, it will be created anew.
And you will have less clutter and will be able to find the log you are interested in more easily.

Tip - run:
python3 server.py logs/log_
It won't work, but then you can just arrow-up, and add the number and tab.


"""



# Expanded main info (after you have used the code a bit, I suggest you read this):
"""

AUTOLOG WITH OTHER DECORATORS:
I suspect always soing the autolog decorator last works.
In this case, doing the @staticmethod after .autolog() caused an error:
@staticmethod
@py_log.autolog(passed_logger=MY_LOGGER)
def fn():
    pass

BETTER CODE SETUP:

Sometimes you want to run the program for a short small problem, and you want all the available logging there.
Sometimes you don't want certain clutter in your logs, so you want to disable some files from logging.
Sometimes you want to run the program for a long time, and the log files would be way too huge.

Either way, you keep going around your files and changing 
import python_logger.log_helper as py_log 
to 
import python_logger.log_helper_off as py_log
and vice versa. And it's annoying.
So we make a txt file: active_logging_config.txt like:
logging_config.yaml
And you make logging_config.yaml like:
unet_original_main.py : True
training_support.py : True
training_wrapper.py : True
model_wrapper.py : True
pruner.py : True

And in this way you specify which files should log and which shouldn't. And you can have
logging_config.yaml, 1_logging_config.yaml, 2_logging_config.yaml, ... and just change the active_logging_config.txt

And so tha active_logging_config.txt and k_logging_config.yaml, ..., don't pollute your repo,
you put them into a folder "pylog_configs". And its also easier to gitignore this way.


Main file:
{

import logging
import yaml
import os.path as osp
import python_logger.log_helper as py_log_always_on

with open(f"{osp.join('pylog_configs', 'active_logging_config.txt')}", 'r') as f:
    cfg_name = f.read()
    yaml_path = osp.join('pylog_configs', cfg_name)

log_config_path = osp.join(yaml_path)
do_log = False
if osp.exists(yaml_path):
    with open(yaml_path, 'r') as stream:
        config = yaml.safe_load(stream)
        file_log_setting = config.get(osp.basename(__file__), False)
        if file_log_setting:
            do_log = True

print(f"{osp.basename(__file__)} do_log: {do_log}")
if do_log:
    import python_logger.log_helper as py_log
else:
    import python_logger.log_helper_off as py_log

MY_LOGGER = logging.getLogger("prototip") # or any string. Mind this: same string, same logger.
MY_LOGGER.setLevel(logging.DEBUG)

py_log_always_on.limitations_setup(max_file_size_bytes=100 * 1024 * 1024, var_blacklist=["tree_ix_2_module", "mask_path"])
handlers = py_log_always_on.file_handler_setup(MY_LOGGER)


}

Other files: (just last three lines not used)
{

import logging
import yaml
import os.path as osp
import python_logger.log_helper as py_log_always_on

with open(f"{osp.join('pylog_configs', 'active_logging_config.txt')}", 'r') as f:
    cfg_name = f.read()
    yaml_path = osp.join('pylog_configs', cfg_name)

log_config_path = osp.join(yaml_path)
do_log = False
if osp.exists(yaml_path):
    with open(yaml_path, 'r') as stream:
        config = yaml.safe_load(stream)
        file_log_setting = config.get(osp.basename(__file__), False)
        if file_log_setting:
            do_log = True

print(f"{osp.basename(__file__)} do_log: {do_log}")
if do_log:
    import python_logger.log_helper as py_log
else:
    import python_logger.log_helper_off as py_log

MY_LOGGER = logging.getLogger("prototip") # or any string. Mind this: same string, same logger.
MY_LOGGER.setLevel(logging.DEBUG)



}




LOG_FOR_CLASS:

You can also put
@py_log.log_for_class(passed_logger=MY_LOGGER)
above a class definition.

This does 3 things. They can all be disabled if you call this like so:
@py_log.log_for_class(passed_logger=MY_LOGGER, add_automatic_str_method=False, add_automatic_repr_method=False, add_class_autolog=False)

If add_class_autolog = True,
this will set @py_log.autolog(passed_logger=MY_LOGGER) to all the class's methods.

This seems nice at first, but it also sets the logging to __init__ 
and other methods python includes by default. And you don't want that.
Also, having log for all methods is too much clutter anyway.

If add_automatic_str_method = True,
it also adds a __str__ method to the class, which prints all its attributes.
This is nice if you want to print the object in your code.

Most importantly:

If add_automatic_repr_method = True,
it also adds a __repr__ method to the class, which prints all the objects attributes.
This is important, because when this class is logged, __repr__ is called.
So without it, you will only get the pointer to the object in your log.

When we do logging, we are always calling __repr__ of our attributes (by using {v!r}.
This is a general python magic method, which gives a comprehensive string representation of the object 
(unlike __str__, which is meant to be more user friendly).

"""





# Advice on use (Maybe a bit stupid - read only after you have used the code a bit):
"""




LOG LOCALS SUGGESTION:

When debugging you want to print what you have changed after every line of your code.
You need to make each print with an f-string so you can even read the output.
So you have to write a unique f-string for each printout (github copilot helps, but still painfull).
And even then you look at the printout and it's hard to make out what text came from exactly which printout,
because you kept changing the same variable name a bunnch, so all prints were like: print(f"Variable a: {a}").

Maybe just use log_locals everywhere.
Its the same line every time, so you can just keep pasting it.
And deleting it is simply find and replace.
It's nice and easy.
You then just:
- have code in your left part of the screen, 
- log frontend on the right, 
- you use regex for " @log_locals ", possibly for "Function {func_name}", 
- and then you just look at the variables you are interested in by line number.
And even if it clutters code a bit, it's still less clutter and much easier and nicer 
than coming up with relevant printouts, and printing out everything after every change, 
and making the printouts f-strings saying what is currently being printed out so you can even interpret the printouts.

(Lesser suggestion below in the text - search for "Lesser suggestion")




NUMPY ARRAY LOGGING SUGGESTION:

Some arrays have useless values at the edges. You want to see the middle of the array.
But the printout cuts it off. Even repr(arr) cuts it off.

You can use:
with np.printoptions(threshold=np.inf):
    py_log.log_manual(arr)   # or log_locals or log_stack

Mind that this took my program 10 seconds for 4 1024x1024x3 imgs.
So COMMENT IT OUT IN PROD!!!




VIZUALIZABLE DUBUGGING SUGGESTION (like images, graphs, neural net compute graphs, ...):

When working with things that can be visualized, like images, have a general non-blocking vizualization function.
Example:
{
SHOW_IMAGE_IX = [0]
def show_image(img, title=""):
    plt.figure()
    plt.imshow(img, cmap='gray')
    plt.title(f"{title} ({SHOW_IMAGE_IX[0]})")
    SHOW_IMAGE_IX[0] += 1
    plt.axis('off')
    plt.show(block=False)
    plt.pause(0.001)
}

Then, instead of just doing log_locals(), do:
py_log.log_locals(MY_LOGGER, attr_sets=["size", "math"]); show_image(img)
Python makes it so that the semicolon is as if there was a newline and correct indentation.
So this line is very easy to add everywhere (just paste everywhere and you don't have the indentation problems like you do when you are pasting newlines.
And it is also very easy to delete (just find and replace with nothingness).


Better img showing function:
- You can show multiple images at once in one figure by passing a list of them.
- You can also pass a list of tuples with the image and the subtitle.
- The figure name will show the line number and the function name where the function was called from.
- You have close_all_limit parameter, which closes all figures if there are more figures than that open.
(If single_threaded program, you can put an input() in that if so you have time to view them before they close.)
{
SHOW_IMAGE_IX = [0]
def show_image(passed_img, title="", close_all_limit=1e9):

    # passed_img can be np.ndarray, Image.Image, or torch.Tensor
    # If passed_img is a list, it will show all images in the list on one plot.
    # passed_img as a list can also have tuples with titles: e.g. [(img1, title1), (img2, title2]

    # Close all open figures
    figure_numbers = plt.get_fignums()
    if len(figure_numbers) >= close_all_limit:
        plt.close('all')


    if not isinstance(passed_img, list):
        passed_img = [passed_img]


    imgs = passed_img

    # determine rown and columns:
    if len(imgs) == 1:
        rc = (1,1)
    elif len(imgs) == 2:
        rc = (1,2)
    elif len(imgs) <= 4:
        rc = (2,2)
    elif len(imgs) <= 6:
        rc = (2,3)
    elif len(imgs) <= 9:
        rc = (3,3)
    else:
        cols = len(imgs) // 3 + 1
        rc = (3, cols)
    
    fig, axes = plt.subplots(rc[0], rc[1])

    # when rc = (1,1), axes is not a np.array of many axes, but a single Axes object. And then flatten doesn't work, and iteration doesn't work.
    # It's just easier to make it into a np.array.
    if isinstance(axes, plt.Axes):
        axes = np.array([axes])

    # Flatten the axes array for easy iteration
    axes = axes.flatten()

    # Iterate over images and axesk
    for i, ax in enumerate(axes):
        if i < len(imgs):

            curr_img = imgs[i][0] if isinstance(imgs[i], tuple) else imgs[i]
            curr_title = imgs[i][1] if isinstance(imgs[i], tuple) else title


            try:
                # this clones the image anyway
                img = smart_conversion(curr_img, 'ndarray', 'uint8')
            except Exception as e:
                # py_log.log_locals(MY_LOGGER, attr_sets=["size", "math"])
                raise e

            ax.imshow(img, cmap='gray')
            ax.set_title(f"{curr_title} ({SHOW_IMAGE_IX[0]})")
            ax.axis('off')
            SHOW_IMAGE_IX[0] += 1
    
    # set main title to the line where this function was called from
    caller_frame = inspect.currentframe().f_back
    caller_line = caller_frame.f_lineno
    caller_func = caller_frame.f_code.co_name
    caller_file = caller_frame.f_code.co_filename
    caller_file = osp.basename(caller_file)
    fig.suptitle(f"Called from line {caller_line} in {caller_func} in {caller_file}")

    initial_fig_name = plt.get_current_fig_manager().get_window_title()
    plt.get_current_fig_manager().set_window_title(f"{initial_fig_name}, line {caller_line} in {caller_func} in {caller_file}")

    plt.show(block=False)
    plt.pause(0.001)
}













LOG FRONTEND SUGGESTION WHEN FIXING BUGS:

Do crtl F on the browser viewer.
Use "Highlight All" in the browser settings that appear.
Use this finder to find by line - easy to type it.

When you are analysing what is happening in your code while you are changing it:
- have a few log_locals through your main function of interest
- (in the browser finder you already have the line number of the first log_locals)
- ctrl R for reload
- ctrl F, enter
And you are there.
And when you change the code, you just ctrl R, ctrl F, enter.
It makes it so easy to see what is happening in your code while you are making changes to fix something.












NEWNAMING SUGGESTION:
"Lesser suggestion" - leave this so it can be searched for in the text.
Alternatively, you could just have one log_locals at the bottom of the function, and you keep making new names for variables like so:
- Newnaming:
{
orig_img = Image.load(path)
transformed_img = my_transform(img)
}
Instead of renaming them:
{
img = Image.load(path)
img = my_transform(img)
}
The biggest problem is, that when an exception happens on the way, you never get to the logging.
And also, in shorter chains of such changes on this one variable you keep changing 
in a pipeline, new_naming works great - great readability, 
because on every line you are sure where the last change happened, 
because the unique name is literally in the line.
But with longer pipelines, especially ones where you might be permuting the lines 
(like in image data augmentation, where there is no best order of lines) 
this becomes a huge pain.

"""







# Additional info on what the system can do (Probably don't need to read this):
"""



LIMITING NUMBER OF LOGS IN log_locals:

You can also pass a list with a number to log_locals to limit the number of times it logs.
Example:
GLOBAL_LIST = [5]
py_log.log_locals(MY_LOGGER, GLOBAL_LIST)
At each logging, the number in the list will be decremented.
If the number is <= 0, log_locals will not log anything.

Examples of use for this:
- In a production environment, you only want the first 100 times to be logged.
- In a production environment, you go to a part of the code where this function, 
which has these log_locals in it, will be called a lot.
And you know there probably aren't any errors there anyway.
So you have this global list be [float(inf)] at the start, and you change it to, for example, [10] or [0] or whatever.
(Using float(inf) is not tested yet tho.)






AUTOLOG:

With autolog, you can also use the parameter:
log_stack_on_exception=True
When an exception happens in this function, it will do log_stack.
But since this is called from the decorator, the stack log doesn't actually have the called function's frame in it.
So you will get the stack, except for the called function - which is generally not very useful.
But you can use it if it helps in your case.




TO STOP LOGGING - EXPLANATION:
{
If you only comment out:
# python_logger_path = os.path.join(os.path.dirname(__file__), 'python_logger')
# handlers = py_log.file_handler_setup(MY_LOGGER, add_stdout_stream=False)
Then, since we set MY_LOGGER to debug level, what we log won't go anywhere. (By default only WARNING and above get printed to stderr.)
So we have effectively turned off writing logs.
But we are still wasting a bunch of CPU time - the logging is still happening, it just isn't written to anywhere.
So instead, we can leave these lines uncommented, and just change:
import python_logger.log_helper as py_log
to:
import python_logger.log_helper_off as py_log
Now all the imported functions, including file_handler_setup, are just empty functions.
However, other files where you still import python_logger.log_helper don't have empty functions. They are still wasting CPU time.
No file is written, because they don't do file_handler_setup, so they never set the file handlers.

So you have to go and add change the import line to python_logger.log_helper_off in every file to stop wasting CPU time.
}



TIMING YOUR CODE - continued:
{
Less useful way of logging time:
If LOG_TIME_ELSEWHERE == True, in log_locals, log_stack, log_manual we log:
- time since last call of log_locals/log_stack/log_manual respectively
- time since last logging of any time (including all above loggings)

In an individual call of .autolog(), log_locals(), log_stack() you can disable the time logging by setting time_log=False.
Time since last log will also not be affected if logging is disabled in this way.
However, log_manual doesn't have this parameter option - we want to keep the parameters clean.
}

"""


























# Previous explanations with minimal usefulness:

"""

Add log_locals(YOUR_LOGGER) above every return.
This will log all local variables of the function at that point.
log_locals() contains " @log_locals " in its printout instead.



!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!
Important VS code regex trick:

Since we need to add @autolog(our_logger) before every function, this is tedious.
We can instead use Ctrl+F with regex.
Find: ^( *)def
Replace: $1@autolog(our_logger)\n$1def
Do the same for log_locals() and return.

Explanation:
^ means start of line,

$k means the k-th capture group.
A capture group is whatever is in parentheses ()





Possibly add @log_for_class(passed_logger=YOUR_LOGGER) above your classes. This can:

if add_class_autolog == True
- set @autolog decorator to all the class's methods. The problem is, it's not just your methods. It's also __init__ and other methods.

If add_automatic_str_method == True
- add a __str__ method to the class, which prints all its attributes.

If add_automatic_repr_method == True
This is important for logging, because when you have an object of such class in your code,
 you want it to be logged with the attributes, not just the pointer to the object - that's useless.





Above we described a scenario, where we pass a logger object to the decorator. 
This code, however, supports 4 more options:
1. No logger is passed to the decorator. Here we create a default logger.

2. A logger class called MyLogger() is passed to the decorator.
(Useful for teams collaborating on a project, so the logger created is always standardized.)
MyLogger() is a class that has a method get_logger(name=None) that returns a logger.
It is a toy class we used in this code. You can just go into this code and rename MyLogger() to your logger class. 

Useful in some cases:
3. An actual logger OR a logger class called MyLogger() is passed as an argument to the decorated function.
4. An actual logger OR a logger class called MyLogger() is the classes attribute.
"""





# Previous explanations with minimal usefulness:


"""
!!!!!!!!!!!!!
Important VS code trick:
Since we need to add @autolog(our_logger) before every function, this is tedious.
We can instead use Ctrl+F with regex.
Find: ^( *)def
Replace: $1@autolog(passed_logger=YOUR_LOGGER)\n$1def
Do the same for log_locals() and return.

(Explanation:
^ means start of line,

$k means the k-th capture group.
A capture group is whatever is in parentheses ()
$0 refers to the entire matched string.

In the find part, we can use \k to refer to the k-th capture group,
 meaning that group repeating exactly.     

And there is a bunch more tricks. Ask ChatGPT.)
"""


# Previous explanations with minimal usefulness:

"""
This log_module:
- Logs the function name and its arguments when the function is called.
- Checks if its type hints are correct. Can crash program if ASSERT_TYPES is True and LET_LOGGER_CRASH_PROGRAM is True.
- Enables simple logging for classes. Enables an automatic addition of __str__ method to classes.
- Although simple logging for classes adds the logging for all methods called on it, like __init__ and other things as well,
so adding @autolog to the methods in the class instead is a good idea.
- Handles loggging shutdown upon SIGINT (ctrl-c interrupt)
- Offers the function log_locals(logger), which logs all local variables of a function.  


This is the logger that is used if no logger is passed to the decorator, like @autolog(my_own_logger).
When logging, it is best to pass your logger of that file.
# in theory you could also just change DEFAULT_LOGGER after importing. 

This sets the behaviour for the root logger. We don't want that, because then matplotlib and stuff start throwing us
debug logs into stderr.
logging.basicConfig(level=logging.DEBUG) # means all logs are logged. This it the least severe log level.


To create a log file, create a log handler.
An example of this is done below in __main__.
Do not forget to .close() the file handler after you are done with it.
"""






DEFAULT_LOGGER = logging.getLogger(__name__)
DEFAULT_LOGGER.setLevel(logging.DEBUG)


LOG_TIME_AUTOLOG = True # Here it makes the most sense. 
# The duration information tells us the most in autolog.
# Also, autologs don't have line information, important value information, ... So in autolog it's okay to clutter with time.

# alternative is time.process_time(). It measures only CPU time, not wall-clock time - so it's not affected by time.sleep().
CURR_TIME_FUNC = time.perf_counter
LAST_LOG_TIME = CURR_TIME_FUNC()








# More functions can happen if SIGINT is received in Python. So we aren't overriding anything.
import signal
import sys

def sigint_handler(signum, frame):
    print("Received SIGINT. Closing logger...")
    logging.shutdown()
    sys.exit(0)

signal.signal(signal.SIGINT, sigint_handler)
# It performs an orderly shutdown of the logging system by flushing and closing all handlers, not loggers per se.

class FileAndStreamHandlers:
    def __init__(self, handlers_list=[]):
        self.handlers = handlers_list

    def add_handler(self, handler):
        self.handlers.append(handler)

    def close_all_handlers(self):
        for handler in self.handlers:
            handler.close()






# because RotatingFileHandler doesn't work for some rason, we make our own variant

class CustomFileHandler(logging.FileHandler):
    def __init__(self, filename, maxBytes, backupCount=1, *args, **kwargs):
        super().__init__(filename, *args, **kwargs)
        self.maxBytes = maxBytes
        self.backupCount = backupCount
        self.baseFilename = os.path.abspath(filename)
        self.is_first_file = True

    def emit(self, record):
        try:
            if self.shouldRollover(record):
                self.doRollover()
            super().emit(record)
        except Exception:
            self.handleError(record)

    def shouldRollover(self, record):
        if self.stream is None:  # Delay was set.
            self.stream = self._open()
        if os.path.getsize(self.baseFilename) >= self.maxBytes:
            return True
        return False

    def doRollover(self):
        self.stream.close()
        

        # the appropriate backup numbers are: [1, 2,..., self.backupCount]
        # delete the backup-overflowing file, it if exists:
        if os.path.exists(f"{self.baseFilename}.{self.backupCount}"):
            os.remove(f"{self.baseFilename}.{self.backupCount}")

        # Bit-shift the names of existing backups:
        # range(4,0,-1) is [4, 3, 2, 1]
        for i in range(self.backupCount - 1, 0, -1):
            sfn = f"{self.baseFilename}.{i}"
            dfn = f"{self.baseFilename}.{i + 1}"
            if os.path.exists(sfn):
                os.rename(sfn, dfn)
        
        

        # If this was the first file, we want iit to be a special backup, so that we never lose it.
        # And if this is the first file, the above for loop didn't do anything anyway.
        if self.is_first_file:
            dfn = self.baseFilename + ".first_backup"
            os.rename(self.baseFilename, dfn)
            self.is_first_file = False
        else:
            # Rename the base file to .1
            dfn = self.baseFilename + ".1"
            os.rename(self.baseFilename, dfn)
        
        # Reopen the base file
        self.stream = self._open()








MAX_CHARS_IN_ONE_VAR = int(1e5)
MAX_FILE_SIZE_BYTES = 20 * 1024 * 1024
BACKUP_NUM = 1
VAR_BLACKLIST = []

def limitations_setup(max_chars_in_one_var=MAX_CHARS_IN_ONE_VAR, max_file_size_bytes=MAX_FILE_SIZE_BYTES, backup_num=BACKUP_NUM, always_have_first_backup=True, var_blacklist=VAR_BLACKLIST):
    
    # max_chars_in_one_var is the maximum number of characters of logging one variable that will be logged.
    # There are some repr()s that are very long and pointless and keep repeting (like the printout of model architecture in pytorch)
  
    # max_file_size_bytes is 20 Mb by default. Because with huge files, the log viewer can't open them anyway.

    # backup_num is the number of old log files to keep before deleting the oldest one.

    # always_have_first_backup is True by default.

    # var_blacklist is a list of variable names that will not be logged. This is useful to prevent annoying long logs that keep being logged but aren0t useful at all.

    global MAX_CHARS_IN_ONE_VAR
    global MAX_FILE_SIZE_BYTES
    global BACKUP_NUM
    global VAR_BLACKLIST

    if not always_have_first_backup:
        raise NotImplementedError("This is not implemented yet.")
    

    MAX_CHARS_IN_ONE_VAR = int(max_chars_in_one_var)
    MAX_FILE_SIZE_BYTES = max_file_size_bytes
    BACKUP_NUM = backup_num
    VAR_BLACKLIST = var_blacklist







# A global variable is shared across all files that import it.
# So when one file sets up logging, others won't set it up again.
# (Unless you e.g. want to set up more different loggers.
# If so, change the if condition to >= k.)
NUM_OF_FILE_HANDLER_SETUP_USES = 0

def file_handler_setup(logger, add_stdout_stream: bool = False, print_log_file_name: bool = True):
    
    global NUM_OF_FILE_HANDLER_SETUP_USES
    if NUM_OF_FILE_HANDLER_SETUP_USES >= 1:
        return None
    NUM_OF_FILE_HANDLER_SETUP_USES += 1

    path_to_python_logger_folder = os.path.dirname(os.path.abspath(__file__))
    os.makedirs(os.path.join(path_to_python_logger_folder, "logs"), exist_ok=True)
    logs_folder = os.path.join(path_to_python_logger_folder, "logs")

    # Create a file handler
    current_time = datetime.datetime.now()
    log_file_name = f"""log_{current_time.strftime('%d_%H-%M-%S_%m-%Y')}.log"""

    # Great idea, but there are some errors. Probably because more processes are trying to write to the same file. But I have no idea and will not try further.
    # handlers = py_log_always_on.file_handler_setup(MY_LOGGER, python_logger_path, rotation_megabytes=1024)
    # }
    # (when the log file is rotation_megabytes big, it is renamed to log_file_name.1 (backed up), and a new file is created.
    # When the new file reaches rotation_megabytes, the prev backup, the current file backs up, and a new file is created.
    # This is meant so you don't destroy your diskspace.
    # Set rotation_megabytes to 0 to never rotate the file.)
    # , rotation_megabytes: int = 10 * 1024, backup_count: int = 2
    # if rotation_megabytes >= 0:
    #     # When file becomes maxBytes big, it is renamed to log_file_name.1, and a new file is created.
    #     # backupCount is the number of old log files to keep before deleting them.
    #     # e.g. (1GB = 1 * 1024 * 1024 * 1024 bytes)
    #     # If maxBytes == 0, rollover never occurs, so we keep writing in the initial file.
    #     file_handler = logging.handlers.RotatingFileHandler(os.path.join(logs_folder, log_file_name), maxBytes=rotation_megabytes * 1024 * 1024, backupCount=backup_count)
    # else:
    #     raise ValueError("rotation_megabytes must be >= 0.")


    file_handler = CustomFileHandler(os.path.join(logs_folder, log_file_name), maxBytes=MAX_FILE_SIZE_BYTES, backupCount=BACKUP_NUM)
    file_handler.setLevel(logging.DEBUG)
    
    # This is nice to have, so you can easily find the log file that corresponds to some out.txt that isn't the latest one.
    if print_log_file_name:
        print(f"""Log file name: {log_file_name}.
            Add print_log_file_name=False to file_handler_setup() to disable this printout.""")

    
    # Enables easier use of log_server.py
    with open(os.path.join(logs_folder, "latest_log_name.txt"), "w") as f:
        f.write(log_file_name)

    # Create a formatter and set it for the file handler
    formatter = logging.Formatter('@log %(asctime)s - %(name)s - %(levelname)s - %(message)s')
    file_handler.setFormatter(formatter)

    # Add the file handler to the logger
    logger.addHandler(file_handler)

    stream_handler = logging.StreamHandler()
    if add_stdout_stream:
        # Add a StreamHandler for stdout - if you want to keep the stdout logging
        stream_handler.setLevel(logging.DEBUG)  # You can set a different level for stdout
        stream_handler.setFormatter(formatter)
        logger.addHandler(stream_handler)
    
    return FileAndStreamHandlers([file_handler, stream_handler])









def mark_list_of_strings(list_of_strings, start_marker, end_marker=None):
    if end_marker is None:
        end_marker = start_marker
    
    marked_list = []
    for s in list_of_strings:
        curr_s = s[:MAX_CHARS_IN_ONE_VAR]
        marked_list.append(start_marker + s + end_marker)

    return marked_list


def get_frame_up_the_stack(num_back):
    """
    :param num_back: The number of frames to go back.
    0 is the frame of get_func_frame_info_dict.
    1 is the frame of the logging function that called get_func_frame_info_dict.
    2 would then usually be the first sensible option.
    """

    frame = inspect.currentframe()
    for _ in range(num_back):
        frame = frame.f_back
    
    return frame


def get_func_frame_info_dict(frame):
    """
    Get a dictionary where:
    "filename",
    "line_number",
    "function_name"
    "local_vars" : dict of local variables
    """

    
    # Get local variables from the frame
    local_vars = frame.f_locals

    # Get additional information from the frame
    full_path = frame.f_code.co_filename
    filename = os.path.basename(full_path)
    line_number = frame.f_lineno
    function_name = frame.f_code.co_name

    returning_dict = {
        "filename": filename,
        "line_number": line_number,
        "function_name": function_name,
        "local_vars": local_vars
    }
    
    
    return returning_dict



def _get_unique_and_hist_string(arr, num_bins=10):

    try:
        import numpy as np

        if isinstance(arr, np.ndarray):

            unique, counts = np.unique(arr, return_counts=True)
            num_unique = len(unique)

            unique_list = unique.tolist()

            logging_string = f"\n Num of unique vals: {num_unique}. "

            # Get the minimum and maximum values
            min_val = np.min(unique)
            max_val = np.max(unique)


            # Count the number of elements equal to min and max
            min_count = counts[unique_list.index(min_val)]
            max_count = counts[unique_list.index(max_val)]

            logging_string += f"Min: {min_val} count: ({min_count}), Max: {max_val} count: ({max_count}). "



            # In the case where there are less unique values than num_bins, we just log the counts of each unique value.
            if num_unique <= num_bins:
                num_of_all = np.sum(counts)
                percents = counts / num_of_all * 100

                logging_string += f"Unique_counts: \n"
                counts_list = counts.tolist()
                percents_list = percents.tolist()
                for u, c, p in zip(unique, counts_list, percents_list):
                    logging_string += f"{u}: {c} ({p:.2f}%)\n"

                return logging_string
            
            

            # Define the bin edges excluding min and maxbins
            bin_edges = np.linspace(min_val, max_val, num_bins+1)

            # Compute the histogram
            hist, _ = np.histogram(arr, bins=bin_edges)
            percent_hist = hist / np.sum(hist) * 100

            hist_list = hist.tolist()
            percent_hist_list = percent_hist.tolist()

            ranges = [f"{bin_edges[i]}-{bin_edges[i+1]}" for i in range(num_bins)]
            logging_string += f"Hist (includes min and max vals):\n (percentage, count : range)\n"
            for r, h, p in zip(ranges, hist_list, percent_hist_list):
                logging_string += f"{p:.2f}%, {h} : {r}\n"
            
            return logging_string
    except Exception as e:
        # raise e
        pass

    try:
    
        import torch
        if isinstance(arr, torch.Tensor):


            # Get unique values and their counts
            unique, counts = torch.unique(arr, return_counts=True)
            num_unique = len(unique)

            unique_list = unique.tolist()

            logging_string = f"\n Num of unique vals: {num_unique}. "

            # Get the minimum and maximum values
            min_val = torch.min(unique).item()
            max_val = torch.max(unique).item()

            min_count = counts[unique_list.index(min_val)].item()
            max_count = counts[unique_list.index(max_val)].item()

            logging_string += f"Min: {min_val} count: ({min_count}), Max: {max_val} count: ({max_count}). "



            # In the case where there are less unique values than num_bins, we just log the counts of each unique value.
            if num_unique <= num_bins:
                num_of_all = torch.sum(counts).item()
                percents = counts / num_of_all * 100

                logging_string += f"Unique_counts: \n"
                counts_list = counts.tolist()
                percents_list = percents.tolist()
                for u, c, p in zip(unique, counts_list, percents_list):
                    logging_string += f"{u}: {c} ({p:.2f}%)\n"

                return logging_string
            


            # Define the bin edges excluding min and max
            bin_edges = torch.linspace(min_val, max_val, steps=num_bins + 1)

            # Compute the histogram
            hist, _ = torch.histogram(arr, bins=bin_edges)
            percent_hist = hist / torch.sum(hist) * 100
            
            hist_list = hist.tolist()
            percent_hist_list = percent_hist.tolist()

            ranges = [f"{bin_edges[i].item()}-{bin_edges[i+1].item()}" for i in range(num_bins)]
            logging_string += f"Hist (includes min and max vals):\n (percentage, count : range)\n"
            for r, h, p in zip(ranges, hist_list, percent_hist_list):
                logging_string += f"{p:.2f}%, {h} : {r}\n"
            
            return logging_string
    except Exception as e:
        # raise e
        pass
    
    # In case nothing was returned
    return None

    




def _get_list_of_reprs_from_dict_like_kwargs(kwargs_like_dict, check_attributes=True, attr_sets=["size"], added_attribute_names=[], func_name=None):
    
    # attr_sets is a list of strings that can be: "size", "math", "hist". Other strs are ignored.
    # "size" are O(1) operations, so they are the default.
    # "math" and "hist" are O(n) operations.

    # Mind that "hist" requires numpy and torch to be installed.

    check_attrs = [name for name in added_attribute_names]
    # if v has .shape, .size, .dtype, .__len__ or .shape(), .size(), .dtype(), .__len__(), we want to log that too.
    if "size" in attr_sets:
        check_attrs += ["shape", "size", "dtype", "__len__"]
    if "math" in attr_sets:
        check_attrs += ["mean", "std", "min", "max", "sum"]

    local_vars_strs = []

    for k, v in kwargs_like_dict.items():



        curr_str = f"{k} ({type(v)}) "
        
        if k in VAR_BLACKLIST:
            curr_str += "= (var is log-blacklisted)"
            local_vars_strs.append(curr_str)
            continue


        if check_attributes:


            for attr_name in check_attrs:
                try:
                    curr_attr = getattr(v, attr_name, "No such attribute.")

                    if curr_attr == "No such attribute.":
                        continue
                    
                    # With getattr you get the method or attribute of the object with that name.
                    # If the object has both a method and an attribute with the same name,
                    # the method is returned. There is a workaround with example_obj.__dict__['shape']
                    # to get the attribute instead of the method. But if it has both we will just stick with
                    # only getting the method for now.

                    if callable(curr_attr):
                        curr_str += f"[{attr_name}(): {curr_attr()}] "
                    else:
                        curr_str += f"[{attr_name}: {curr_attr}] "

                except Exception as e:
                    curr_str += f"(logger error in trying to get {attr_name}. Error: {e}) "


            # This functionality is not as simple as regular getattr checking, so we do it separately.
            if "hist" in attr_sets:
                hist_str = _get_unique_and_hist_string(v)
                if hist_str is not None:
                    curr_str += hist_str




        try:
            # Preventing infinite recursion in the case where the object has log_for_class decorator,
            # and has a __repr__ method (which then has autolog decorator).

            # And so when we call {v!r}, where the v is self (repr has self as a param),
            # it calls the __repr__ method, which calls autolog, which calls the __repr__ method, ...
            detect_recursion = func_name == "__repr__" and k == "self"
            
            if not detect_recursion:
                curr_str += f"= {v!r}"
        except:
            curr_str += f"= (logger error in trying to get the representation of the object.)"

        
        local_vars_strs.append(curr_str)
    
    return local_vars_strs


def info_dict_to_string(info_dict, have_local_vars=True, check_attributes=True, attr_sets=["size"], added_attribute_names=[]):

    filename = info_dict["filename"]
    line_number = info_dict["line_number"]
    function_name = info_dict["function_name"]
    local_vars = info_dict["local_vars"]
    
    logging_string = f"""Filename: {filename}
                    Function {function_name} 
                      Line: {line_number}\n"""

    if have_local_vars:
        logging_string += "Local variables: "

        local_vars_strs = _get_list_of_reprs_from_dict_like_kwargs(local_vars, check_attributes=check_attributes, attr_sets=attr_sets, added_attribute_names=added_attribute_names)
        
        # local_vars_strs = [f"{k}={v!r}" for k, v in local_vars.items()]

        marked = mark_list_of_strings(local_vars_strs, start_marker="[START_VAR]", end_marker="[END_VAR]")
        logging_string += " \n " + ", \n".join(marked)

    return logging_string




def log_locals(passed_logger=DEFAULT_LOGGER, list_with_limiting_number=[], check_attributes=True, attr_sets=["size"], added_attribute_names=[]):
    """
    Log all local variables in the current frame.
    
    :param logger: The logger to use (defaults to DEFAULT_LOGGER)
    """
    logging_string = " @log_locals \n"

    

    if len(list_with_limiting_number) == 1: 
        if list_with_limiting_number[0] <= 0:
            return
        else:
            list_with_limiting_number[0] -= 1

    frame = get_frame_up_the_stack(2)
    frame_info = get_func_frame_info_dict(frame)
    
    # Break potential reference cycle 
    del frame

    info_string = info_dict_to_string(frame_info, check_attributes=check_attributes, attr_sets=attr_sets, added_attribute_names=added_attribute_names)


    logging_string += info_string
    passed_logger.debug(logging_string)






def log_stack(passed_logger=DEFAULT_LOGGER, check_attributes=True, attr_sets=["size"], added_attribute_names=[]):
    """
    Log the stack trace.
    """

    logging_string = " @log_stack \n"

    all_info_dicts = []

    stack = inspect.stack()

    for ix, frame_info_class in enumerate(stack):
        frame = frame_info_class.frame
        
        frame_info = get_func_frame_info_dict(frame)
        frame_info_string = info_dict_to_string(frame_info, check_attributes=check_attributes, attr_sets=attr_sets, added_attribute_names=added_attribute_names)
        
        logging_string += 4*"\n" + 15*"-" + "\n"
        logging_string += f"Frame {ix}\n" + frame_info_string + "\n"
        all_info_dicts.append(frame_info)


    # Log each local variable
    passed_logger.debug(logging_string)


    return all_info_dicts



def log_manual(passed_logger=DEFAULT_LOGGER, *args, **kwargs):

    check_attributes = True
    attr_sets = ["size", "math", "hist"]
    added_attribute_names = []

    if "check_attributes" in kwargs:
        check_attributes = kwargs["check_attributes"]
    if "attr_sets" in kwargs:
        attr_sets = kwargs["attr_sets"]
    if "added_attribute_names" in kwargs:
        added_attribute_names = kwargs["added_attribute_names"]



    logging_string = " @log_manual \n"

    

    
    frame = get_frame_up_the_stack(2)
    frame_info = get_func_frame_info_dict(frame)
    
    # Break potential reference cycle 
    del frame

    info_string = info_dict_to_string(frame_info, have_local_vars=False)
    logging_string += info_string

    
    args_dict = {}
    for ix, arg in enumerate(args):
        args_dict[f"arg_{ix}"] = arg

    args_strs = _get_list_of_reprs_from_dict_like_kwargs(args_dict, check_attributes=check_attributes, attr_sets=attr_sets, added_attribute_names=added_attribute_names)
    kwargs_strs = _get_list_of_reprs_from_dict_like_kwargs(kwargs, check_attributes=check_attributes, attr_sets=attr_sets, added_attribute_names=added_attribute_names)

    all_args = args_strs + kwargs_strs
    marked = mark_list_of_strings(all_args, start_marker="[START_VAR]", end_marker="[END_VAR]")
    
    logging_string += " \n " + ", \n".join(marked)

    passed_logger.debug(logging_string)



IMMUTABLE_2_TIMES = {}

def log_time(passed_logger=DEFAULT_LOGGER, immutable_id=""):
    """
    Log the time since the last log_time call.
    """

    curr_time = CURR_TIME_FUNC()

    global LAST_LOG_TIME
    global IMMUTABLE_2_TIMES
    
    logging_string = " @log_time \n"

    if immutable_id in IMMUTABLE_2_TIMES:
        since_last_call = curr_time - IMMUTABLE_2_TIMES[immutable_id]
        logging_string += f"Time since last log_time call with this '{immutable_id}': {since_last_call:.8f} s\n"
    else:
        logging_string += f"First log_time call with this '{immutable_id}'. Curr time: {curr_time}\n"

    
    since_last_log = curr_time - LAST_LOG_TIME
    logging_string += f"Time since last log: {since_last_log:.8f} s\n"


    frame = get_frame_up_the_stack(2)
    frame_info = get_func_frame_info_dict(frame)
    
    # Break potential reference cycle 
    del frame

    info_string = info_dict_to_string(frame_info, have_local_vars=False)
    logging_string += info_string


    passed_logger.debug(logging_string)

    last_time = CURR_TIME_FUNC()
    LAST_LOG_TIME = last_time
    IMMUTABLE_2_TIMES[immutable_id] = last_time






# Initial ideas:
"""
This log_module covers 5 scenarios.

1. No logger is passed to the decorator.
Here we create a default logger.

2. A logger class called MyLogger() is passed to the decorator.
3. An actual logger is passed to the decorator.
Here we simply use what was passed.

4. An actual logger OR a logger class called MyLogger() is passed as an argument to the decorated function.
5. An actual logger OR a logger class called MyLogger() is the classes attribute.
Here we use what was passed to the decorated function as a parameter first,
and if it wasn't, we look for any such thing in the class's attributes,
and if nothing is there, we do the 1. case and create MyLogger().





Initial idea:

Za logging decorator bi tako lahko ustvaril decorator, ki pred in po klicu funkcije izpiše njene lokalne spremenljivke (does not work).
Lahko bi tudi avtomatsko preveril, če so parametri pravilnega tipa glede na type hints. Tako bi, če niso,
 lahko naredil critical log, da niso bili. Lahko bi tudi imel glocalno spremenljivko ASSERT_TYPES=True,
 in ob njej tudi assertal vse tipe, akr je fajn when developping.
Najboljše je, da je te dekoratorje tako preprosto dodat: preprosto control F-aš def in ga nadomestiš z @nekaj\ndef.
Lahko bi tudi naredil dekorator za classe, ki avtomatsko vsem njegovim metodam doda ta funkcijski decorator,
 in ga tako pišeš samo nad definicijo classa.
Ta class decorator bi lahko tudi avtomatsko ustvaril __str__ metodo, ki bi izpisala vrednosti vseh spremenljivk classa. 


Logging local variables of a function does not work.
You can only log wrapper() or module.
This only makes sense, since in the decorateor, we are never in the function.
Another logging mechanism has to be created for that.




This logger is adapted from https://ankitbko.github.io/blog/2021/04/logging-in-python/

It loggs the function name and its arguments when the function is called.
It also logs the exception raised in the function, if any.


It covers options of passing a logger to the decorator, passing a logger to the decorated function,
or having a logger in the method's class's attributes.

It also covers the case of passing a logger generating class, here named MyLogger(),
but could be anything your project uses - just rename MyLogger in this code.

If no logger is passed, it uses the default logger.
"""





class MyLogger:
    def __init__(self):
        logging.basicConfig(level=logging.DEBUG)

    def get_logger(self, name=None):
        return logging.getLogger(name)

# Was used before in place of DEFAULT LOGGER 
# def get_default_logger():
#     return MyLogger().get_logger()





def autolog(_func=None, *, passed_logger: Union[MyLogger, logging.Logger] = None, assert_types=True, let_logger_crash_program=True, log_stack_on_exception=False, time_log=True, check_attributes=True, attr_sets=["size"], added_attribute_names=[]):

        

    def decorator_log(func):
        @functools.wraps(func)
        def wrapper(*args, **kwargs):

            
            # First we try to do the first part of loging time,
            # and to set up what logger to use.
            # If we fail here, no logging happens.
            # Also, if we fail here, the try block that does the logging will fail too.
            # But the function result will still be returned correctly.

            function_call_id = random.randint(0, int(1e9))

            try:

                

                # ----------------- SETTING UP LOGGER -----------------
                
                logger = DEFAULT_LOGGER

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


                

                # ----------------- LOGGING PREP -----------------

                # Here we try to log the function call.
                # Now comes what we do with the logger before function call:

                signature = inspect.signature(func)
                bound_args = signature.bind(*args, **kwargs)
                bound_args.apply_defaults()

                # Log function call
                func_name = func.__name__

                args_dict = {}
                for key, arg in bound_args.arguments.items():
                    args_dict[key] = arg
                    
                printable_args = _get_list_of_reprs_from_dict_like_kwargs(args_dict, check_attributes=check_attributes, attr_sets=attr_sets, added_attribute_names=added_attribute_names, func_name=func_name)
                marked_printable_args = mark_list_of_strings(printable_args, start_marker="[START_VAR]", end_marker="[END_VAR]")
                
                logging_string = " @autolog \n"
                logging_string += f" Function {func_name} \n"
                logging_string += f"Call id: {function_call_id} \n"
                args_string = "Called with arguments: "
                args_string += " \n " + ", \n".join(marked_printable_args)
                logging_string += args_string
                logger.debug(logging_string)
                


                # Type checking
                for param, arg_value in bound_args.arguments.items():
                    param_type = signature.parameters[param].annotation
                    if param_type != inspect.Parameter.empty and not isinstance(arg_value, param_type):
                        logger.critical(f""" @autolog 
                                        Type mismatch for parameter '{param}'. 
                                        Expected {param_type}, got {type(arg_value)}""")
                        if assert_types:
                            assert param_type == type(arg_value), f"Type mismatch for parameter {param}. Expected {param_type}, got {type(arg_value)}"
                            # raise TypeError(f"Type mismatch for parameter {param}. Expected {param_type}, got {type(arg_value)}")



                # We want it right before the function call, but we want it in a try-block, so it can't mess up the function call.
                time_right_before_func_call = CURR_TIME_FUNC()

            except Exception as e:
                if let_logger_crash_program:
                    raise e
                



            # ----------------- CALLING THE FUNCTION -----------------

            # Here we try to call the passed function. We return it after the logging try block.
            try:

                # WHERE THE FUNC HAPPENS!!!
                result = func(*args, **kwargs)
                
                try:
                    time_right_after_func_call = CURR_TIME_FUNC()
                    func_duration = time_right_after_func_call - time_right_before_func_call

                    
                    if LOG_TIME_AUTOLOG and time_log:

                        logging_string = " @time_autolog \n"
                        logging_string += f"Function {func_name} \n"
                        logging_string += f"Call id: {function_call_id} \n"
                        logging_string += f"Function duration: {func_duration:.8f} s\n"
                        logging_string += f"Returned: {result!r} \n"
                        logger.debug(logging_string)

                except Exception as e:
                        if let_logger_crash_program:
                            raise e
            
                

                return result
            

            # The except block for the entire function.
            except Exception as e:

                if log_stack_on_exception:
                    log_stack(logger)
                logger.exception(f""" @autolog 
                                 Exception raised in {func.__name__}. 
                                    exception: {str(e)}""")
                raise e
            
        return wrapper

    if _func is None:
        return decorator_log
    else:
        return decorator_log(_func)



def log_for_class(_cls=None, *, passed_logger: Union[MyLogger, logging.Logger] = None, add_automatic_str_method=True, add_automatic_repr_method=True, add_class_autolog=True):

    def decorator(cls):
        # Add automatic __str__ method if requested
        if add_automatic_str_method:
            def auto_str(self):
                attrs = vars(self)
                return f"{cls.__name__}({', '.join(f'{key}={value}' for key, value in attrs.items())})"
            cls.__str__ = auto_str
        
        # Add automatic __repr__ method
        if add_automatic_repr_method:
            def auto_repr(self):
                attrs = vars(self)
                return f"{cls.__name__}({', '.join(f'{key}={value!r}' for key, value in attrs.items())})"
            cls.__repr__ = auto_repr

        if add_class_autolog:
            # Wrap each method with the log decorator
            for name, member in inspect.getmembers(cls):
                if inspect.isfunction(member):
                    setattr(cls, name, autolog(member, passed_logger=passed_logger))

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
        
        if add_automatic_str_method:
            def __str__(self):
                attrs = vars(self)
                return f"{cls.__name__}({', '.join(f'{key}={value}' for key, value in attrs.items())})"
    

    for name, member in inspect.getmembers(cls):
        if inspect.isfunction(member):
            # Below this is performed: cls.func_name = autolog(class.func_name)
            # Which is what is in the background of using @autolog above a function.
            setattr(WrapperClass, name, autolog(getattr(cls, name)))
    
    return WrapperClass
"""


if __name__ == "__main__":




    MY_LOGGER = logging.getLogger("whatever_name_you_want")
    MY_LOGGER.setLevel(logging.DEBUG)

    handlers = file_handler_setup(MY_LOGGER, add_stdout_stream=True)

    # # Create a file handler
    # current_time = datetime.datetime.now()
    # log_file_name = f"log_{current_time.strftime('%S-%M-%H_%Y-%m-%d')}.log"
    # file_handler = logging.FileHandler(log_file_name)
    # file_handler.setLevel(logging.DEBUG)

    # # Enables easier use of log_server()
    # with open("latest_log_name.txt", "w") as f:
    #     f.write(log_file_name)

    # # Create a formatter and set it for the file handler
    # formatter = logging.Formatter('@log %(asctime)s - %(name)s - %(levelname)s - %(message)s')
    # file_handler.setFormatter(formatter)

    # # Add the file handler to the logger
    # MY_LOGGER.addHandler(file_handler)

    # # Add a StreamHandler for stdout - if you want to keep the stdout logging
    # stream_handler = logging.StreamHandler()
    # stream_handler.setLevel(logging.DEBUG)  # You can set a different level for stdout
    # stream_handler.setFormatter(formatter)
    # MY_LOGGER.addHandler(stream_handler)



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

    class MyClass_2:
        def __init__(self, x: int, y: str):
            self.x = x
            self.y = y
        
        @autolog(passed_logger=MY_LOGGER)
        def add(self, z: int) -> int:
            return self.x + z
        
        @autolog(passed_logger=MY_LOGGER)
        def concat(self, s: str) -> str:
            return self.y + s
    
    obj = MyClass_2(5, "Hello")
    print(obj.add(3))
    print(obj.concat(" World"))
    print(obj)
    

    
    # actual logger is passed

    @autolog(passed_logger=MY_LOGGER)
    def sum(a, b=10):
        return a + b
    sum(10)

    
    
    # MY_LOGGER is passed as an argument to the decorated function
    @autolog
    def foo(a, b, logger):
        pass

    @autolog
    def bar(a, b=10, logger=None): # Named parameter
        pass

    foo(10, 20, MY_LOGGER)
    bar(10, b=20, logger=MY_LOGGER)




    # logger is the classes attribute

    class Foo:
        def __init__(self, logger):
            self.lg = MY_LOGGER

        @autolog
        def sum(self, a: int, b: int =10):
            hejhoj = 5
            log_locals(MY_LOGGER)
            return a + b

    Foo(MY_LOGGER).sum(10, b=20)



    inp = input("Enter 'c' to close file_handler. Anything else to continue.")

    if inp == "c":
        handlers.close()


    inp = input("Enter 'c' to crash due to type mismatch. Anything else to continue.")

    if inp == "c":

        # Testing type assertion
        @autolog(passed_logger=MY_LOGGER)
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
    formatter = logging.Formatter('@log %(asctime)s - %(name)s - %(levelname)s - %(message)s')
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
    class MyClass_3:
        def __init__(self, x: int, y: str):
            self.x = x
            self.y = y
        
        def add(self, z: int) -> int:
            return self.x + z
        
        def concat(self, s: str) -> str:
            return self.y + s
    
    obj = MyClass_3(5, "Hello")
    print(obj.add(3))
    print(obj.concat(" World"))
    print(obj)
    



    # no logger is passed

    @autolog
    def sum(a, b=10):
        return a+b
    sum(10, 20)



    # logger class is passed

    @autolog(passed_logger=MyLogger())
    def sum(a, b=10):
        return a + b
    sum(10)

    
    # actual logger is passed

    lg = MyLogger().get_logger()

    @autolog(passed_logger=lg)
    def sum(a, b=10):
        return a + b
    sum(10)

    
    
    # logger is passed as an argument to the decorated function
    @autolog
    def foo(a, b, logger):
        pass

    @autolog
    def bar(a, b=10, logger=None): # Named parameter
        pass

    foo(10, 20, MyLogger())  # OR foo(10, 20, MyLogger().get_logger())
    bar(10, b=20, logger=MyLogger())  # OR bar(10, b=20, logger=MyLogger().get_logger())




    # logger is the classes attribute

    class Foo:
        def __init__(self, logger):
            self.lg = logger

        @autolog
        def sum(self, a: int, b: int =10):
            hejhoj = 5
            log_locals(DEFAULT_LOGGER)
            return a + b

    Foo(MyLogger()).sum(10, b=20)  # OR Foo(MyLogger().get_logger()).sum(10, b=20)



    input("Enter 'c' to close file_handler. Anything else to continue (to the crash).")

    if input() == "c":
        file_handler.close()


    # Testing type assertion
    @autolog
    def sum(a: int, b=10):
        return a+b
    sum(1.25, 20)

    input()




