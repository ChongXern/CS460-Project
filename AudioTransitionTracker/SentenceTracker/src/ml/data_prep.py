import json
import os
import os.path
import numpy as np
import librosa
import sys
from sklearn.model_selection import train_test_split
from utils import load_json_files

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

def generate_spectrogram_array(audio_filepath, start_time, duration, is_full):
    y, sr = librosa.load(audio_filepath)
    print(f"Audio data loaded: {audio_filepath}, Duration: {len(y)} samples, Sample Rate: {sr}")  # Debugging print
    if not is_full:
        start_sample = int(int(start_time * sr) /1000)
        end_sample = int(int((start_time + duration) * sr) /1000)
        print(f"Slicing audio: start_sample = {start_sample}, end_sample = {end_sample}")  # Debugging print
        y = y[start_sample:end_sample]
    D = librosa.stft(y)
    S_db = librosa.amplitude_to_db(abs(D), ref=np.max)
    return S_db.T

def get_surrounding_segments(item, data, spectrogram_dir):
    """Fetches spectrograms for the preceding, current, and succeeding segments."""
    # Check the 'item['name']' format
    print(f"Processing item: {item['name']}")  # Debugging print

    # Split the filename to get video_id, start_time, end_time
    try:
        video_id = item['name'][:11]
        parts = item['name'][12:].split('_')
        
        if len(parts) == 2:
            start_time = int(parts[0])
            end_time = int(parts[1])
        else:
            raise ValueError("Filename format is incorrect. Expected: {video_id}_{start_time}_{end_time}")
        
        print(f"{video_id}, {start_time}, {end_time}")
    except ValueError:
        print(f"Skipping item due to unexpected format: {item['name']}")
        return None  # Skip this item if the format is unexpected

    def load_spectrogram(video_id, start, end):
        filepath = os.path.join(spectrogram_dir, f"{video_id}_{start}_{end}.json")
        print(f"Loading spectrogram: {filepath}")  # Debugging print
        if os.path.exists(filepath):
            with open(filepath, 'r') as file:
                data = json.load(file)
            try:
                # Generate spectrogram array
                return pad_or_truncate_spectrogram(generate_spectrogram_array(
                    audio_filepath=f"../../data/audio_files/audio_{video_id}.mp3",
                    start_time=int(data["start_time"]),
                    duration=int(data["duration"]),
                    is_full=data["is_full"]
                ))
            except Exception as e:
                print(f"Error generating spectrogrm for {filepath}: {e}")
                return None
        else:
            print(f"Spectrogram file not found: {filepath}")
            return None


    # Check if preceding spectrogram exists
    preceding_filename = f"../../data/lectures_segments/json/{video_id}_{start_time - 5000}_{start_time}.json"
    if not os.path.exists(preceding_filename):
        print(f"No preceding file for {item['name']}, skipping")
        print(f"Couldn't find filename: {preceding_filename}")
        return None
    else:
        preceding = load_spectrogram(video_id, start_time - 5000, start_time)
        if preceding is None:
            print(f"No preceding file for {item['name']}, skipping")
            return None

    # Check if succeeding spectrogram exists
    succeeding_filename = f"../../data/lectures_segments/json/{video_id}_{end_time}_{end_time + 5000}.json"
    if not os.path.exists(succeeding_filename):
        print(f"No succeeding file for {item['name']}, skipping")
        return None  # Skip this segment if no succeeding segment exists
    else:
        succeeding = load_spectrogram(video_id, end_time, end_time + 5000)
        if succeeding is None:
            print(f"No succeeding file for {item['name']}, skipping")
            return None  # Skip this segment if succeeding segment is missing

    current = load_spectrogram(video_id, start_time, end_time)
    if current is None:
        print(f"No current file for {item['name']}, skipping")
        return None  # Skip if the current segment is missing

    final_spectrogram_array = np.concatenate([preceding, current, succeeding], axis=0)  # Shape: (648, 1025)
    print(f"SHAPE: {final_spectrogram_array.shape}")
    return final_spectrogram_array

def extract_features_and_labels(data, checkpoint_path="checkpoint.npz"):
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

    for i, item in enumerate(data[start_index:], start=start_index):
        print(f"Processing item {i + 1}/{len(data)}: {item['name']}")
        try:
            json_directory = "../../data/lectures_segments/json"
            extended_spectrogram = get_surrounding_segments(item, data, json_directory)
            if extended_spectrogram is None:
                continue  # Skip if no valid surrounding spectrograms are found
            X.append(extended_spectrogram[..., np.newaxis])  # Add channel dimension
            # Label only for the middle segment
            has_fullstop = any(
                item['start_time'] <= ts < (item['start_time'] + item['duration'])
                for ts in item['fullstop_timestamps']
            )
            y.append(1 if has_fullstop else 0)
            # Save checkpoint
            np.savez(checkpoint_path, X=np.array(X), y=np.array(y), start_index=i + 1)
            # animate_loading_bar(len(data), i + 1)
        except Exception as e:
            print(f"Error processing {item['name']}: {e}")

    return np.array(X), np.array(y)

if __name__ == "__main__":
    json_dir = "../../data/lectures_segments/json"
    json_data = load_json_files(json_dir)
    print(f"Total data: {len(json_data)}")
    X, y = extract_features_and_labels(json_data)
    if X.size == 0:
        print("No valid data found after processing, exiting.")
        exit()  # Exit if no valid data was found

    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)
    np.savez('../../data/npz/fullstop_prediction_train.npz', X_train=X_train, y_train=y_train)
    np.savez('../../data/npz/fullstop_prediction_test.npz', X_test=X_test, y_test=y_test)
    print("Datasets saved successfully!")
