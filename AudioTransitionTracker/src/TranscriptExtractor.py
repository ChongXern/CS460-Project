from youtube_transcript_api import YouTubeTranscriptApi
import os
import math

import os
import math
from youtube_transcript_api import YouTubeTranscriptApi

def extract_transcript_from_youtube(video_url):
    video_id = video_url.split('=')[-1]
    filename = f"transcripts/transcript_{video_id}.txt"

    # Ensure the output directory exists
    os.makedirs("transcripts", exist_ok=True)

    try:
        # Fetch the transcript from YouTube
        extracted_transcript = YouTubeTranscriptApi.get_transcript(video_id)
    except Exception as e:
        print(f"Error fetching transcript: {e}")
        return None

    transcript_lines = {}

    # Process each caption entry
    for entry in extracted_transcript:
        start_time = math.floor(entry['start'])  # Start time in seconds
        duration = math.ceil(entry['duration'])  # Duration in seconds
        words = entry['text'].split()  # Split caption text into words

        words_per_second = math.ceil(len(words) / duration)
        word_index = 0

        # Distribute words across each second
        for second in range(start_time, start_time + duration):
            if second not in transcript_lines:
                transcript_lines[second] = []

            for _ in range(words_per_second):
                if word_index < len(words):
                    transcript_lines[second].append(words[word_index])
                    word_index += 1

    with open(filename, "w") as f:
        max_time = max(transcript_lines.keys(), default=0)
        for second in range(max_time + 1):
            f.write(f"timestamp {second}: ")
            f.write(" ".join(transcript_lines.get(second, [])) + "\n")

    return filename

if __name__ == "__main__":
    video_url = "https://www.youtube.com/watch?v=1DkdnRPlf_U"
    extract_transcript_from_youtube(video_url)
