from youtube_transcript_api import YouTubeTranscriptApi
import os
import math

def extract_transcript_from_youtube(video_url):
    video_id = video_url.split('=')[-1]
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

if __name__ == "__main__":
    video_url = "https://www.youtube.com/watch?v=1DkdnRPlf_U"
    extract_transcript_from_youtube(video_url)
