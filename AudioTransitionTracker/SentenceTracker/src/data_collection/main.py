from audio_processing import *
from utils import *

if __name__ == "__main__":
    while True:
        video_id = input("Input video: ")
        is_url = "youtube.com" in video_id
        if is_url:
            video_id = extract_id_from_url(video_id)
        print("Available modes:\nP: Parse\nS: Segment\nD: Divide\n")
        mode = input("Parse new URL or Segment existing AudioFile? ")
        if mode.lower() == 'p' or mode.lower() == 'parse':
            existing_urls = load_urls("urls.txt")
            #video_url = input("Input URL: ")
            video_url = create_item_from_id(video_id, "u")
            if video_url in existing_urls:
                print("URL already converted into AudioLecture object")
            else:
                create_new_audio_lecture(video_url)
                existing_urls.add(video_url)
                save_url("../urls.txt", video_url)
                print("URL saved, converting to AudioLecture")
        elif mode.lower() != 'q':
            json_file = f"../../data/json_lectures/{video_id}.json"
            audio_lec = parse_audio_lecture_from_json(json_file)
            if audio_lec.is_full:
                if mode.lower() == 's' or mode.lower() == 'segment':
                    segment_audio_lecture(audio_lec, 120000, 120000)
                elif mode.lower() == 'd' or mode.lower() == 'divide':
                    #obtain audiolecture obj from json
                    duration = audio_lec.duration
                    print(f"FYI, total duration: {duration} ms or {duration // 60000} min {(duration % 60000) // 1000} s")
                    unit_duration_ms = (int)(input("Unit duration length (seconds): ")) * 1000
                    print(f"Recommended total segments for {unit_duration_ms} ms is {duration // unit_duration_ms}")
                    total_count = (int)(input(f"Total segments: "))
                    is_create_spectrogram = 'y' in input("Generate spectrogram? ")
                    no_segments = divide_audio_into_segments(audio_lec, unit_duration_ms, total_count, is_create_spectrogram)
                    print(f"Create {total_count} {unit_duration_ms}-sec segments for {video_id} (No segments = {no_segments})")
            else:
                print("Item is already segmented")
        else: 
            exit()
