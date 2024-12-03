import json
import os
import numpy as np
import librosa
import sys

from utils import load_json_files
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import LabelEncoder

def animate_loading_bar(total, curr, bar_length=60):
    percentage = curr / total
    filled_length = int(bar_length * percentage)
    
    bar = '#' * filled_length + '-' * (bar_length - filled_length)

    sys.stdout.write(f"\r|{bar}| {100 * percentage:.2f}% ")
    sys.stdout.flush()

def pad_or_truncate_spectrogram(S, target_shape=(862, 1025)):
    """Pads or truncates the spectrogram S to match the target shape."""
    target_rows, target_cols = target_shape
    
    # Pad or truncate rows (time frames)
    if S.shape[0] < target_rows:
        padding_rows = target_rows - S.shape[0]
        S = np.pad(S, ((0, padding_rows), (0, 0)), mode='constant')
    elif S.shape[0] > target_rows:
        S = S[:target_rows, :]
    
    # Ensure the number of columns (frequency bins) is exactly target_cols
    if S.shape[1] < target_cols:
        padding_cols = target_cols - S.shape[1]
        S = np.pad(S, ((0, 0), (0, padding_cols)), mode='constant')
    elif S.shape[1] > target_cols:
        S = S[:, :target_cols]
    
    return S

def generate_spectrogram_array(item):
    json_filename = item["name"]
    
    directory = "../../data/lectures_segments/json_test"
    filepath = f"{directory}/{json_filename}.json"
    
    print(f"Reading JSON from: {filepath}")
    
    if "_h30HBYxtws" in filepath:
        audio_filepath = "../../data/audio_files/audio__h30HBYxtws.mp3"
    elif "4PkKI_S9TIQ" in filepath:
        audio_filepath = "../../data/audio_files/audio_4PkKI_S9TIQ.mp3"
    else:
        audio_filepath = f"../../data/audio_files/audio_{json_filename.split('_')[0]}.mp3"
    
    with open(filepath, 'r') as file:
        data = json.load(file)
    
    start_time = data["start_time"]
    duration = data["duration"]
    if start_time > 1000 or duration > 1000:
        start_time /= 1000
        duration /= 1000

    print(f"start time is {start_time} and duration is {duration}")
    y, sr = librosa.load(audio_filepath)

    if not data["is_full"]: # usually the case
        start_sample = int(start_time * sr)
        end_sample = int((start_time + duration) * sr)
        if end_sample > len(y):
            end_sample = len(y)
        y = y[start_sample:end_sample]
        # self.duration = duration
    else:
        print("AudioLecture object is full, try again")
        exit()

    D = librosa.stft(y)
    S_db = librosa.amplitude_to_db(abs(D), ref=np.max)

    return S_db.T

def extract_features_and_labels(data):
    X = []
    y = []
    
    for i, item in enumerate(data):
        print(f"Item is {item}")
        spectrogram_data = generate_spectrogram_array(item)
        X.append(spectrogram_data)
        
        # Create label: 1 if full stop exists within segment, 0 otherwise
        has_fullstop = any(item['start_time'] <= ts < (item['start_time'] + item['duration'])
                           for ts in item['fullstop_timestamps'])
        y.append(1 if has_fullstop else 0)
        
        animate_loading_bar(len(data), i + 1)
    
    return np.array(X), np.array(y)

def save_datasets(X_train, X_test, y_train, y_test):
    np.savez('audio_data_train.npz', X_train=X_train, y_train=y_train)
    np.savez('audio_data_test.npz', X_test=X_test, y_test=y_test)
    print("Datasets saved successfully!")

if __name__ == "__min__":
    json_dir = "../../data/lectures_segments/json_test"
    json_data = load_json_files(json_dir)
    print(f"total data is {len(json_data)}")
    X, y = extract_features_and_labels(json_data)
    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)
    save_datasets(X_train, X_test, y_train, y_test)
    

if __name__ == "__main__":
    #json_file = input("INPUT JSON FILE: ")
    item = {
        'name': 'p9yZNLeOj4s_253800_263800',
        'url': 'https://www.youtube.com/watch?v=p9yZNLeOj4s',
        'audio_filepath': '../../data/audio_files/audio_p9yZNLeOj4s.mp3',
        'spectrogram_filepath': '../../data/spectrograms/p9yZNLeOj4s.png',
        'start_time': 253800,  # in milliseconds
        'duration': 10000,     # in milliseconds
        'is_full': False,
        'fullstop_timestamps': []
    }
    spectrogram = generate_spectrogram_array(item)
    print(f"Spectrogram: {spectrogram}")
    print(f"Spectrogram shape: {spectrogram.shape}")
