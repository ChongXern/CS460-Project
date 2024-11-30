import json
import math

def convert_timestamps_in_json(json_filepath):
    with open(json_filepath, 'r') as file:
        data = json.load(file)
    
    if math.floor(data["fullstop_timestamps"][0]) != 0:
        exit()
    
    for i in range(len(data["fullstop_timestamps"])):
        # Parse timestamp from decimal into seconds
        timestamp = data["fullstop_timestamps"][i]
        minute = math.floor(timestamp)
        second = 100 * (timestamp - minute)
        new_timestamp = math.ceil(minute * 60 + second)
        data["fullstop_timestamps"][i] = new_timestamp
    
    with open(json_filepath, 'w') as file:
        json.dump(data, file, ensure_ascii=False, indent=4)

def check_valid(json_filepath):
    with open(json_filepath, 'r') as file:
        data = json.load(file)
    prev_timestamp = data["fullstop_timestamps"][0]
    for i in range(1, len(data["fullstop_timestamps"])):
        curr_timestamp = data["fullstop_timestamps"][i]
        if prev_timestamp >= curr_timestamp:
            print(f"Check at {curr_timestamp}")
            return False
        if curr_timestamp - math.floor(curr_timestamp) >= 0.6:
            print(f"{curr_timestamp} has out of bounds seconds")
            return False
        prev_timestamp = curr_timestamp
    return True

json_filepath = input("INPUT JSON FILE: ")
mode = input("Check order? ")
if mode.lower() == 'y':
    is_in_order = check_valid(f"lectures/{json_filepath}.json")
    print(f"Is timestamp array ascending? {is_in_order}")
if is_in_order:
    convert_timestamps_in_json(f"lectures/{json_filepath}.json")