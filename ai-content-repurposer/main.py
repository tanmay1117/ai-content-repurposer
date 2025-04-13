import streamlit as st
import yt_dlp
import whisper
import openai
import os
from pydub import AudioSegment

# Set OpenAI key from secrets


model = whisper.load_model("base")

# --------------- Functions ---------------- #

def download_video(yt_url, output_path="video.mp4"):
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

def extract_audio(video_path, audio_path="audio.mp3"):
    video = AudioSegment.from_file(video_path)
    video.export(audio_path, format="mp3")
    return audio_path

def transcribe_audio(audio_path):
    result = model.transcribe(audio_path)
    return result["text"]

def ask_gpt(prompt):
    response = openai.ChatCompletion.create(
        model="gpt-3.5-turbo",
        messages=[{"role": "user", "content": prompt}],
        temperature=0.7
    )
    return response.choices[0].message.content

# --------------- Streamlit UI ---------------- #

st.set_page_config(page_title="AI Content Repurposer", layout="centered")
st.title("🎬 AI Content Repurposer")
st.markdown("Turn your video into content with one click.")

yt_url = st.text_input("📺 Enter YouTube URL")
uploaded_file = st.file_uploader("📁 Or upload an MP4 file", type=["mp4"])

if st.button("🚀 Process Video"):
    video_path = None

    if yt_url:
        st.info("📥 Downloading YouTube video...")
        video_path = download_video(yt_url)
    elif uploaded_file:
        video_path = "uploaded_video.mp4"
        with open(video_path, "wb") as f:
            f.write(uploaded_file.read())
    else:
        st.warning("Please upload a video or paste a YouTube link.")

    if video_path and os.path.exists(video_path):
        st.success("✅ Video loaded!")
        st.video(video_path)

        audio_path = extract_audio(video_path)
        st.info("📝 Transcribing audio...")
        transcript = transcribe_audio(audio_path)
        st.text_area("📄 Transcript", transcript, height=300)

        st.info("🤖 Generating content...")

        summary = ask_gpt(f"Summarize and analyze this video:\n{transcript}")
        blog = ask_gpt(f"Write a blog post based on this transcript:\n{transcript}")
        tweets = ask_gpt(f"Turn this transcript into a tweet thread:\n{transcript}")
        seo = ask_gpt(f"Extract SEO keywords and key points from this transcript:\n{transcript}")

        # Show results
        st.markdown("### 🧠 Summary & Analysis")
        st.write(summary)
        st.download_button("💾 Download Summary", summary, file_name="summary.txt")

        st.markdown("### ✍️ Blog Post")
        st.write(blog)
        st.download_button("💾 Download Blog", blog, file_name="blog_post.txt")

        st.markdown("### 🧵 Tweet Thread")
        st.write(tweets)
        st.download_button("💾 Download Tweets", tweets, file_name="tweet_thread.txt")

        st.markdown("### 🔑 SEO Key Points")
        st.write(seo)
        st.download_button("💾 Download SEO Points", seo, file_name="seo_keywords.txt")

# --------------- Watermark ---------------- #
st.markdown("""
<style>
.watermark {
    position: fixed;
    bottom: 10px;
    right: 10px;
    color: #888;
    font-size: 13px;
    background: #f9f9f9;
    padding: 6px 12px;
    border-radius: 10px;
    box-shadow: 0 2px 6px rgba(0,0,0,0.15);
    z-index: 100;
}
</style>
<div class="watermark">
    🚀 Made by <b style='color:#00BFFF;'>Tanmay</b>
</div>
""", unsafe_allow_html=True)
