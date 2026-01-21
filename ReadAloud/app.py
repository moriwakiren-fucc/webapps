import streamlit as st
import numpy as np
import librosa
import soundfile as sf
import tempfile
import os
import re
from openai import OpenAI

# =====================
# OpenAI TTS
# =====================
def tts_openai(text, out_path):
    client = OpenAI(api_key=os.environ["OPENAI_API_KEY"])
    with client.audio.speech.with_streaming_response.create(
        model="gpt-4o-mini-tts",
        voice="alloy",
        input=text
    ) as response:
        response.stream_to_file(out_path)


# =====================
# モーラ分割（簡易）
# =====================
def split_to_moras(text):
    pattern = r"[きしちにひみりぎじぢびぴ][ゃゅょ]|[ァ-ンー]|[ぁ-ん]|."
    return re.findall(pattern, text)


# =====================
# アクセント → F0カーブ
# =====================
def build_f0_curve(level, length):
    # level: 0〜4（低 → 高）
    center = length // 2
    height = (level - 2) * 0.15
    x = np.linspace(-1, 1, length)
    curve = np.exp(-4 * x**2) * height
    return curve


# =====================
# モーラ単位ピッチ加工
# =====================
def apply_pitch_curve(y, sr, curve):
    f0 = librosa.yin(y, fmin=70, fmax=400)
    f0 = np.nan_to_num(f0, nan=np.nanmean(f0))
    f0 *= (1 + curve[: len(f0)])
    y_shifted = librosa.effects.pitch_shift(
        y, sr, n_steps=12 * np.log2(f0.mean() / np.mean(f0))
    )
    return y_shifted


# =====================
# Streamlit UI
# =====================
st.title("日本語読み上げ（モーラ×アクセント制御）")

text = st.text_input(
    "読み上げテキスト",
    "昨日私が公園で見た白い犬はとても元気でした"
)

if st.button("音声生成（上）"):

    with tempfile.NamedTemporaryFile(suffix=".wav", delete=False) as f:
        tts_openai(text, f.name)
        y, sr = librosa.load(f.name, sr=22050)

    moras = split_to_moras(text)

    st.write("### アクセント設定（上が高）")

    levels = []
    cols = st.columns(len(moras))
    for i, (mora, col) in enumerate(zip(moras, cols)):
        with col:
            st.text(mora)
            lv = st.radio(
                label="",
                options=[0, 1, 2, 3, 4],
                index=2,
                key=f"m_{i}",
                label_visibility="collapsed"
            )
            levels.append(lv)

    segments = np.array_split(y, len(moras))
    out = []

    for seg, lv in zip(segments, levels):
        curve = build_f0_curve(lv, len(seg))
        out.append(apply_pitch_curve(seg, sr, curve))

    y_out = np.concatenate(out)
    y_out /= np.max(np.abs(y_out))

    with tempfile.NamedTemporaryFile(suffix=".wav", delete=False) as f:
        sf.write(f.name, y_out, sr)
        st.audio(f.name)
        st.download_button("ダウンロード", open(f.name, "rb"), "accent.wav")

if st.button("音声生成（下）"):
    st.experimental_rerun()
