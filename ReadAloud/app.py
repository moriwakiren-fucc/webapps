import streamlit as st
from gtts import gTTS
import librosa
import numpy as np
import soundfile as sf
import tempfile
import os

# =====================
# 音声加工関数
# =====================
def process_voice(wav_path, accents, voice_type):
    y, sr = librosa.load(wav_path, sr=None)

    # ---- 声タイプ設定 ----
    if voice_type == "男声低":
        pitch = -4
        stretch = 0.95
        formant = 0.90
    elif voice_type == "男声中":
        pitch = -2
        stretch = 1.0
        formant = 0.95
    elif voice_type == "男声高":
        pitch = 0
        stretch = 1.05
        formant = 1.0
    elif voice_type == "女声低":
        pitch = 2
        stretch = 1.05
        formant = 1.05
    elif voice_type == "女声中":
        pitch = 4
        stretch = 1.1
        formant = 1.1
    else:  # 女声高
        pitch = 6
        stretch = 1.15
        formant = 1.15

    # ---- 話速 ----
    y = librosa.effects.time_stretch(y, rate=stretch)

    # ---- ピッチ ----
    y = librosa.effects.pitch_shift(y, sr=sr, n_steps=pitch)

    # ---- 擬似フォルマント ----
    y = librosa.resample(y, orig_sr=sr, target_sr=int(sr * formant))
    y = librosa.resample(y, orig_sr=int(sr * formant), target_sr=sr)

    # ---- アクセント（全体に反映）----
    accent_gain = np.mean(accents)
    y *= accent_gain

    return y, sr


# =====================
# Streamlit UI
# =====================
st.title("日本語テキスト読み上げ")

text = st.text_area("読み上げテキスト", "文章の時にイントネーションを調整します。")

voice_type = st.selectbox(
    "声タイプ",
    ["男声低", "男声中", "男声高", "女声低", "女声中", "女声高"]
)

# ---- 文字ごとのアクセント ----
accents = []
st.subheader("文字ごとのアクセント")
for i, ch in enumerate(text):
    accents.append(
        st.slider(
            f"{i}:{ch}",
            0.7,
            1.3,
            1.0,
            0.05,
            key=f"accent_{i}"
        )
    )

if st.button("音声生成"):
    with tempfile.TemporaryDirectory() as tmpdir:
        raw_mp3 = os.path.join(tmpdir, "raw.mp3")
        raw_wav = os.path.join(tmpdir, "raw.wav")

        # ---- gTTS ----
        tts = gTTS(text=text, lang="ja")
        tts.save(raw_mp3)

        # ---- mp3 → wav ----
        y, sr = librosa.load(raw_mp3, sr=None)
        sf.write(raw_wav, y, sr)

        # ---- 波形加工 ----
        y2, sr2 = process_voice(raw_wav, accents, voice_type)

        out_wav = os.path.join(tmpdir, "output.wav")
        sf.write(out_wav, y2, sr2)

        st.audio(out_wav)
        st.download_button(
            "音声ファイルをダウンロード（wav）",
            open(out_wav, "rb"),
            file_name="read_aloud.wav"
        )
