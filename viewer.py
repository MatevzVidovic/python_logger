

# for viewing .py logs

"""
Recommended usage:

- use of log regex is well explained in the console printout.

- make a note of conditions you want to filter by,
and paste it to the terminal. This gives you easy reproducability
of the wanted filtering later. 
e.g.
c:a
n:all
n:a
k:2
c:@autolog

Important: make sure to copy the last newline too (here, the \n after c:@autolog)
by dragging your mouse to the empty line after the conditions.
Otherwise, it doesn't get added.


- use ctrl + K + 0  in vscode
This collapses the text in python.
It will also collapse the multiline strings.
You then manually uncollapse certain logs on the left side (by the line numbers).
Also, use ctrl F to search through the logs. This automatically uncollapses the found log.


"""
# cd python_logger
# python3 viewer.py logs/log_999_sthsth.py

import argparse
from pathlib import Path

import os, time

def clear():
    os.system('cls' if os.name == 'nt' else 'clear')





# take path to log arg
def main():
    parser = argparse.ArgumentParser(description='Log File Viewer')
    parser.add_argument('log_path',  nargs='?', default=None, help='Path to the log file to view')
    args = parser.parse_args()




    # get path to this file
    code_file_path = Path(__file__).parent.resolve()

    relative_log_path = args.log_path
    if relative_log_path is None:
        latest_log_name_path = code_file_path / "logs" / "latest_log_name.txt"
        with open(latest_log_name_path, 'r') as f:
            log_name = f.read().strip()
            relative_log_path = Path("logs") / log_name
    log_path = code_file_path / Path(relative_log_path)




    if not log_path.exists():
        print(f"Error: The log file '{log_path}' does not exist.")
        return

    try:
        with open(log_path, 'r') as file:
            original_content = file.read()
            log_splitter = "# @log"
            og_logs = original_content.split(log_splitter)
    except Exception as e:
        print(f"Error reading the log file: {e}")



    curr_logs = og_logs.copy()
    regex_conditions = []

    while True:
        logs_to_temp(curr_logs, code_file_path, log_splitter)

        print("""Regex syntax:
c:<regex> - log must match condition (contains)
n:<regex> - log must not match condition (does not contain)
k:<index> - remove condition with that index
              
""")
        print("Current regex conditions:")
        for i, condition in enumerate(regex_conditions):
            print(f"{i}: {condition}")
        cond = input("Add condition: (Press Enter to skip)")
        clear() # clear stdout

        if cond.startswith("c:") or cond.startswith("n:"):
            regex_conditions.append(cond)
        elif cond.startswith("k:"):
            # remove condition
            try:
                index = int(cond[2:])
                if 0 <= index < len(regex_conditions):
                    regex_conditions.pop(index)
                else:
                    print(f"Error: Index {index} is out of range.")
            except ValueError:
                print("Error: Invalid index format. Use 'k:<index>' to remove a condition.")
        elif cond != "":
            print(f"Error: Invalid condition format. Gave: {cond}")
            continue

        
        curr_logs = apply_regex(og_logs, regex_conditions)
        


def logs_to_temp(logs, code_file_path, log_splitter="# @log"):
    """
    Takes a list of logs and writes them to a temporary output file.
    Each log is separated by the specified log_splitter.
    """
    temp_out_path = code_file_path / "logs" / "000temp_out.py"
    
    with open(temp_out_path, 'w') as temp_file:
        
        temp_content = log_splitter + log_splitter.join(logs)
        temp_file.write(temp_content + "\n\n")
    
    return temp_out_path


def passes_regex(log, regex_condition):
    """
    Checks if the given log passes the specified regex condition.
    """
    import re
    searched = regex_condition[2:]
    
    if regex_condition.startswith("c:"):
        return re.search(searched, log) is not None
    elif regex_condition.startswith("n:"):
        return re.search(searched, log) is None
    else:
        raise ValueError(f"Invalid regex condition format: {regex_condition}. Use 'c:<regex>' or 'n:<regex>'.")
    
def apply_regex(logs, regex_conditions):
    """
    Applies the given regex conditions to the logs and returns the filtered logs.
    """
    import re

    filtered_logs = []
    
    for log in logs:
        if all(passes_regex(log, cond) for cond in regex_conditions):
            filtered_logs.append(log)
    
    return filtered_logs 




if __name__ == '__main__':
    main()