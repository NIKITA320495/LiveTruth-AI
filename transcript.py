from youtube_transcript_api import YouTubeTranscriptApi

def fetch_live_stream_transcript(video_id):
    try:
        # Fetching the transcript for the live stream
        transcript = YouTubeTranscriptApi.get_transcript(video_id)
        print("Transcript fetched successfully!")
        for entry in transcript:
            print(f"{entry['start']} - {entry['start'] + entry['duration']}: {entry['text']}")
    except Exception as e:
        print(f"Error fetching transcript: {e}")

# Example live stream video ID (replace with actual live stream video ID)
video_id = 'wgi1IDDOHUc'
fetch_live_stream_transcript(video_id)
