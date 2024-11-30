from audio_processing import *
from utils import *

if __name__ == "__main__":
    mode = input("Parse new URL or Segment existing AudioFile? ")
    if mode.lower() == 'p' or mode.lower() == 'parse':
        existing_urls = load_urls("urls.txt")
        video_url = input("Input URL: ")
        if video_url in existing_urls:
            print("URL already converted into AudioLecture object")
        else:
            create_new_audio_lecture(video_url)
            existing_urls.add(video_url)
            save_url("urls.txt", video_url)
            print("URL saved, converting to AudioLecture")
    elif mode.lower == 's' or mode.lower == 'segment':
        json_file = "json_lectures/4PkKI_S9TIQ.json"
        audioLecture = parse_audio_lecture_from_json(json_file)
        segment_audio_lecture(audioLecture, 2, 2)
    elif mode.lower == 'q':
        exit()
    else:
        mode = input("Parse new URL or Segment existing AudioFile? ")