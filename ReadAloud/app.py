import streamlit as st
from gtts import gTTS
import librosa
import soundfile as sf
import numpy as np
import os
from pydub import AudioSegment

# ===== 音声パラメータ =====
VOICE_PRESETS = {
    "男声低":  {"pitch": -3, "high_cut": 4000},
    "男声中":  {"pitch": -1, "high_cut": 5000},
    "男声高":  {"pitch": 1,  "high_cut": 6000},
    "女声低":  {"pitch": 3,  "high_cut": 7000},
    "女声中":  {"pitch": 5,  "high_cut": 8000},
    "女声高":  {"pitch": 7,  "high_cut": 9000},
}

# ===== ピッチ変更 =====
def change_pitch(wav_path, semitone):
    y, sr = librosa.load(wav_path, sr=None)
    y_shift = librosa.effects.pitch_shift(y, sr, semitone)
    sf.write(wav_path, y_shift, sr)

# ===== 音声生成（1文字） =====
def synth_char(ch, pitch):
    tts = gTTS(text=ch, lang="ja")
    tts.save("temp.mp3")

    audio = AudioSegment.from_mp3("temp.mp3")
    audio.export("temp.wav", format="wav")

    change_pitch("temp.wav", pitch)
    return AudioSegment.from_wav("temp.wav")

# ===== Streamlit UI =====
st.title("日本語テキスト読み上げ（アクセント調整付き）")

text = st.text_input("読み上げテキスト", "なまざかな")

voice_type = st.selectbox("声タイプ", list(VOICE_PRESETS.keys()))

st.write("### 1文字ごとのアクセント（±半音）")
accents = []
for i, ch in enumerate(text):
    val = st.slider(f"{ch}", -5.0, 5.0, 0.0, 0.5)
    accents.append(val)

if st.button("音声生成"):
    final_audio = AudioSegment.silent(duration=0)

    base_pitch = VOICE_PRESETS[voice_type]["pitch"]

    for ch, acc in zip(text, accents):
        seg = synth_char(ch, base_pitch + acc)
        final_audio += seg

    final_audio.export("output.mp3", format="mp3")

    st.audio("output.mp3")
    with open("output.mp3", "rb") as f:
        st.download_button("mp3ダウンロード", f, "speech.mp3")
