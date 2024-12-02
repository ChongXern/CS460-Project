import json
import math
import librosa
import librosa.display
import matplotlib.pyplot as plt
import numpy as np
import os
import yt_dlp
import matplotlib.ticker as mticker

from utils import extract_id_from_url

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
        #print(f"new audio lecture duration: {data['duration']}"),
        with open(json_filepath, 'w') as file:
            json.dump(data, file, indent=4)
        #print(f"JSON saved to {json_filepath}")

    def extract_audio_from_youtube(video_url, filename):
        video_id = extract_id_from_url(video_url)
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
        if start_time > 1000 or duration > 1000:  # Convert ms to s
            start_time /= 1000
            duration /= 1000

        spectrogram_filepath = output_image_path
        open(spectrogram_filepath, "w").close()
        y, sr = librosa.load(audio_filepath)
        
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

        # Use ScalarFormatter to avoid scientific notation
        plt.gca().xaxis.set_major_formatter(mticker.ScalarFormatter(useOffset=False, useMathText=False))
        plt.gca().ticklabel_format(style="plain", axis="x")

        plt.colorbar(format='%+2.0f dB')
        plt.title(f'Spectrogram for {self.name}')
        plt.tight_layout()
        plt.savefig(output_image_path)
        plt.close()
