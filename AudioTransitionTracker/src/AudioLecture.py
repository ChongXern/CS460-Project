import json

class AudioLecture:
    def __init__(self, name, audio_filepath, spectrogram_filepath, duration, transitions):
        self.name = name
        self.audio_filepath = audio_filepath
        self.spectrogram_filepath = spectrogram_filepath
        self.duration = duration
        self.transitions = transitions # List of (start_time, end_time) tuples

    def add_transition(self, start_time, end_time):
        self.transitions.append((start_time, end_time))

    def __repr__(self):
        return f"AudioLecture(name={self.name}, duration={self.duration} min, transitions={self.transitions})"

def load_audio_lecture_from_json(json_filepath):
    with open(json_filepath, 'r') as file:
        data = json.load(file)
        transitions = [(t['start_time'], t['end_time']) for t in data['transitions']]
        return AudioLecture(
            name=data['name'],
            audio_filepath=data['audio_filepath'],
            spectrogram_filepath=data['spectrogram_filepath'],
            duration=data['duration'],
            transitions=transitions
        )
