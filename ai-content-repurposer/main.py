import streamlit as st
import openai
import yt_dlp
import os
import whisper
import tempfile
from pydub import AudioSegment

# Set your OpenAI API key (use st.secrets in production)
api_key = "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"

# ---------------------------
# Download YouTube Video
# ---------------------------
def download_video(yt_url, output_path="video.mp4"):
    ydl_opts = {
        'format': 'mp4',
        'outtmpl': output_path,
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
        st.error(f"⚠️ Download failed: {str(e)}")
        return None

# ---------------------------
# Extract Audio from Video
# ---------------------------
def extract_audio(video_path):
    try:
        audio_path = os.path.splitext(video_path)[0] + ".mp3"
        video = AudioSegment.from_file(video_path)
        video.export(audio_path, format="mp3")
        return audio_path
    except Exception as e:
        st.error(f"⚠️ Audio extraction failed: {str(e)}")
        return None

# ---------------------------
# Transcribe with Whisper
# ---------------------------
def transcribe_audio(audio_path):
    try:
        model = whisper.load_model("base")
        result = model.transcribe(audio_path)
        return result['text']
    except Exception as e:
        st.error(f"⚠️ Transcription failed: {str(e)}")
        return None

# ---------------------------
# Generate Summary with OpenAI
# ---------------------------
def generate_summary(transcript):
    try:
        response = openai.ChatCompletion.create(
            model="gpt-3.5-turbo",
            messages=[
                {"role": "system", "content": "You are an AI that summarizes transcripts."},
                {"role": "user", "content": f"Summarize this transcript:\n{transcript}"},
            ]
        )
        return response.choices[0].message['content'].strip()
    except Exception as e:
        st.error(f"⚠️ Summary generation failed: {str(e)}")
        return None

# ---------------------------
# Streamlit UI
# ---------------------------
st.set_page_config(page_title="AI Content Repurposer", layout="centered")

st.title("🎬 AI Content Repurposer")
st.markdown("Paste a YouTube URL. We’ll download the video, transcribe it, and generate a summary.")

yt_url = st.text_input("Enter YouTube video URL")

if st.button("Process Video"):
    if yt_url:
        st.info("📥 Downloading video...")
        video_path = download_video(yt_url)

        if video_path and os.path.exists(video_path):
            st.success("✅ Video downloaded!")
            st.video(video_path)

            st.info("🔊 Extracting audio...")
            audio_path = extract_audio(video_path)

            if audio_path:
                st.info("📝 Transcribing audio...")
                transcript = transcribe_audio(audio_path)

                if transcript:
                    st.subheader("🗒️ Transcript")
                    st.text_area("Full Transcript", transcript, height=200)

                    st.info("🧠 Generating summary...")
                    summary = generate_summary(transcript)

                    if summary:
                        st.subheader("📌 Summary")
                        st.write(summary)
    else:
        st.warning("Please enter a YouTube URL.")
