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
def synth_char(ch, accent, voice_type, sr=22050):
    if not is_speakable(ch):
        silence = np.zeros(int(sr * 0.15))
        return silence, sr

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

    y = librosa.effects.pitch_shift(
        y,
        sr=sr,
        n_steps=base_pitch + accent
    )

    return y, sr


# =====================
# Streamlit UI
# =====================
st.title("日本語テキスト読み上げ（アクセント指定）")

input_text = st.text_input(
    "読み上げテキスト",
    "昨日私が公園で見た、赤い帽子を被って元気に走り回っていた白い犬の飼い主は、私の父の古い友人でした。"
)

client = OpenAI(api_key=os.environ["OPENAI_API_KEY"])

response = client.responses.create(
    model="gpt-4.1-mini",
    input=f"「{input_text}」という文章の読み方をひらがなで1つだけ示してください。"
)

text = response.output_text.strip()

voice_type = st.selectbox(
    "声タイプ",
    ["男声低", "男声中", "男声高", "女声低", "女声中", "女声高"]
)

# ---- 音声生成ボタン（上）----
generate_top = st.button("音声生成（上）")

st.subheader("アクセント指定")

# ---- 文字表示（横並び）----
char_cols = st.columns(len(text))
for col, ch in zip(char_cols, text):
    col.markdown(f"**{ch}**")

# ---- ラジオボタン（5段階）----
accent_map = [-3, -1, 0, 1, 3]
accents = []

radio_cols = st.columns(len(text))
for i, (col, ch) in enumerate(zip(radio_cols, text)):
    val = col.radio(
        "",
        options=list(range(5)),
        index=2,
        key=f"r_{i}"
    )
    accents.append(accent_map[val])

# ---- 音声生成ボタン（下）----
generate_bottom = st.button("音声生成（下）")

# =====================
# 音声生成処理
# =====================
if generate_top or generate_bottom:
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
