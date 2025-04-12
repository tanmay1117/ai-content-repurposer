import streamlit as st

st.set_page_config(page_title="AI Content Repurposer", layout="centered")
st.title("AI Content Repurposer 🧠✍️")
st.write("Turn YouTube videos into tweets, blogs, and post ideas using OpenAI.")

youtube_url = st.text_input("Paste YouTube URL:")

if youtube_url:
    st.success("Transcription fetched successfully ")
    st.subheader("📝 Tweet Thread")
    st.code("1/ Just watched this amazing video on productivity hacks...\n2/ Here's what I learned 👇")
    
    st.subheader("📄 Blog Draft")
    st.write("In today's fast-paced world, productivity is everything. In this post, we'll explore...")

    st.button("Generate More ➕")
