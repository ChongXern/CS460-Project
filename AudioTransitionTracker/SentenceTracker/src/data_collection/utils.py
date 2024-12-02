import math
import sys
import time

def convert_timestamp_to_ms(timestamp):
    minute = math.floor(timestamp)
    second = 100 * (timestamp - minute)
    return math.ceil(minute * 60 + second) * 1000

def load_urls(filename):
    try:
        with open(filename, 'r') as file:
            return {line.strip() for line in file}
    except FileNotFoundError:
        return set()

def save_url(filename, user_input):
    """Append a new input to the specified file."""
    with open(filename, 'a') as file:
        file.write(user_input + '\n')

def extract_id_from_url(video_url):
    return video_url.split('=')[-1]

def create_item_from_id(video_id, mode):
    #switch case for url, spectrogram_file, audio_filepath
    # print("Available Modes:\nU: URL\nS: Spectrogram filepath\nA: Audio filepath\n")
    match mode:
        case "u":
            return f"https://www.youtube.com/watch?v={video_id}"
        case "s":
            return f"../../data/spectrograms/{video_id}.png"
        case "a":
            return f"../../data/audio_files/audio_{video_id}.mp3"
        case _:
            return "Invalid id-to-format mode"

def animate_loading_bar(total, curr, bar_length=60):
    percentage = curr / total
    filled_length = int(bar_length * percentage)
    
    bar = '#' * filled_length + '-' * (bar_length - filled_length)

    sys.stdout.write(f"\r|{bar}| {100 * percentage:.2f}%")
    sys.stdout.flush()
