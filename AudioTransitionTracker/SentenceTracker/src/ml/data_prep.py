import json
import os
import numpy as np
import librosa
import sys
from sklearn.model_selection import train_test_split
from utils import load_json_files

def animate_loading_bar(total, curr, bar_length=60):
    percentage = curr / total
    filled_length = int(bar_length * percentage)
    bar = '#' * filled_length + '-' * (bar_length - filled_length)
    sys.stdout.write(f"\r|{bar}| {100 * percentage:.2f}% ")
    sys.stdout.flush()

def pad_or_truncate_spectrogram(S, target_shape=(216, 1025)):
    target_rows, target_cols = target_shape
    if S.shape[0] < target_rows:
        padding_rows = target_rows - S.shape[0]
        S = np.pad(S, ((0, padding_rows), (0, 0)), mode='constant')
    elif S.shape[0] > target_rows:
        S = S[:target_rows, :]
    if S.shape[1] < target_cols:
        padding_cols = target_cols - S.shape[1]
        S = np.pad(S, ((0, 0), (0, padding_cols)), mode='constant')
    elif S.shape[1] > target_cols:
        S = S[:, :target_cols]
    return S

def generate_spectrogram_array(item):
    json_filename = item["name"]
    directory = "../../data/lectures_segments/json"
    filepath = f"{directory}/{json_filename}.json"
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
    y, sr = librosa.load(audio_filepath)
    if not data["is_full"]:
        start_sample = int(start_time * sr)
        end_sample = int((start_time + duration) * sr)
        if end_sample > len(y):
            end_sample = len(y)
        y = y[start_sample:end_sample]
    else:
        print("AudioLecture object is full, try again")
        exit()
    D = librosa.stft(y)
    S_db = librosa.amplitude_to_db(abs(D), ref=np.max)
    return S_db.T

def extract_features_and_labels(data, checkpoint_path="checkpoint.npz"):
    # Load checkpoint if exists
    if os.path.exists(checkpoint_path):
        checkpoint = np.load(checkpoint_path)
        X = checkpoint["X"].tolist()
        y = checkpoint["y"].tolist()
        start_index = checkpoint["start_index"].item()
        print(f"Resuming from checkpoint: {start_index}/{len(data)}")
    else:
        X = []
        y = []
        start_index = 0

    # Process data
    for i, item in enumerate(data[start_index:], start=start_index):
        print(f"Processing item {i + 1}/{len(data)}: {item['name']}")
        try:
            spectrogram_data = generate_spectrogram_array(item)
            processed_spectrogram = pad_or_truncate_spectrogram(spectrogram_data, target_shape=(216, 1025))
            X.append(processed_spectrogram)
            has_fullstop = any(
                item['start_time'] <= ts < (item['start_time'] + item['duration'])
                for ts in item['fullstop_timestamps']
            )
            y.append(1 if has_fullstop else 0)

            # Save checkpoint
            np.savez(checkpoint_path, X=np.array(X), y=np.array(y), start_index=i + 1)
            animate_loading_bar(len(data), i + 1)
        except Exception as e:
            print(f"Error processing {item['name']}: {e}")

    return np.array(X), np.array(y)

if __name__ == "__main__":
    json_dir = "../../data/lectures_segments/json"
    json_data = load_json_files(json_dir)
    print(f"Total data: {len(json_data)}")
    X, y = extract_features_and_labels(json_data)
    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)
    np.savez('../../data/npz/fullstop_prediction_train.npz', X_train=X_train, y_train=y_train)
    np.savez('../../data/npz/fullstop_prediction_test.npz', X_test=X_test, y_test=y_test)
    print("Datasets saved successfully!")
