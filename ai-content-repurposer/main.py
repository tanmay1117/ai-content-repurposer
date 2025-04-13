import streamlit as st
import whisper
import openai
import os
os.system("apt-get install -y ffmpeg")

import tempfile

openai.api_key = "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"  # put in secret config later

st.title("🎥 AI Content Repurposer")
uploaded_file = st.file_uploader("Upload a video", type=["mp4", "mov", "mkv"])

if uploaded_file:
    st.video(uploaded_file)

    with st.spinner("Extracting and transcribing..."):
        with tempfile.NamedTemporaryFile(delete=False, suffix=".mp4") as tmp_video:
            tmp_video.write(uploaded_file.read())
            tmp_video_path = tmp_video.name

        audio_path = tmp_video_path.replace(".mp4", ".mp3")
        os.system(f"ffmpeg -i {tmp_video_path} -q:a 0 -map a {audio_path} -y")

        model = whisper.load_model("base")
        result = model.transcribe(audio_path)
        transcript = result["text"]

    st.subheader("📄 Transcript")
    st.write(transcript)

    if st.button("Summarize + Analyze"):
        with st.spinner("Thinking hard..."):
            response = openai.ChatCompletion.create(
                model="gpt-3.5-turbo",
                messages=[
                    {"role": "system", "content": "You are an assistant that summarizes and analyzes content."},
                    {"role": "user", "content": f"Here's a transcript of a video:\n\n{transcript}\n\nPlease summarize it and provide a brief analysis."}
                ]
            )
            summary = response["choices"][0]["message"]["content"]

        st.subheader("🧠 Summary & Analysis")
        st.write(summary)
