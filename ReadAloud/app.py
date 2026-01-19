import streamlit as st
from gtts import gTTS
import tempfile
import os

st.title("テキスト読み上げアプリ（gTTS）")

text = st.text_area("読み上げたい文章を入力してください", height=150)

accents = []

if text:
    st.subheader("文字ごとのアクセント調整")

    for i, ch in enumerate(text):
        value = st.slider(
            label=f"{i+1}文字目「{ch}」",
            min_value=0.7,
            max_value=1.3,
            value=1.0,
            step=0.05,
            key=f"accent_{i}"   # ← ここが最重要
        )
        accents.append(value)

if st.button("音声生成"):
    if not text:
        st.warning("テキストを入力してください")
    else:
        tts = gTTS(text=text, lang="ja")

        with tempfile.NamedTemporaryFile(delete=False, suffix=".mp3") as f:
            tts.save(f.name)
            audio_path = f.name

        st.audio(audio_path)
        with open(audio_path, "rb") as f:
            st.download_button(
                label="MP3をダウンロード",
                data=f,
                file_name="read_aloud.mp3",
                mime="audio/mpeg"
            )

        os.remove(audio_path)
