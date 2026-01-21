import time
import tempfile
import numpy as np
import soundfile as sf
import streamlit as st
from openai import OpenAI, RateLimitError

client = OpenAI()


def tts_openai_retry(text: str, out_path: str, max_retry: int = 5):
    """
    OpenAI TTS を RateLimit 耐性付きで呼び出す
    """
    wait = 1.0  # 初期待機秒

    for attempt in range(max_retry):
        try:
            with client.audio.speech.with_streaming_response.create(
                model="gpt-4o-mini-tts",
                voice="alloy",
                input=text,
            ) as response:
                response.stream_to_file(out_path)
            return

        except RateLimitError:
            if attempt == max_retry - 1:
                raise
            time.sleep(wait)
            wait *= 2  # 指数バックオフ


@st.cache_data(show_spinner=False)
def generate_base_audio_safe(text: str):
    """
    Streamlit 用安全 TTS 生成
    """
    with tempfile.NamedTemporaryFile(suffix=".wav", delete=False) as f:
        tts_openai_retry(text, f.name)

        y, sr = sf.read(f.name)
        y = y.astype(np.float32)

    return y, sr


st.title("Read Aloud")

text = st.text_area("読み上げテキスト")

if st.button("TTS生成"):
    try:
        y, sr = generate_base_audio_safe(text)
        st.audio(y, sample_rate=sr)
    except RateLimitError:
        st.error("現在TTSが混雑しています。少し待ってから再試行してください。")
