import os
import json
import copy
from pydub import AudioSegment
from pydub.playback import play

from audio_lecture import AudioLecture
from utils import convert_timestamp_to_ms

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
        audio_filepath=f"{audio_filepath}.mp3",
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
def segment_audio_lecture(audiolec: AudioLecture, start_time, duration, is_play=False):
    #should return new audioLecture
    name = audiolec.name
    json_file = f"json_lectures/{name}.json"
    with open(json_file, 'r') as file:
        data = json.load(file)
    
    new_audio_lecture = copy.copy(audiolec)
    
    # segment timestamp array based on start time and end time
    start_time_ms = convert_timestamp_to_ms(start_time)
    duration_ms = convert_timestamp_to_ms(duration)
    fullstop_timestamps = data["fullstop_timestamps"]
    new_timestamps_array = []
    
    for timestamp in fullstop_timestamps:
        if timestamp >= start_time_ms + duration_ms:
            break
        if timestamp + 2 > start_time_ms:
            #new_timestamps_array.append(timestamp - start_time_ms)
            new_timestamps_array.append(timestamp)
    
    new_audio_lecture.name = f"{name}_{str(start_time)}_{str(start_time + duration)}"
    new_audio_lecture.is_full = False
    new_audio_lecture.start_time = start_time_ms
    new_audio_lecture.duration = duration_ms
    print(f"new audio lecture duration: {new_audio_lecture.duration}")
    new_audio_lecture.generate_spectrogram(f"{audiolec.audio_filepath}.mp3", f"lectures_segments/spectrograms/{new_audio_lecture.name}.png")
    new_audio_lecture.fullstop_timestamps = new_timestamps_array
    new_audio_lecture.duration = duration_ms #reset duration_ms, figure smth out
    
    #create json file
    new_audio_lecture.to_json(f"lectures_segments/json/{new_audio_lecture.name}.json")
    print("Segmented audio lecture")
    
    if is_play:
        #audio_file = audiolec.audio_filepath
        audio_file = audiolec.audio_filepath if audiolec.audio_filepath.endswith(".mp3") else f"{audiolec.audio_filepath}.mp3"
        audio = AudioSegment.from_file(audio_file)
        segment = audio[start_time_ms:start_time_ms+duration_ms]
        play(segment)

