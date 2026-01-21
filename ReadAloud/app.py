from openai import OpenAI
import streamlit as st
import librosa
import numpy as np
import soundfile as sf
import tempfile
import os
import hashlib

# =====================
# OpenAI Client
# =====================
client = OpenAI(api_key=os.environ["OPENAI_API_KEY"])

# =====================
# OpenAI TTS（1回だけ）
# =====================
def tts_openai(text, out_path):
    with client.audio.speech.with_streaming_response.create(
        model="gpt-4o-mini-tts",
        voice="alloy",
        input=text
    ) as response:
        response.stream_to_file(out_path)

# =====================
# TTS結果をキャッシュ
# =====================
def text_to_hash(text):
    return hashlib.sha256(text.encode("utf-8")).hexdigest()
@st.cache_data(show_spinner="音声生成中...")
def generate_base_audio_safe(text):
    h = text_to_hash(text)
    cache_path = f"/tmp/tts_{h}.wav"

    if os.path.exists(cache_path):
        y, sr = librosa.load(cache_path, sr=22050)
        return y, sr

    try:
        with tempfile.NamedTemporaryFile(suffix=".wav", delete=False) as f:
            tts_openai(text, f.name)
            os.rename(f.name, cache_path)

        y, sr = librosa.load(cache_path, sr=22050)
        return y, sr

    except Exception as e:
        st.error("TTS生成に失敗しました（RateLimitの可能性）")
        raise e

# =====================
# 声タイプ設定
# =====================
VOICE_PRESET = {
    "男声低":  (-4, 0.95),
    "男声中":  (-2, 1.00),
    "男声高":  (0, 1.05),
    "女声低":  (2, 1.05),
    "女声中":  (4, 1.10),
    "女声高":  (6, 1.15),
}

# =====================
# アクセントカーブ生成
# =====================
def build_pitch_curve(levels, length):
    x = np.linspace(0, 1, len(levels))
    y = np.array(levels)
    xx = np.linspace(0, 1, length)
    return np.interp(xx, x, y)

# =====================
# 波形加工（ローカルのみ）
# =====================
def apply_accent(y, sr, levels, voice_type):
    base_pitch, stretch = VOICE_PRESET[voice_type]

    # 話速
    y = librosa.effects.time_stretch(y, rate=stretch)

    # ピッチカーブ
    curve = build_pitch_curve(levels, len(y))
    pitch = base_pitch + (curve - 2) * 2.5

    y_out = np.zeros_like(y)
    frame = 2048
    hop = 512

    for i in range(0, len(y) - frame, hop):
        seg = y[i:i+frame]
        step = int(np.mean(pitch[i:i+frame]))
        seg = librosa.effects.pitch_shift(seg, sr=sr, n_steps=step)
        y_out[i:i+frame] += seg

    return y_out

# =====================
# Streamlit UI
# =====================
st.title("日本語読み上げ（RateLimit完全回避版）")

text = st.text_area(
    "読み上げテキスト",
    "昨日私が公園で見た白い犬はとても元気でした。"
)

voice_type = st.selectbox(
    "声タイプ",
    list(VOICE_PRESET.keys())
)

st.divider()

# ---- アクセントUI ----
st.subheader("アクセント（モーラ想定・相対）")

chars = list(text)
levels = []

cols = st.columns(len(chars))
for i, ch in enumerate(chars):
    with cols[i]:
        st.markdown(f"<div style='text-align:center'>{ch}</div>", unsafe_allow_html=True)
        lv = st.radio(
            label=f"accent_{i}",
            options=[0,1,2,3,4],
            index=2,
            key=f"r_{i}",
            label_visibility="collapsed"
        )
        levels.append(lv)

st.divider()

# ---- 上下に生成ボタン ----
if st.button("🔊 音声生成（TTS）"):
    y_base, sr = generate_base_audio_safe(text)
    st.session_state["base_audio"] = (y_base, sr)

if "base_audio" in st.session_state:
    y_base, sr = st.session_state["base_audio"]

    y_out = apply_accent(y_base, sr, levels, voice_type)
    y_out /= np.max(np.abs(y_out) + 1e-9)

    with tempfile.NamedTemporaryFile(suffix=".wav", delete=False) as f:
        sf.write(f.name, y_out, sr)
        st.audio(f.name)
        st.download_button(
            "⬇ wavダウンロード",
            open(f.name, "rb"),
            file_name="accent_voice.wav"
        )
