import re
import argparse
from collections import defaultdict
from flask import Flask, jsonify
from flask_cors import CORS

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

"""def parse_log_file(filename):
    parsed_lines = []
    function_numbers = defaultdict(lambda: len(function_numbers))
    
    with open(filename, 'r') as file:
        for line in file:
            match = re.search(r'(@autolog|@locallog)?\s*Function\s+(\w+)', line)
            if match:
                log_type, function_name = match.groups()
                log_type = log_type or ''
                function_number = function_numbers[function_name]
                parsed_lines.append((line.strip(), log_type, function_number))
            else:
                parsed_lines.append((line.strip(), '', -1))
    
    return parsed_lines"""

@app.route('/logs')
def get_logs():
    if log_filename:
        parsed_lines = parse_log_file(log_filename)
        return jsonify(parsed_lines)
    else:
        return jsonify({"error": "No log file specified"}), 400

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Log File Parser Server')
    parser.add_argument('log_file', type=str, help='Path to the log file')
    args = parser.parse_args()

    log_filename = args.log_file

    app.run(debug=True)