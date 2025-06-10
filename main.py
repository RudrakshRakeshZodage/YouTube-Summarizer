from fastapi import FastAPI
from pydantic import BaseModel
import google.generativeai as genai
from youtube_transcript_api import YouTubeTranscriptApi
import whisper
import json
import re
import os
import yt_dlp
import tempfile
import shutil
from glob import glob

# Configure Gemini and Whisper
genai.configure(api_key="AIzaSyB9Ku-xf8094EOibDTLWsrbK6R1a_Vdkaw")
whisper_model = whisper.load_model("base")

app = FastAPI()

class VideoURL(BaseModel):
    url: str

# Extract YouTube video ID
def get_video_id(url: str) -> str:
    match = re.search(r"(?:v=|\/)([A-Za-z0-9_-]{11})", url)
    return match.group(1) if match else None

# Try getting YouTube captions
def fetch_transcript_youtube(video_id: str) -> str:
    try:
        transcript = YouTubeTranscriptApi.get_transcript(video_id)
        return " ".join([t["text"] for t in transcript])
    except Exception:
        return None

# Fallback: Whisper transcription via yt_dlp + ffmpeg
def fetch_transcript_whisper(video_url: str) -> str:
    if not shutil.which("ffmpeg"):
        raise EnvironmentError("FFmpeg is not installed or not in PATH.")

    with tempfile.TemporaryDirectory() as tmpdir:
        try:
            ydl_opts = {
                'format': 'bestaudio/best',
                'outtmpl': os.path.join(tmpdir, '%(title)s.%(ext)s'),
                'postprocessors': [{
                    'key': 'FFmpegExtractAudio',
                    'preferredcodec': 'mp3',
                    'preferredquality': '192',
                }],
                'quiet': True,
            }
            with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                ydl.download([video_url])

            mp3_files = glob(os.path.join(tmpdir, '*.mp3'))
            if not mp3_files:
                raise FileNotFoundError("MP3 file not found after yt_dlp processing.")

            result = whisper_model.transcribe(mp3_files[0])
            return result["text"]
        except Exception as e:
            raise RuntimeError(f"Whisper transcription failed: {e}")

@app.post("/summarize")
async def summarize_video(video: VideoURL):
    video_id = get_video_id(video.url)
    if not video_id:
        return {"error": "Invalid YouTube URL."}

    # Step 1: Try captions
    transcript = fetch_transcript_youtube(video_id)

    # Step 2: Fallback to Whisper
    if not transcript:
        try:
            transcript = fetch_transcript_whisper(video.url)
        except Exception as e:
            return {"error": f"Both transcript methods failed: {e}"}

    # Step 3: Truncate transcript
    if len(transcript) > 12000:
        transcript = transcript[:12000]

    # Step 4: Prepare prompt
    prompt = f"""
    Based on the transcript below, summarize in JSON format:
    {{
      "topic_name": " ",
      "topic_summary": " "
    }}

    Transcript:
    \"\"\"{transcript}\"\"\"
    """

    # Step 5: Call Gemini API
    try:
        model = genai.GenerativeModel("gemini-1.5-flash-latest")
        response = model.generate_content(prompt)
        output = response.text.strip()

        # Remove Markdown if present
        if output.startswith("```json"):
            output = output.split("```json")[-1].strip("``` \n")
        elif output.startswith("```"):
            output = output.split("```")[-1].strip("``` \n")

        try:
            return json.loads(output)
        except json.JSONDecodeError:
            return {"raw_output": output}
    except Exception as e:
        return {"error": f"Gemini failed: {e}"}
