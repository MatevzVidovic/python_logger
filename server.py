import re
import argparse
from collections import defaultdict
from flask import Flask, jsonify, request
from flask_cors import CORS
import time
import os
from threading import Thread
import threading



# ------------------------------------------------------------------------------

# !!!!!!!!!! This creates some weird behaviour.
# This is a probable cause of issues.
# Thread(target=check_latest_log).start()



# ------------------------------------------------------------------------------



app = Flask(__name__)
CORS(app)





import signal
import sys

# Event to signal threads to stop
stop_event = threading.Event()

def signal_handler(sig, frame):
    print("SIGINT received, stopping threads...")
    stop_event.set()
    sys.exit(0)










LOG_FILE_PATH = None
LOG_FILE_LINE_COUNT = 0
CHECK_LINE_COUNT = True
PARSED_LINES = []
PREVIOUS_REQUIRED_REGEXS = []
REQUIRED_REGEXS = []
CHECK_LATEST_LOG_PATH = False


# This is efficient, because it is a generator expression, so it does not actually read the file into memory.
def count_lines(file_path):
    if file_path == None:
        return 0
    with open(file_path, 'r') as file:
        return sum(1 for line in file)

def parse_log_file():
    global LOG_FILE_PATH
    global PARSED_LINES
    function_numbers = defaultdict(lambda: len(function_numbers))
    current_line = ""

    PARSED_LINES = []
    
    with open(LOG_FILE_PATH, 'r') as file:
        for line in file:
            if line.strip().startswith("@log"):
                if current_line:
                    # Parse the accumulated line
                    match = re.search(r'(@autolog|@locallog)?\s*Function\s+(\w+)', current_line)
                    if match:
                        log_type, function_name = match.groups()
                        log_type = log_type or ''
                        function_number = function_numbers[function_name]
                        PARSED_LINES.append((current_line.strip(), log_type, function_number))
                    else:
                        PARSED_LINES.append((current_line.strip(), '', -1))
                
                # Reset current_line and start accumulating the new line
                current_line = line.strip() + "\n "
            else:
                # Concatenate lines, adding a space after each newline
                current_line += line.rstrip() + " \n "
        
        # Process the last line if it exists
        if current_line:
            match = re.search(r'(@autolog|@locallog)?\s*Function\s+(\w+)', current_line)
            if match:
                log_type, function_name = match.groups()
                log_type = log_type or ''
                function_number = function_numbers[function_name]
                PARSED_LINES.append((current_line.strip(), log_type, function_number))
            else:
                PARSED_LINES.append((current_line.strip(), '', -1))
    

    # remove all lines that do not contain the required content
    # line[0] is the text of the parsed line
    new_PARSED_LINES = []
    if REQUIRED_REGEXS != []:
        for line in PARSED_LINES:
            is_okay = True
            for regex, contain in REQUIRED_REGEXS:
                if contain:
                    if not re.search(regex, line[0]):
                        is_okay = False
                        break
                else:
                    if re.search(regex, line[0]):
                        is_okay = False
                        break
            
            if is_okay:
                new_PARSED_LINES.append(line)
            
            
        PARSED_LINES = new_PARSED_LINES

    return


def paginate_lines(lines, page, page_size):
    return lines[(page - 1) * page_size: page * page_size]


@app.route('/logs')
def get_logs():

    global CHECK_LINE_COUNT

    if LOG_FILE_PATH:
        page = request.args.get('page', 1, type=int)
        per_page = request.args.get('per_page', 10, type=int)
        returning_JSON = jsonify(paginate_lines(PARSED_LINES, page, per_page))
        # To trigger possible update of log file, if lines have been added.
        CHECK_LINE_COUNT = True
        return returning_JSON
    else:
        return jsonify({"error": "No log file specified"}), 400


@app.route('/required_regexs', methods=['POST'])
def update_required_regexs():
    global REQUIRED_REGEXS

    # Check if the request contains JSON data
    if request.is_json:
        # Extract the JSON data
        data = request.get_json()
        regexs = data.get('regexs', [])

        new_required_regexs = []
        for regex in regexs:
            new_required_regexs.append((regex["regex"], regex["contain"]))
        
        REQUIRED_REGEXS = new_required_regexs
        
        # Return a success response
        return jsonify({"message": "Contents received successfully", "regexs": REQUIRED_REGEXS}), 200
    else:
        # Return an error response if the content type is not JSON
        return jsonify({"error": "Request must be JSON"}), 400


CHECK_ITERS = 0

def check_latest_log_and_required_regexs():
    global LOG_FILE_PATH
    global PREVIOUS_REQUIRED_REGEXS
    global REQUIRED_REGEXS

    global CHECK_ITERS
    global CHECK_LINE_COUNT
    global LOG_FILE_LINE_COUNT
    
    logs_folder = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'logs')
    latest_log_path = os.path.join(logs_folder, "latest_log_name.txt")

    while True:
        
        # When sigint is received, stop the thread
        if stop_event.is_set():
            return

        do_parse = False

        if CHECK_LATEST_LOG_PATH:
            if os.path.exists(latest_log_path):
                with open(latest_log_path, 'r') as file:
                    new_content = file.read().strip()
                    new_content = os.path.join(logs_folder, new_content)
                    if new_content != LOG_FILE_PATH:
                        LOG_FILE_PATH = new_content
                        print(f"Now showing log file: {LOG_FILE_PATH}")
                        do_parse = True
            else:
                LOG_FILE_PATH = None
                print("Warning: No 'latest_log_name.txt' file found.")


        if PREVIOUS_REQUIRED_REGEXS != REQUIRED_REGEXS:
            PREVIOUS_REQUIRED_REGEXS = REQUIRED_REGEXS
            print(f"New required content: {REQUIRED_REGEXS}")
            do_parse = True
        


        # If a refresh request is made, right after it we go refresh the parsed lines.
        # (We don't do this at the time of the request, because it might take a while to parse the log file and a the request then fails, and error is sent.)
        # Check for this every k seconds anyway.
        if CHECK_LINE_COUNT or CHECK_ITERS % 10 == 0:
            CHECK_ITERS = 0
            CHECK_LINE_COUNT = False
            new_line_count = count_lines(LOG_FILE_PATH)
            if new_line_count != LOG_FILE_LINE_COUNT:
                LOG_FILE_LINE_COUNT = new_line_count
                print(f"New line count: {LOG_FILE_LINE_COUNT}")
                do_parse = True
        
        if do_parse:
            parse_log_file()


        # print(len(PARSED_LINES))

        CHECK_ITERS += 1

        time.sleep(1)



if __name__ == '__main__':

    signal.signal(signal.SIGINT, signal_handler)

    parser = argparse.ArgumentParser(description='Log File Parser Server')

    # if no argument is provided, log_file will be None
    parser.add_argument('log_file', type=str, help='Name of log file', nargs='?')
    args = parser.parse_args()

    # Start the background thread to check for updates
    Thread(target=check_latest_log_and_required_regexs).start()

    logs_folder = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'logs')

    if args.log_file != None:
        log_filename = args.log_file
        LOG_FILE_PATH = os.path.join(logs_folder, log_filename)
        parse_log_file()


    # If no log file is provided, check for a 'latest_log_name.txt' file
    # and update log_filename to what it contains.
    # Keeps checking it every second and notifies us when the file changed.
    else:
        CHECK_LATEST_LOG_PATH = True
        latest_log_path = os.path.join(logs_folder, "latest_log_name.txt")
        if os.path.exists(latest_log_path):
            with open(latest_log_path, 'r') as file:
                log_filename = file.read().strip()
                LOG_FILE_PATH = os.path.join(logs_folder, log_filename)
                LOG_FILE_LINE_COUNT = count_lines(LOG_FILE_PATH)
                parse_log_file()
        else:
            print("Warning: No 'latest_log_name.txt' file found.")
    
    print("Now showing log file: ", LOG_FILE_PATH)
    

    # testing comm
            
    
    # This blocks execution.
    app.run(debug=True, port=5000)

