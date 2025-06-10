#🧠✨ AI-Powered YouTube Summarizer API

🚀 Project Overview:
Built an intelligent API that automatically summarizes YouTube videos using AI-powered transcript extraction and LLMs. If captions are missing, it seamlessly falls back to speech-to-text transcription via Whisper.

📌 Key Use Case:
🔍 Save time by getting quick, structured summaries of long videos — ideal for students, researchers, content creators, and professionals who want insights without watching the full content.

🧰 Tech Stack:
⚙️ Framework: FastAPI

🧠 AI Models:

Google Gemini 1.5 Pro – for generating structured summaries
OpenAI Whisper – for audio transcription fallback
📺 Video Processing: yt-dlp
🎙️ Audio Processing: FFmpeg
📝 Caption Extraction: YouTube Transcript API

🐍 Language: Python
🧪 Tools & Libs: Pydantic, tempfile, regex, JSON, glob

🧪 Features:
🎯 Accurate video summarization in JSON format
🎧 Automatic speech transcription using Whisper if captions are unavailable
📦 Lightweight and production-ready API
🛠️ Error handling with fallback logic
