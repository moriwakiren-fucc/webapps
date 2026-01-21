import streamlit as st
import numpy as np
import pyworld as pw
import soundfile as sf
import librosa
from gtts import gTTS
import tempfile
import os
import re
from openai import OpenAI

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
# モーラ音声生成（WORLD）
# =====================
def synth_mora_world(mora, accent_level, voice_type):
    if not is_speakable(mora):
        return np.zeros(2205), 22050

    with tempfile.NamedTemporaryFile(suffix=".mp3", delete=False) as f:
        gTTS(text=mora, lang="ja").save(f.name)
        y, sr = librosa.load(f.name, sr=22050)

    # ---- WORLD分析 ----
    f0, t = pw.dio(y, sr)
    f0 = pw.stonemask(y, f0, t, sr)
    sp = pw.cheaptrick(y, f0, t, sr)
    ap = pw.d4c(y, f0, t, sr)

    # ---- 声タイプ（声道長）----
    if voice_type == "男声低":
        f0 *= 0.85
        sp = pw.frequency_warp(sp, 0.9)
    elif voice_type == "男声中":
        f0 *= 0.95
    elif voice_type == "男声高":
        f0 *= 1.05
    elif voice_type == "女声低":
        f0 *= 1.15
        sp = pw.frequency_warp(sp, 1.05)
    elif voice_type == "女声中":
        f0 *= 1.25
        sp = pw.frequency_warp(sp, 1.1)
    else:
        f0 *= 1.35
        sp = pw.frequency_warp(sp, 1.15)

    # ---- アクセント（滑らか）----
    target = (accent_level - 2) / 2 * 0.4
    curve = np.linspace(1.0, 1.0 + target, len(f0))
    f0 *= curve

    # ---- 再合成 ----
    y_out = pw.synthesize(f0, sp, ap, sr)
    return y_out, sr


# =====================
# UI
# =====================
st.title("WORLD方式 日本語読み上げ")

text = st.text_input(
    "読み上げテキスト",
    "今日私が公園で見た、赤い帽子を被って元気に走り回っていた白い犬の飼い主は、私の父の古い友人でした。"
)

voice_type = st.selectbox(
    "声タイプ",
    ["男声低", "男声中", "男声高", "女声低", "女声中", "女声高"]
)

if st.button("① モーラ分解"):
    st.session_state["mora"] = get_mora_text(text)

if "mora" in st.session_state:
    moras = st.session_state["mora"].split("|")

    st.subheader("モーラアクセント")

    cols = st.columns(len(moras))
    levels = []

    for i, (col, mora) in enumerate(zip(cols, moras)):
        with col:
            st.markdown(f"<b>{mora}</b>", unsafe_allow_html=True)
            lv = st.radio(
                "アクセント",
                [0, 1, 2, 3, 4],
                index=2,
                key=f"lv_{i}",
                label_visibility="collapsed",
                format_func=lambda _: ""
            )
            levels.append(lv)

    if st.button("② 音声生成"):
        audio = []

        for mora, lv in zip(moras, levels):
            y, sr = synth_mora_world(mora, lv, voice_type)
            audio.append(y)

        y_all = np.concatenate(audio)
        y_all /= np.max(np.abs(y_all))

        with tempfile.NamedTemporaryFile(suffix=".wav", delete=False) as f:
            sf.write(f.name, y_all, sr)
            st.audio(f.name)
            st.download_button(
                "音声ダウンロード（wav）",
                open(f.name, "rb"),
                file_name="world_voice.wav"
            )
