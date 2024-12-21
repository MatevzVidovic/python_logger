


# Beware!
The data in this md might be old.
The most current version of the docs is in the comments at the top of log_helper.py.


# TL;DR:
"""

This code helps you log your code with minimal effort.
Above a function definition, you just add:
@py_log.log(passed_logger=MY_LOGGER)
def foo(a: int, b, c: float): ...
This does:
- automatic logging that the function was called and the arguments it was called with
- checking the correctness of type hints of the passed arguments (was the passed c really a float?)
- logging the amount of time that the function needed in its execution
Also:
- logging of local variables (all vars defined in this func) at any point in the code (just write py_log.log_locals(MY_LOGGER))
- logging of all local variables in the entire stack trace (py_log.log_stack(MY_LOGGER))
- logging of time since the last log_time call with a certain immutable_id (py_log.log_time(MY_LOGGER, immutable_id="some string you like"))
- logging of whatever you want (py_log.manual_log(MY_LOGGER, "rocni string", vrba, vrbica_moja=vrba))
- and some other stuff too.
And most importantly:
- you can view all these logs in a nice frontend that is easy to filter.

# Main info:

## SETUP:

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






## CODE SETUP:

In your main file, above all imports at the top of the file, add this code:
(above all imports so that file_handler_setup() is done before any 
code from importing your other files is run. And so all the loggings 
are actually written to the output file.)
{
```
import os
import logging
import python_logger.log_helper as py_log

MY_LOGGER = logging.getLogger("prototip") # or any string. Mind this: same string, same logger.
MY_LOGGER.setLevel(logging.DEBUG)

python_logger_path = os.path.join(os.path.dirname(\_\_file\_\_), 'python_logger')
handlers = py_log.file_handler_setup(MY_LOGGER, python_logger_path, add_stdout_stream=False)
```
}

In all the other files you are importing, add this code without the file handler part:
{
```
import logging
import python_logger.log_helper as py_log

MY_LOGGER = logging.getLogger("prototip") # or any string. Mind this: same string, same logger.
MY_LOGGER.setLevel(logging.DEBUG)
```
}
(In theory adding more file handlers would lead to logs being duplicated.
Although our code is set up so that this doesn't happen even if you mess up.)





## IF YOU WANT TO STOP LOGGING:

If you want the logging to stop, you can:
- simply comment out the 2 file_handler_setup lines in your main file. (still wastes CPU time)
- You change the line import python_logger.log_helper
to: import python_logger.log_helper_off
in all files where you use this import. Now the logging functions, including file_handler_setup,
 are all empty functions that just return, write nothing anywhere, waste no resources.
(If you don't mind wasting CPU time, all you care about is the log files to not be written,
you can make this _off change in just the file/files where you call file_handler_setup() (same as commenting out the lines).)





## USE:

Go play with the following repo to get example uses and how they work: https://github.com/MatevzVidovic/pylog_tester.git
It will be easier than just reading this text (although, do that too).
Especially go look for the use of what log_stack returns. It comes in really handy in debugging with vizualizations.





## AUTOLOG:

Add @py_log.log(passed_logger=MY_LOGGER) above functions you want to log.
@py_log.log(passed_logger=MY_LOGGER)
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
@py_log.log(passed_logger=MY_LOGGER, assert_types=False, let_logger_crash_program=False)

We also log the time of execution of the function.
However, to time the function, we have to run it first. But we want @autolog to happen right before the
function happens - so we can't put the time in the same log.
For this reason, we created @time_autolog logs.
These logs contain " @time_autolog " in its printout.
These happen right after the function finished.

In a way this is nice, because then in your logs you have a nice encapsulation of the function - the start and the end logs are clear.
It is however less clear for functions that call themselves, because in the logs between the main @autolog and @time_autolog, we have the same encapsulation.
For this reason we add a random number to both the @autolog and @time_autolog logs, so we can actually know which @time_autolog belongs to which @autolog.

If these logs bug you, just regex them away in the log viewer.

See more in TIMING YOUR CODE.







## LOG_LOCALS:

Add py_log.log_locals(MY_LOGGER) somewhere in the code.
It will print all the local variables at that point (function scope variables).
Possibly add this above every return.
These logs contain " @log_locals " in its printout.




## OBJECT ATTRIBUTE LOGGING:

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
"size" checks for shape, size, dtype, \_\_len\_\_.
"math" checks for mean, std, min, max, sum.
You can pass these set names in a list to attr_sets.
By default, this is only ["size"], because math operations take longer to compute.

These three parameters can be used in .log, .log_locals, .log_stack, .manual_log.
Everywhere they are check_attributes=True, attr_sets=["size"], added_attribute_names=[] by default.




## MANUAL_LOG:

Use py_log.manual_log(MY_LOGGER, *args, **kwargs) to log whatever you want.
You just give anything as arguments and keyword arguments and it will log them.
These logs contain " @manual_log " in its printout.

I suggest using kwargs for better readability - manual log will log 
what keyword you used for the argument, so you can easily be sure what is what in the log.

Possibly use your own @something_something as arguments in your manual logs.
This will allow you to use the regex aspect of the log viewer to filter out only certain manual logs.

Example:
py_log.manual_log(MY_LOGGER, "rocni string", vrba, vrbica_moja=vrba)
(vrba was a variable in that scope)



## LOG_STACK:

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





## TIMING YOUR CODE:

All loggings of time use time.perf_counter() to measure time.
This means they measure wall-clock time, not CPU time - so if you have sleep() in your code, it will affect the time.
An alternative is time.process_time(). It measures only CPU time, not wall-clock time - so it's not affected by time.sleep().
To change it, change the CURR_TIME_FUNC global variable to time.process_time.

LOG_TIME:
Use py_log.log_time(MY_LOGGER, immutable_id="") to log the time since the last log_time call with that immutable_id.
As immutable_id you can pass any immutable type - like a string, a number, a tuple, ...
These logs contain " @log_time " in its printout.


Most useful way of logging time:
if LOG_TIME_AUTOLOG == True, in autologging with .log() we log the time of execution of the decorated function.
In an individual call of .log() you can disable the time logging by setting time_log=False.






## ENABLING OF LAZINESS:

If you are lazy and don't care about clutter of logs, you can do a find and replace
to add the loggings to all your functions.
(This regex will still duplicate the loggings, so add them one by one in teh find and replace.)
{
To do this easily in VS code, use regex:

^(?!.*@log\n)( *)def
Find: ^( *)def
Replace: \$1@py_log.log(passed_logger=MY_LOGGER)\n$1def

and

Find: ^( *)return
Replace: \$1log_locals(passed_logger=MY_LOGGER)\n$1return
}





## USING LOG VIEWER REGEX:

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





# USING SERVER_PY:

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








# Expanded main info (after you have used the code a bit, I suggest you read this):


## LOG_FOR_CLASS:

You can also put
@py_log.log_for_class(passed_logger=MY_LOGGER)
above a class definition.

This does 3 things. They can all be disabled if you call this like so:
@py_log.log_for_class(passed_logger=MY_LOGGER, add_automatic_str_method=False, add_automatic_repr_method=False, add_class_autolog=False)

If add_class_autolog = True,
this will set @py_log.log(passed_logger=MY_LOGGER) to all the class's methods.

This seems nice at first, but it also sets the logging to \_\_init\_\_ 
and other methods python includes by default. And you don't want that.
Also, having log for all methods is too much clutter anyway.

If add\_automatic\_str\_method = True,
it also adds a \_\_str\_\_ method to the class, which prints all its attributes.
This is nice if you want to print the object in your code.

Most importantly:

If add\_automatic\_repr\_method = True,
it also adds a \_\_repr\_\_ method to the class, which prints all the objects attributes.
This is important, because when this class is logged, \_\_repr\_\_ is called.
So without it, you will only get the pointer to the object in your log.

When we do logging, we are always calling \_\_repr\_\_ of our attributes (by using {v!r}.
This is a general python magic method, which gives a comprehensive string representation of the object 
(unlike \_\_str\_\_, which is meant to be more user friendly).







# Advice on use (Maybe a bit stupid - read only after you have used the code a bit):





## LOG LOCALS SUGGESTION:

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




## NUMPY ARRAY LOGGING SUGGESTION:

Some arrays have useless values at the edges. You want to see the middle of the array.
But the printout cuts it off. Even repr(arr) cuts it off.

You can use:
with np.printoptions(threshold=np.inf):
    py_log.manual_log(arr)   # or log_locals or log_stack

Mind that this took my program 10 seconds for 4 1024x1024x3 imgs.
So COMMENT IT OUT IN PROD!!!




## VIZUALIZABLE DUBUGGING SUGGESTION (like images, graphs, neural net compute graphs, ...):

When working with things that can be visualized, like images, have a general non-blocking vizualization function.
Example:
{
```
SHOW_IMAGE_IX = [0]
def show_image(img, title=""):
    plt.figure()
    plt.imshow(img, cmap='gray')
    plt.title(f"{title} ({SHOW_IMAGE_IX[0]})")
    SHOW_IMAGE_IX[0] += 1
    plt.axis('off')
    plt.show(block=False)
    plt.pause(0.001)
```
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
```
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
```
}













## LOG FRONTEND SUGGESTION WHEN FIXING BUGS:

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












## NEWNAMING SUGGESTION:
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









# Additional info on what the system can do (Probably don't need to read this):




## LIMITING NUMBER OF LOGS IN log_locals:

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






## AUTOLOG:

With autolog, you can also use the parameter:
log_stack_on_exception=True
When an exception happens in this function, it will do log_stack.
But since this is called from the decorator, the stack log doesn't actually have the called function's frame in it.
So you will get the stack, except for the called function - which is generally not very useful.
But you can use it if it helps in your case.




## TO STOP LOGGING - EXPLANATION:
{
If you only comment out:
```
# python_logger_path = os.path.join(os.path.dirname(\_\_file\_\_), 'python_logger')
# handlers = py_log.file_handler_setup(MY_LOGGER, python_logger_path, add_stdout_stream=False)
```
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



## TIMING YOUR CODE - continued:
{
Less useful way of logging time:
If LOG_TIME_ELSEWHERE == True, in log_locals, log_stack, manual_log we log:
- time since last call of log_locals/log_stack/manual_log respectively
- time since last logging of any time (including all above loggings)

In an individual call of .log(), log_locals(), log_stack() you can disable the time logging by setting time_log=False.
Time since last log will also not be affected if logging is disabled in this way.
However, manual_log doesn't have this parameter option - we want to keep the parameters clean.
}











