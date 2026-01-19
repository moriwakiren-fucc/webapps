from openai import OpenAI
import streamlit as st
from gtts import gTTS
import librosa
import numpy as np
import soundfile as sf
import tempfile
import os
import re

# =====================
# 読み上げ可能判定
# =====================
def is_speakable(ch):
    return bool(re.search(r"[ぁ-んァ-ン一-龯]", ch))


# =====================
# 1文字音声生成
# =====================
def synth_char(ch, accent_level, voice_type, sr=22050):
    if not is_speakable(ch):
        return np.zeros(int(sr * 0.15)), sr

    with tempfile.NamedTemporaryFile(suffix=".mp3", delete=False) as f:
        gTTS(text=ch, lang="ja").save(f.name)
        y, sr = librosa.load(f.name, sr=None)

    if voice_type == "男声低":
        base_pitch, stretch = -4, 0.95
    elif voice_type == "男声中":
        base_pitch, stretch = -2, 1.0
    elif voice_type == "男声高":
        base_pitch, stretch = 0, 1.05
    elif voice_type == "女声低":
        base_pitch, stretch = 2, 1.05
    elif voice_type == "女声中":
        base_pitch, stretch = 4, 1.1
    else:
        base_pitch, stretch = 6, 1.15

    y = librosa.effects.time_stretch(y, rate=stretch)

    accent_shift = (2 - accent_level) * -2
    y = librosa.effects.pitch_shift(y, sr=sr, n_steps=base_pitch + accent_shift)

    return y, sr


# =====================
# Streamlit UI
# =====================
st.title("日本語テキスト読み上げ（アクセント調整）")

input_text = st.text_input(
    "読み上げテキスト",
    "昨日私が公園で見た、赤い帽子を被って元気に走り回っていた白い犬の飼い主は、私の父の古い友人でした。"
)

client = OpenAI(api_key=os.environ["OPENAI_API_KEY"])
response = client.responses.create(
    model="gpt-4.1-mini",
    input=f"「{input_text}」という文章の読み方のうち一般的なものをひらがなで1つだけ教えて。"
)

text = response.output_text.strip()

voice_type = st.selectbox(
    "声タイプ",
    ["男声低", "男声中", "男声高", "女声低", "女声中", "女声高"]
)

st.button("音声生成", key="top_generate")

# ===== 横並び表示 =====
char_cols = st.columns(len(text))
accent_levels = []

for i, (col, ch) in enumerate(zip(char_cols, text)):
    with col:
        st.markdown(f"<div style='text-align:center;font-size:20px'>{ch}</div>", unsafe_allow_html=True)

        level = st.radio(
            "",
            options=[0, 1, 2, 3, 4],
            index=2,
            key=f"accent_{i}",
            label_visibility="collapsed",
            format_func=lambda _: ""
        )

        accent_levels.append(level)

st.button("音声生成", key="bottom_generate")

# ===== 音声生成処理 =====
if st.session_state.get("top_generate") or st.session_state.get("bottom_generate"):
    audio = []
    sr = None

    for ch, level in zip(text, accent_levels):
        y, sr = synth_char(ch, level, voice_type)
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
