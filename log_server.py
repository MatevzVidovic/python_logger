import re
import argparse
from collections import defaultdict
from flask import Flask, jsonify, request
from flask_cors import CORS
import time
import os
from threading import Thread




# ------------------------------------------------------------------------------

# !!!!!!!!!! This creates some weird behaviour.
# This is a probable cause of issues.
# Thread(target=check_latest_log).start()



# ------------------------------------------------------------------------------



app = Flask(__name__)
CORS(app)


LOG_FILE_PATH = None
PARSED_LINES = []
PREVIOUS_REQUIRED_CONTENT = ""
REQUIRED_CONTENT = ""
CHECK_LATEST_LOG_PATH = False

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
    if REQUIRED_CONTENT != "":
        PARSED_LINES = [line for line in PARSED_LINES if REQUIRED_CONTENT in line[0]]
    
    return


def paginate_lines(lines, page, page_size):
    return lines[(page - 1) * page_size: page * page_size]


@app.route('/logs')
def get_logs():
    if LOG_FILE_PATH:
        page = request.args.get('page', 1, type=int)
        per_page = request.args.get('per_page', 10, type=int)
        return jsonify(paginate_lines(PARSED_LINES, page, per_page))
    else:
        return jsonify({"error": "No log file specified"}), 400


@app.route('/required_content', methods=['POST'])
def update_required_content():
    global REQUIRED_CONTENT
    data = request.json
    if 'content' in data:
        REQUIRED_CONTENT = data['content']
        return jsonify({"message": "REQUIRED_CONTENT updated successfully", "REQUIRED_CONTENT": REQUIRED_CONTENT}), 200
    else:
        return jsonify({"error": "No content provided"}), 400




def check_latest_log_and_required_content():
    global LOG_FILE_PATH
    global PREVIOUS_REQUIRED_CONTENT
    global REQUIRED_CONTENT
    
    logs_folder = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'logs')
    latest_log_path = os.path.join(logs_folder, "latest_log_name.txt")

    while True:

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


        if PREVIOUS_REQUIRED_CONTENT != REQUIRED_CONTENT:
            PREVIOUS_REQUIRED_CONTENT = REQUIRED_CONTENT
            print(f"New required content: {REQUIRED_CONTENT}")
            do_parse = True
        
        if do_parse:
            parse_log_file()



        time.sleep(1)



if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Log File Parser Server')

    # if no argument is provided, log_file will be None
    parser.add_argument('log_file', type=str, help='Name of log file', nargs='?')
    args = parser.parse_args()

    # Start the background thread to check for updates
    Thread(target=check_latest_log_and_required_content).start()

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
        # print("here1")
        latest_log_path = os.path.join(logs_folder, "latest_log_name.txt")
        if os.path.exists(latest_log_path):
            with open(latest_log_path, 'r') as file:
                log_filename = file.read().strip()
                LOG_FILE_PATH = os.path.join(logs_folder, log_filename)
                parse_log_file()
        else:
            print("Warning: No 'latest_log_name.txt' file found.")
 
            
    
    # This blocks execution.
    app.run(debug=True, port=5000)

