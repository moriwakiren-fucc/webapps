import pyopenjtalk
import pyworld as pw
import numpy as np
import soundfile as sf
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

text = "イントネーションを調整します"

# 音声生成（素の音声）
x, sr = pyopenjtalk.tts(text)

# WORLDで解析
_f0, t = pw.dio(x.astype(np.float64), sr)
f0 = pw.stonemask(x.astype(np.float64), _f0, t, sr)
sp = pw.cheaptrick(x.astype(np.float64), f0, t, sr)
ap = pw.d4c(x.astype(np.float64), f0, t, sr)

# アクセント操作（例：全体を少し高く）
f0 *= 1.2

# 再合成
y = pw.synthesize(f0, sp, ap, sr)

# 保存
sf.write("output.wav", y, sr)
