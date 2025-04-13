import streamlit as st
import yt_dlp
import whisper
import os
from openai import OpenAI

# Initialize Whisper + OpenAI Client
model = whisper.load_model("base")
client = OpenAI(api_key=st.secrets["openai"]["api_key"])

# ----------------- Functions ----------------- #

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

def transcribe_with_whisper(video_path):
    if not os.path.exists(video_path):
        st.error("⚠️ Video file not found.")
        return ""
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

# ----------------- Streamlit UI ----------------- #

st.set_page_config(page_title="AI Content Repurposer", layout="centered")
st.title("📼 AI Content Repurposer")
st.caption("Paste a YouTube URL or upload a video to repurpose content using AI.")

yt_url = st.text_input("📺 Paste YouTube URL")
uploaded_file = st.file_uploader("📁 Or upload an MP4 file", type=["mp4"])

if st.button("🚀 Process Video"):
    video_path = None

    if yt_url:
        st.info("📥 Downloading video...")
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

        st.info("📝 Transcribing with Whisper...")
        transcript = transcribe_with_whisper(video_path)
        st.text_area("📄 Transcript", transcript, height=300)

        st.info("🤖 Generating content with GPT...")

        summary = ask_gpt(f"Summarize and analyze this video:\n{transcript}")
        blog = ask_gpt(f"Write a blog post based on this transcript:\n{transcript}")
        tweets = ask_gpt(f"Turn this transcript into a tweet thread:\n{transcript}")
        seo = ask_gpt(f"Extract SEO keywords and key points from this transcript:\n{transcript}")

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

# ----------------- Watermark ----------------- #

st.markdown("""
<style>
.watermark {
    position: fixed;
    bottom: 10px;
    right: 10px;
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
