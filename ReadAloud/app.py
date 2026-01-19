import streamlit as st
from gtts import gTTS
import tempfile
import os
import base64

# ===== 声タイプ（Streamlit安全）=====
VOICE_PRESETS = {
    "男声低": {"speed": 0.85},
    "男声中": {"speed": 0.95},
    "男声高": {"speed": 1.05},
    "女声低": {"speed": 1.05},
    "女声中": {"speed": 1.15},
    "女声高": {"speed": 1.25},
}

# ===== 1文字読み上げ =====
def synth_char(ch):
    tts = gTTS(text=ch, lang="ja")
    tmp = tempfile.NamedTemporaryFile(delete=False, suffix=".mp3")
    tts.save(tmp.name)
    return tmp.name

# ===== HTML Audio 結合 =====
def combine_audio(files, speeds):
    audio_tags = []
    for f, sp in zip(files, speeds):
        audio_tags.append(
            f"""
            <audio src="data:audio/mp3;base64,{encode_audio(f)}"
                   playbackrate="{sp}"></audio>
            """
        )
    return audio_tags

def encode_audio(path):
    with open(path, "rb") as f:
        return base64.b64encode(f.read()).decode()

# ===== UI =====
st.title("日本語テキスト読み上げ（Streamlit対応版）")

text = st.text_input("読み上げテキスト", "なまざかな")
voice = st.selectbox("声タイプ", VOICE_PRESETS.keys())

st.write("### 1文字ごとのアクセント（話速）")
accents = []
for ch in text:
    accents.append(st.slider(ch, 0.7, 1.3, 1.0, 0.05))

if st.button("読み上げ"):
    files = [synth_char(ch) for ch in text]

    speeds = [
        VOICE_PRESETS[voice]["speed"] * acc
        for acc in accents
    ]

    html = ""
    for f, sp in zip(files, speeds):
        b64 = encode_audio(f)
        html += f"""
        <audio autoplay controls>
          <source src="data:audio/mp3;base64,{b64}" type="audio/mp3">
        </audio>
        <script>
        document.currentScript.previousElementSibling.playbackRate = {sp};
        </script>
        """

    st.components.v1.html(html, height=300)
