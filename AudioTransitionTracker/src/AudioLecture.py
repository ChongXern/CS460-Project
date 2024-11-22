import json
import yt_dlp
import os
import librosa
import librosa.display
import matplotlib.pyplot as plt
import numpy as np

def generate_spectrogram(audio_filepath, output_image_path):
    y, sr = librosa.load(audio_filepath)

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

class AudioLecture:
    def __init__(self, name, url, audio_filepath, spectrogram_filepath, duration, transitions):
        self.name = name
        self.url = url
        self.audio_filepath = audio_filepath
        self.spectrogram_filepath = spectrogram_filepath
        self.duration = duration
        self.transitions = transitions  # List of (start_time, end_time) tuples

    def add_transition(self, start_time, end_time):
        self.transitions.append((start_time, end_time))

    def __repr__(self):
        return f"AudioLecture(name={self.name}, duration={self.duration} min, transitions={self.transitions})"

    def to_json(self, json_filepath):
        """Save the AudioLecture instance to a JSON file."""
        data = {
            'name': self.name,
            'url': self.url,
            'audio_filepath': self.audio_filepath,
            'spectrogram_filepath': self.spectrogram_filepath,
            'duration': self.duration,
            'transitions': [{'start_time': t[0], 'end_time': t[1]} for t in self.transitions],
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
            'quiet': True
        }

        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            ydl.download([video_url])

        print(f"Audio saved to {output_path}")
        return output_path
    
if __name__ == "__main__":
    video_url = input("Input URL: ")
    output_dir = "audio_files"
    json_dir = "lectures"  # Directory to save JSON files

    # Extract audio from YouTube
    audio_filepath = AudioLecture.extract_audio_from_youtube(video_url, output_dir)
    #duration = librosa.get_duration(filename=audio_filepath)
    #y, sr = librosa.load(audio_filepath, sr=None)
    #duration = len(y) / sr
    duration = 0
    name = video_url.split('=')[-1]
    spectrogram_filepath = f"spectrograms/{name}.png"  # replace w/ actual path
    open(spectrogram_filepath, "w").close()
    #print(f"AA: {audio_filepath} & {spectrogram_filepath}")
    generate_spectrogram(f"{audio_filepath}.mp3", spectrogram_filepath)
    transitions = []  # init empty list of transitions

    audio_lecture = AudioLecture(
        name=name,
        url=video_url,
        audio_filepath=audio_filepath,
        spectrogram_filepath=spectrogram_filepath,
        duration=duration,
        transitions=transitions
    )

    os.makedirs(json_dir, exist_ok=True)

    json_path = os.path.join(json_dir, f"{name}.json")  # Update this path as needed
    audio_lecture.to_json(json_path)

    print(audio_lecture)
