import asyncio
import warnings

try:
    asyncio.get_running_loop()
except RuntimeError:
    asyncio.set_event_loop(asyncio.new_event_loop())

# Optional: silence Whisper FP16 warning
warnings.filterwarnings("ignore", category=UserWarning)


import streamlit as st
import yt_dlp
import whisper
import os
import shutil
from openai import OpenAI

st.set_page_config(page_title="AI Content Repurposer")
warnings.filterwarnings("ignore", category=UserWarning)

os.environ["STREAMLIT_DISABLE_WATCHDOG_WARNINGS"] = "true"

try:
    asyncio.get_running_loop()
except RuntimeError:
    asyncio.set_event_loop(asyncio.new_event_loop())


if shutil.which("ffmpeg") is None:
    st.error("❌ ffmpeg is NOT available. Make sure packages.txt contains 'ffmpeg'")
else:
    st.success("✅ ffmpeg is available.")

try:
    client = OpenAI(api_key=st.secrets["openai"]["api_key"])
except Exception as e:
    st.error(f"❌ OpenAI config error: {e}")
    st.stop()

model = whisper.load_model("base")

def download_video(yt_url, output_path="video.mp4"):
    # Delete old video if exists
    if os.path.exists(output_path):
        os.remove(output_path)

    ydl_opts = {
        'format': 'mp4',
        'outtmpl': output_path,
        'noplaylist': True,
        'user_agent': 'Mozilla/5.0',
        'postprocessors': [{
            'key': 'FFmpegVideoConvertor',
            'preferedformat': 'mp4',
        }],
    }
    try:
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            ydl.download([yt_url])
        return output_path
    except Exception as e:
        st.error(f"❌ Download failed: {e}")
        return None

def transcribe_with_whisper(video_path):
    try:
        result = model.transcribe(video_path)
        return result["text"]
    except Exception as e:
        st.error(f"❌ Transcription failed: {e}")
        return ""




def ask_gpt(prompt):
    try:
        response = client.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=[{"role": "user", "content": prompt}],
            temperature=0.7
        )
        return response.choices[0].message.content
    except Exception as e:
        st.error(f"❌ OpenAI API error: {e}")
        return ""

st.title("📼 AI Content Repurposer")

yt_url = st.text_input("📺 Paste YouTube URL")
uploaded_file = st.file_uploader("📁 Or upload an MP4 file", type=["mp4"])

if st.button("🚀 Process Video"):
    video_path = None

    if yt_url:
        video_path = download_video(yt_url)
    elif uploaded_file:
        video_path = "uploaded.mp4"
        with open(video_path, "wb") as f:
            f.write(uploaded_file.read())
    else:
        st.warning("Paste a YouTube URL or upload a video.")

    if video_path and os.path.exists(video_path):
        st.video(video_path)
        st.info("📝 Transcribing...")
        transcript = transcribe_with_whisper(video_path)
        st.text_area("Transcript", transcript, height=300)

        if transcript:
            st.info("🤖 Generating content with GPT...")
            summary = ask_gpt(f"Summarize and analyze:\n{transcript}")
            st.markdown("### 🧠 Summary & Analysis")
            st.write(summary)

st.markdown("""
<style>
.watermark {
    position: fixed;
    bottom: 10px;
    left: 10px; /* Changed from right to left */
    background-color: #f0f0f0;
    padding: 8px 14px;
    border-radius: 10px;
    font-size: 13px;
    color: #333;
    box-shadow: 0 2px 6px rgba(0,0,0,0.15);
    font-weight: 500;
    z-index: 100;
}
</style>
<div class="watermark">
    🚀 Made by <b style='color:#007bff;'>Tanmay Pareek</b>
</div>
""", unsafe_allow_html=True)
