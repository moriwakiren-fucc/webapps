import streamlit as st
from gtts import gTTS
import librosa
import numpy as np
import soundfile as sf
import tempfile
import os

# =====================
# 1文字音声生成
# =====================
def synth_char(ch, accent, voice_type):
    with tempfile.NamedTemporaryFile(suffix=".mp3", delete=False) as f:
        gTTS(text=ch, lang="ja").save(f.name)
        y, sr = librosa.load(f.name, sr=None)

    # ---- 声タイプ設定 ----
    if voice_type == "男声低":
        base_pitch = -4
        stretch = 0.95
    elif voice_type == "男声中":
        base_pitch = -2
        stretch = 1.0
    elif voice_type == "男声高":
        base_pitch = 0
        stretch = 1.05
    elif voice_type == "女声低":
        base_pitch = 2
        stretch = 1.05
    elif voice_type == "女声中":
        base_pitch = 4
        stretch = 1.1
    else:
        base_pitch = 6
        stretch = 1.15

    # ---- 話速 ----
    y = librosa.effects.time_stretch(y, rate=stretch)

    # ---- アクセント（文字ごと）----
    y = librosa.effects.pitch_shift(
        y,
        sr=sr,
        n_steps=base_pitch + (accent - 1.0) * 6
    )

    return y, sr


# =====================
# Streamlit UI
# =====================
st.title("日本語テキスト読み上げ（アクセント調整対応）")

text = st.text_input("読み上げテキスト", "なまざかな")

voice_type = st.selectbox(
    "声タイプ",
    ["男声低", "男声中", "男声高", "女声低", "女声中", "女声高"]
)

st.subheader("文字ごとのアクセント")
accents = []
for i, ch in enumerate(text):
    accents.append(
        st.slider(
            f"{i}:{ch}",
            0.7,
            1.3,
            1.0,
            0.05,
            key=f"a_{i}"
        )
    )

if st.button("音声生成"):
    audio = []
    sr = None

    for ch, acc in zip(text, accents):
        y, sr = synth_char(ch, acc, voice_type)
        audio.append(y)

    y_all = np.concatenate(audio)
    y_all /= np.max(np.abs(y_all))

    with tempfile.NamedTemporaryFile(suffix=".wav", delete=False) as f:
        sf.write(f.name, y_all, sr)
        st.audio(f.name)
        st.download_button(
            "音声をダウンロード（wav）",
            open(f.name, "rb"),
            file_name="accent_voice.wav"
        )
