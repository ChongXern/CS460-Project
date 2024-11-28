import json
import math

def convert_timestamps_in_json(json_filepath):
    with open(json_filepath, 'r') as file:
        data = json.load(file)
    
    if math.floor(data["transitions"][0]) != 0:
        exit()
    
    for i in range(len(data["transitions"])):
        # Parse timestamp from decimal into seconds
        timestamp = data["transitions"][i]
        minute = math.floor(timestamp)
        second = 100 * (timestamp - minute)
        new_timestamp = math.ceil(minute * 60 + second)
        data["transitions"][i] = new_timestamp
    
    with open(json_filepath, 'w') as file:
        json.dump(data, file, ensure_ascii=False, indent=4)

json_filepath = input("INPUT JSON FILE: ")
convert_timestamps_in_json(f"lectures/{json_filepath}")