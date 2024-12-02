import os
import json
import copy
from utils import animate_loading_bar
from pydub import AudioSegment
from pydub.playback import play

from audio_lecture import AudioLecture
from utils import extract_id_from_url, convert_timestamp_to_ms

def create_new_audio_lecture(video_url, is_create_spectrogram=True):
    output_dir = "../../data/audio_files"
    json_dir = "../../data/json_lectures"
    spectrogram_dir = "../../data/spectrograms"

    audio_filepath = AudioLecture.extract_audio_from_youtube(video_url, output_dir)

    duration = 0
    fullstop_timestamps = []
    name = extract_id_from_url(video_url)

    os.makedirs(spectrogram_dir, exist_ok=True)
    output_image_path = os.path.join(spectrogram_dir, f"{name}.png") if is_create_spectrogram else None
    
    # Create AudioLecture instance
    audio_lecture = AudioLecture(
        name=name,
        url=video_url,
        audio_filepath=f"{audio_filepath}.mp3",
        spectrogram_filepath=None,  # Placeholder for now
        duration=duration,
        fullstop_timestamps=fullstop_timestamps
    )

    if is_create_spectrogram:
        audio_lecture.generate_spectrogram(f"{audio_filepath}.mp3", output_image_path)
        audio_lecture.spectrogram_filepath = output_image_path  # Update the spectrogram filepath
    else:
        audio_lecture.spectrogram_filepath = ""
    
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

#assume start_time and duration in ms
def segment_audio_lecture(audiolec: AudioLecture, start_time_ms, duration_ms, is_play=False, is_create_spectrogram=True):
    #returns if segmentation successful or not (any fullstops present or if already segmented)
    if not audiolec.is_full: 
        return False
    name = audiolec.name
    json_file = f"../../data/json_lectures/{name}.json"
    with open(json_file, 'r') as file:
        data = json.load(file)
    
    new_audio_lecture = copy.copy(audiolec)
    
    # segment timestamp array based on start time and end time
    fullstop_timestamps = data["fullstop_timestamps"]
    new_timestamps_array = []
    
    for timestamp in fullstop_timestamps:
        if timestamp >= start_time_ms + duration_ms:
            break
        if timestamp + 2 > start_time_ms:
            new_timestamps_array.append(timestamp)
    
    new_audio_lecture.name = f"{name}_{str(start_time_ms)}_{str(start_time_ms + duration_ms)}"
    new_audio_lecture.is_full = False
    new_audio_lecture.start_time = start_time_ms
    new_audio_lecture.duration = duration_ms
    #print(f"new audio lecture duration: {new_audio_lecture.duration}")
    if is_create_spectrogram:
        new_audio_lecture.generate_spectrogram(f"{audiolec.audio_filepath}", f"../../data/lectures_segments/spectrograms/{new_audio_lecture.name}.png")
    else:
        new_audio_lecture.spectrogram_filepath = ""
    new_audio_lecture.fullstop_timestamps = new_timestamps_array
    new_audio_lecture.duration = duration_ms #reset duration_ms, figure smth out
    
    #create json file
    new_audio_lecture.to_json(f"../../data/lectures_segments/json/{new_audio_lecture.name}.json")
    
    if is_play:
        #audio_file = audiolec.audio_filepath
        audio_file = audiolec.audio_filepath if audiolec.audio_filepath.endswith(".mp3") else f"{audiolec.audio_filepath}.mp3"
        audio = AudioSegment.from_file(audio_file)
        segment = audio[start_time_ms:start_time_ms+duration_ms]
        play(segment)
    
    return len(new_timestamps_array) > 0

def divide_audio_into_segments(audiolec: AudioLecture, unit_duration_ms: int, total_count: int, is_create_spectrogram=True):
    total_duration_ms = audiolec.duration
    start_time_offset_ms = audiolec.start_time
    effective_duration_ms = total_duration_ms - start_time_offset_ms
    
    start_indx_diff = effective_duration_ms // total_count
    
    for i in range(total_count):
        curr_start = start_time_offset_ms + i * start_indx_diff
        if curr_start + unit_duration_ms > total_duration_ms + start_time_offset_ms:
            curr_start = total_duration_ms + start_time_offset_ms - unit_duration_ms
        
        if segment_audio_lecture(audiolec, curr_start, unit_duration_ms, is_create_spectrogram=is_create_spectrogram):
            animate_loading_bar(total_count, i + 1)
        else:
            print(f"No segments made for start_time={curr_start}")
