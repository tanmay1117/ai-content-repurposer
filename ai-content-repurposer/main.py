import streamlit as st
import whisper
import openai
import yt_dlp
import os
import tempfile

openai.api_key = st.secrets["openai"]["api_key"]

st.set_page_config(page_title="AI Content Repurposer", layout="centered")
st.title("🎥 AI Content Repurposer")
st.caption("Paste a YouTube video and turn it into a blog, tweet thread, key points & more!")

yt_url = st.text_input("📎 Paste a YouTube video URL")

if yt_url:

    # 🎬 MP4 Downloader
    if st.button("⬇️ Download Full Video (MP4)"):
        with st.spinner("Downloading video in MP4..."):
            with tempfile.TemporaryDirectory() as tmpdir:
                mp4_path = os.path.join(tmpdir, "video.mp4")

                ydl_opts = {
                    'format': 'bestvideo[ext=mp4]+bestaudio[ext=m4a]/mp4',
                    'outtmpl': mp4_path,
                    'quiet': True,
                    'merge_output_format': 'mp4',
                }

                with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                    ydl.download([yt_url])

                with open(mp4_path, 'rb') as f:
                    video_data = f.read()
                    st.download_button(
                        label="🎬 Click to Download MP4",
                        data=video_data,
                        file_name="youtube_video.mp4",
                        mime="video/mp4"
                    )

    # 🔊 Audio + Transcription
    with st.spinner("🎧 Downloading audio & transcribing..."):
        with tempfile.TemporaryDirectory() as tmpdir:
            output_path = os.path.join(tmpdir, "video.%(ext)s")

            ydl_opts = {
                'format': 'bestaudio/best',
                'outtmpl': output_path,
                'quiet': True,
                'postprocessors': [{
                    'key': 'FFmpegExtractAudio',
                    'preferredcodec': 'mp3',
                    'preferredquality': '192',
                }],
            }

            with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                ydl.download([yt_url])

            for file in os.listdir(tmpdir):
                if file.endswith(".mp3"):
                    audio_path = os.path.join(tmpdir, file)
                    break
