import re
import argparse
from collections import defaultdict
from flask import Flask, jsonify
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


log_filename = None

def parse_log_file(filename):
    parsed_lines = []
    function_numbers = defaultdict(lambda: len(function_numbers))
    current_line = ""
    
    with open(filename, 'r') as file:
        for line in file:
            if line.strip().startswith("@log"):
                if current_line:
                    # Parse the accumulated line
                    match = re.search(r'(@autolog|@locallog)?\s*Function\s+(\w+)', current_line)
                    if match:
                        log_type, function_name = match.groups()
                        log_type = log_type or ''
                        function_number = function_numbers[function_name]
                        parsed_lines.append((current_line.strip(), log_type, function_number))
                    else:
                        parsed_lines.append((current_line.strip(), '', -1))
                
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
                parsed_lines.append((current_line.strip(), log_type, function_number))
            else:
                parsed_lines.append((current_line.strip(), '', -1))
    
    return parsed_lines




@app.route('/logs')
def get_logs():
    if log_filename:
        parsed_lines = parse_log_file(log_filename)
        return jsonify(parsed_lines)
    else:
        return jsonify({"error": "No log file specified"}), 400





def check_latest_log():
    global log_filename
    latest_log_path = "latest_log_name.txt"
    while True:
        if os.path.exists(latest_log_path):
            with open(latest_log_path, 'r') as file:
                new_content = file.read().strip()
                if new_content != log_filename:
                    log_filename = new_content
                    print(f"Now showing log file: {log_filename}")
        else:
            log_filename = None
            print("Warning: No 'latest_log_name.txt' file found.")
        time.sleep(1)

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Log File Parser Server')

    # if no argument is provided, log_file will be None
    parser.add_argument('log_file', type=str, help='Path to the log file', nargs='?')
    args = parser.parse_args()



    if args.log_file != None:
        log_filename = args.log_file

    # If no log file is provided, check for a 'latest_log_name.txt' file
    # and update log_filename to what it contains.
    # Keeps checking it every second and notifies us when the file changed.
    else:
        # print("here1")
        latest_log_path = "latest_log_name.txt"
        if os.path.exists(latest_log_path):
            with open(latest_log_path, 'r') as file:
                log_filename = file.read().strip()
        else:
            print("Warning: No 'latest_log_name.txt' file found.")
        
        # This creates some weird behaviour, so I would rather do it differently.
        # But right now it is working okay, so I will leave it.
        # Start the background thread to check for updates
        Thread(target=check_latest_log).start()
        # print("here")
            
    
    # This blocks execution.
    app.run(debug=True, port=5000)

