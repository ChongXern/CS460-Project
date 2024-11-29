import json
import yt_dlp
import os
import librosa
import librosa.display
import matplotlib.pyplot as plt
import numpy as np
import math
from youtube_transcript_api import YouTubeTranscriptApi

class AudioLecture:
    def __init__(self, name, url, audio_filepath, spectrogram_filepath, duration, fullstop_timestamps, transcript_path):
        self.name = name
        self.url = url
        self.audio_filepath = audio_filepath
        self.spectrogram_filepath = spectrogram_filepath
        self.duration = duration
        self.fullstop_timestamps = fullstop_timestamps  # List of (start_time, end_time) tuples
        self.transcript_path = transcript_path
        self.is_full = True
        self.start_time = 0

    def __repr__(self):
        return f"AudioLecture(name={self.name}, duration={self.duration} min, fullstop_timestamps={self.fullstop_timestamps})"

    def extract_transcript(self, video_id):
        filename = f"transcripts/transcript_{video_id}.txt"
        open(filename, "w")
        extracted_transcript = YouTubeTranscriptApi.get_transcript(video_id)
        
        transcript_lines = {}
        
        for entry in extracted_transcript:
            start_time = math.floor(entry['start'])
            text = entry['text']
            
            if start_time not in transcript_lines:
                transcript_lines[start_time] = []
            transcript_lines[start_time].append(text)
        
        with open(filename, "w") as f:
            max_time = max(transcript_lines.keys())
            for second in range(max_time + 1):
                if second in transcript_lines:
                    f.write("timestamp " + str(second) + ": ")
                    f.write(" ".join(transcript_lines[second]) + "\n")
                else:
                    f.write("\n")
        f.close()
        
        #self.transcript_path = filename
        return filename
    
    def to_json(self, json_filepath):
        data = {
            'name': self.name,
            'url': self.url,
            'audio_filepath': self.audio_filepath,
            'spectrogram_filepath': self.spectrogram_filepath,
            'start_time': 0,
            'duration': self.duration,
            'is_full': True,
            'fullstop_timestamps': [{'start_time': t[0], 'end_time': t[1]} for t in self.fullstop_timestamps],
            'transcript_path': self.transcript_path if self.transcript_path != None else None
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

    def generate_spectrogram(self, audio_filepath, output_image_path, start_time=0):
        spectrogram_filepath = output_image_path
        open(spectrogram_filepath, "w").close()
        y, sr = librosa.load(audio_filepath)
        #self.duration = librosa.get_duration(y=y, sr=sr)
        self.duration = math.floor(librosa.get_duration(y=y, sr=sr))

        #start_sample = int(sr * start_time)
        #end_sample = int(sr * (start_time + duration))
        
        D = librosa.stft(y)
        S_db = librosa.amplitude_to_db(abs(D), ref=np.max)

        # Plotting the spectrogram
        plt.figure(figsize=(10, 4))
        librosa.display.specshow(S_db, sr=sr, x_axis='time', y_axis='log', cmap='coolwarm')
        plt.colorbar(format='%+2.0f dB')
        plt.title('Spectrogram')
        plt.tight_layout()
        plt.savefig(output_image_path)
        plt.close()

def create_new_audio_lecture(video_url):
    output_dir = "audio_files"
    json_dir = "lectures"  # Directory to save JSON files
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
        fullstop_timestamps=fullstop_timestamps,
        transcript_path=None
    )

    audio_lecture.generate_spectrogram(f"{audio_filepath}.mp3", output_image_path)
    audio_lecture.spectrogram_filepath = output_image_path  # Update the spectrogram filepath
    audio_lecture.extract_transcript(name)
    
    os.makedirs(json_dir, exist_ok=True)
    json_path = os.path.join(json_dir, f"{name}.json")
    audio_lecture.to_json(json_path)

    print(audio_lecture)

#def segment_audio_lecture(audioLecture: AudioLecture, start_time, duration):
    #should return new audioLecture
    

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

if __name__ == "__main__":
    existing_urls = load_urls("urls.txt")
    while True:
        video_url = input("Input URL: ")
        if video_url.lower() == "q":
            break
        if video_url in existing_urls:
            print("URL already converted into AudioLecture object")
        else:
            create_new_audio_lecture(video_url)
            existing_urls.add(video_url)
            save_url("urls.txt", video_url)
            print("URL saved, converting to AudioLecture")

"""
def slice_spectrogram(audiolec: AudioLecture):
    spectrogram = audiolec.spectrogram_filepath

def slice_audiolecture(audiolec: AudioLecture, duration, start):
    name = f"{audiolec.name}_{str(start)}"
    url = audiolec.url
    audio_filepath = audiolec.audio_filepath
    
    for i in range(duration):
    
"""
