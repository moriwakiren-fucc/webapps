from openai import OpenAI
import streamlit as st
from gtts import gTTS
import librosa
import numpy as np
import soundfile as sf
import tempfile
import os
import re

st.set_page_config(layout="wide")

# =====================
# OpenAI client
# =====================
client = OpenAI(api_key=os.environ["OPENAI_API_KEY"])


# =====================
# 読み上げ可能判定
# =====================
def is_speakable(ch):
    return bool(re.search(r"[ぁ-んァ-ン一-龯]", ch))


# =====================
# AIふりがな取得→モーラ分解
# =====================
def get_furigana(text):
    res = client.responses.create(
        model="gpt-4.1-mini",
        input=(
            "次の日本語の文章の最も一般的な読み方をひらがなに変換して、"
            "ただし、質問の復唱など、読み方以外のことは何も言わないでください。\n\n"
            f"{text}"
        )
    )
    return res.output_text.strip()

def get_mora_text(text):
    out_text = get_furigana(text)
    pattern = r'[ぁ-んー][ゃゅょぁぃぅぇぉ]?'

    moras = re.findall(pattern, out_text)
    moras_joined = "|".join(moras)
    return moras_joined

# =====================
# モーラ内アクセントカーブ
# =====================
def build_pitch_curve(level, length, max_shift=4):
    """
    level: 0〜4
    中央が最大になる山型カーブ
    """
    target = (level - 2) / 2 * max_shift
    x = np.linspace(-1, 1, length)
    curve = (1 - x**2) * target
    return curve


# =====================
# モーラ音声生成
# =====================
def synth_mora(mora, accent_level, voice_type, sr=22050):
    if not is_speakable(mora):
        return np.zeros(int(sr * 0.12)), sr

    with tempfile.NamedTemporaryFile(suffix=".mp3", delete=False) as f:
        gTTS(text=mora, lang="ja").save(f.name)
        y, sr = librosa.load(f.name, sr=None)

    # 声タイプ設定
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

    y = librosa.effects.time_stretch(y, rate=stretch)

    curve = build_pitch_curve(accent_level, len(y))

    frame = 1024
    hop = 256
    out = np.zeros_like(y)

    for i in range(0, len(y) - frame, hop):
        shift = base_pitch + curve[i]
        out[i:i+frame] += librosa.effects.pitch_shift(
            y[i:i+frame],
            sr=sr,
            n_steps=shift,
            n_fft = frame
        )

    return out, sr


# =====================
# Streamlit UI
# =====================
st.title("日本語読み上げ（モーラ × 滑らかアクセント）")

input_text = st.text_input(
    "読み上げテキスト",
    "今日私が公園で見た、赤い帽子を被って元気に走り回っていた白い犬の飼い主は、私の父の古い友人でした。"
)

voice_type = st.selectbox(
    "声タイプ",
    ["男声低", "男声中", "男声高", "女声低", "女声中", "女声高"]
)

if st.button("テキスト読み込み"):
    st.session_state["mora_text"] = get_mora_text(input_text)

if "mora_text" in st.session_state:
    
    moras = st.session_state["mora_text"].split("|")

    st.subheader("モーラアクセント（上ほど高）")

    cols = st.columns([len(mora) for mora in moras])
    accent_levels = []

    for i, (col, mora) in enumerate(zip(cols, moras)):
        with col:
            st.markdown(
                f"<div style='text-align:center;font-weight:bold;'>{mora}</div>",
                unsafe_allow_html=True
            )
            level = st.radio(
                "アクセント選択",
                [0, 1, 2, 3, 4],
                index=2,
                key=f"a_{i}",
                label_visibility="collapsed",
                format_func=lambda _: ""
            )
            accent_levels.append(level)

    st.markdown("---")

    if st.button("② 音声生成"):
        progress_bar = st.progress(0, text='')
        audio = []

        for i,(mora, level) in enumerate(zip(moras, accent_levels)):
            ip = i / (len(moras)-1)
            y, sr = synth_mora(mora, level, voice_type)
            audio.append(y)
            progress_bar.progress(ip, text=f'{str(round(ip * 100))}%完了　処理中のテキスト：{mora}')
            if ip == 1:
                progress_bar.progress(ip, text=f'完了！')

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
