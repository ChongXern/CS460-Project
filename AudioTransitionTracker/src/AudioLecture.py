import json
import yt_dlp
import os
import librosa
import librosa.display
import matplotlib.pyplot as plt
import numpy as np
import math
import copy

class AudioLecture:
    def __init__(self, name, url, audio_filepath, spectrogram_filepath, duration, fullstop_timestamps, start_time=0, is_full=True):
        self.name = name
        self.url = url
        self.audio_filepath = audio_filepath
        self.spectrogram_filepath = spectrogram_filepath
        self.start_time = start_time
        self.duration = duration
        self.fullstop_timestamps = fullstop_timestamps
        self.is_full = is_full

    def __repr__(self):
        return f"AudioLecture(name={self.name}, duration={self.duration} min, fullstop_timestamps={self.fullstop_timestamps})"
    
    def to_json(self, json_filepath):
        data = {
            'name': self.name,
            'url': self.url,
            'audio_filepath': self.audio_filepath,
            'spectrogram_filepath': self.spectrogram_filepath,
            'start_time': self.start_time,
            'duration': self.duration,
            'is_full': self.is_full,
            'fullstop_timestamps': self.fullstop_timestamps
        }
        with open(json_filepath, 'w') as file:
            json.dump(data, file, indent=4)
        print(f"JSON saved to {json_filepath}")

    def extract_audio_from_youtube(video_url, filename):
        video_id = video_url.split('=')[-1]
        audio_filename = f"audio_{video_id}"
        output_path = os.path.join(filename, audio_filename)
        os.makedirs(filename, exist_ok=True)

        ydl_opts = {
            'format': 'bestaudio/best',
            'noplaylist': True,
            'outtmpl': output_path,
            'postprocessors': [{
                'key': 'FFmpegExtractAudio',
                'preferredcodec': 'mp3',
                'preferredquality': '192',
            }],
            'quiet': True,
            'cookiesfrombrowser': ('chrome',),
        }

        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            ydl.download([video_url])

        print(f"Audio saved to {output_path}")
        return output_path

    def generate_spectrogram(self, audio_filepath, output_image_path):
        #differentiating attributes for full or segment
        start_time = self.start_time
        duration = self.duration
        
        spectrogram_filepath = output_image_path
        open(spectrogram_filepath, "w").close()
        y, sr = librosa.load(audio_filepath)
        #print(f"waveform: {y} & sampling rate: {sr}")
        if self.is_full:
            self.duration = math.floor(librosa.get_duration(y=y, sr=sr))
        else:
            start_sample = int(start_time * sr)
            end_sample = int((start_time + duration) * sr)
            if end_sample > len(y):
                end_sample = len(y)
            y = y[start_sample:end_sample]
            self.duration = duration
        
        D = librosa.stft(y)
        S_db = librosa.amplitude_to_db(abs(D), ref=np.max)

        # Plotting the spectrogram
        plt.figure(figsize=(10, 4))
        time_axis = np.linspace(start_time, start_time + self.duration, S_db.shape[-1])
        librosa.display.specshow(S_db, sr=sr, x_axis='time', y_axis='log', cmap='coolwarm', x_coords=time_axis)
        plt.colorbar(format='%+2.0f dB')
        plt.title(f'Spectrogram for {self.name}')
        plt.tight_layout()
        plt.savefig(output_image_path)
        plt.close()

def create_new_audio_lecture(video_url):
    output_dir = "audio_files"
    json_dir = "json_lectures"
    spectrogram_dir = "spectrograms"

    audio_filepath = AudioLecture.extract_audio_from_youtube(video_url, output_dir)

    duration = 0
    fullstop_timestamps = []
    name = video_url.split('=')[-1]

    os.makedirs(spectrogram_dir, exist_ok=True)
    output_image_path = os.path.join(spectrogram_dir, f"{name}.png")
    
    # Create AudioLecture instance
    audio_lecture = AudioLecture(
        name=name,
        url=video_url,
        audio_filepath=audio_filepath,
        spectrogram_filepath=None,  # Placeholder for now
        duration=duration,
        fullstop_timestamps=fullstop_timestamps
    )

    audio_lecture.generate_spectrogram(f"{audio_filepath}.mp3", output_image_path)
    audio_lecture.spectrogram_filepath = output_image_path  # Update the spectrogram filepath
    
    os.makedirs(json_dir, exist_ok=True)
    json_path = os.path.join(json_dir, f"{name}.json")
    audio_lecture.to_json(json_path)

    print(audio_lecture)

def convert_timestamp_to_ms(timestamp):
    minute = math.floor(timestamp)
    second = 100 * (timestamp - minute)
    return math.ceil(minute * 60 + second) * 1000

def parse_audio_lecture_from_json(json_filepath):
    with open(json_filepath, 'r') as file:
        data = json.load(file)
    
    # create parsed audiolecture object
    parsed_audio_lecture = AudioLecture(
        name = data["name"],
        url = data["url"],
        audio_filepath = data["audio_filepath"],
        spectrogram_filepath = data["spectrogram_filepath"],
        start_time = data["start_time"],
        duration = data["duration"],
        fullstop_timestamps = data["fullstop_timestamps"],
        is_full = data["is_full"]
    )
    
    return parsed_audio_lecture

#assume start_time is in decimals
def segment_audio_lecture(audioLecture: AudioLecture, start_time, duration):
    #should return new audioLecture
    name = audioLecture.name
    json_file = f"json_lectures/{name}.json"
    with open(json_file, 'r') as file:
        data = json.load(file)
    
    new_audio_lecture = copy.copy(audioLecture)
    
    # segment timestamp array based on start time and end time
    start_time_ms = convert_timestamp_to_ms(start_time)
    duration_ms = convert_timestamp_to_ms(duration)
    fullstop_timestamps = data["fullstop_timestamps"]
    new_timestamps_array = []
    
    for timestamp in fullstop_timestamps:
        if timestamp >= start_time_ms + duration_ms:
            break
        if timestamp + 2 > start_time_ms:
            new_timestamps_array.append(timestamp)
    
    new_audio_lecture.name = f"{name}_{str(start_time)}_{str(start_time + duration)}"
    new_audio_lecture.start_time = start_time_ms
    new_audio_lecture.duration = duration_ms
    new_audio_lecture.is_full = False
    new_audio_lecture.generate_spectrogram(f"{audioLecture.audio_filepath}.mp3", f"lectures_segments/spectrograms/{new_audio_lecture.name}.png")
    new_audio_lecture.fullstop_timestamps = new_timestamps_array
    
    #create json file
    new_audio_lecture.to_json(f"lectures_segments/json/{new_audio_lecture.name}.json")
    print("Segmented audio lecture")

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

if __name__ == "__main2__":
    existing_urls = load_urls("urls.txt")
    video_url = input("Input URL: ")
    if video_url in existing_urls:
        print("URL already converted into AudioLecture object")
    else:
        create_new_audio_lecture(video_url)
        existing_urls.add(video_url)
        save_url("urls.txt", video_url)
        print("URL saved, converting to AudioLecture")
else:
    json_file = "json_lectures/4PkKI_S9TIQ.json"
    audioLecture = parse_audio_lecture_from_json(json_file)
    segment_audio_lecture(audioLecture, 2, 1)
    #audioLecture.generate_spectrogram("audio_files/audio_4PkKI_S9TIQ.mp3", "lectures_segments/spectrograms/4PkKI_S9TIQ.png")
