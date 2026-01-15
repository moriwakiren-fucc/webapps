import streamlit as st
import time
import re

# -----------------------------
# 初期設定
# -----------------------------
st.set_page_config(page_title="YouTube 学習ループツール", layout="centered")

# -----------------------------
# session_state 初期化
# -----------------------------
if "urls" not in st.session_state:
    st.session_state.urls = [""] * 5

if "play" not in st.session_state:
    st.session_state.play = False

if "video_index" not in st.session_state:
    st.session_state.video_index = 0

if "start_time" not in st.session_state:
    st.session_state.start_time = None

if "limit_seconds" not in st.session_state:
    st.session_state.limit_seconds = 0

# -----------------------------
# タイトル
# -----------------------------
st.title("📺 YouTube 学習用 区間ループ再生ツール")

# -----------------------------
# URL入力
# -----------------------------
st.subheader("① YouTube URL（最大5本）")

for i in range(5):
    st.session_state.urls[i] = st.text_input(
        f"URL {i+1}", st.session_state.urls[i]
    )

# 有効なURLだけ抽出
def extract_video_id(url):
    match = re.search(r"(?:v=|youtu.be/)([A-Za-z0-9_-]{11})", url)
    return match.group(1) if match else None

video_ids = []
for url in st.session_state.urls:
    vid = extract_video_id(url)
    if vid:
        video_ids.append(vid)

# -----------------------------
# 区間指定
# -----------------------------
st.subheader("② 再生区間（秒）")

start_sec, end_sec = st.slider(
    "開始秒 → 終了秒",
    min_value=0,
    max_value=3600,
    value=(0, 30)
)

# -----------------------------
# ループ設定
# -----------------------------
st.subheader("③ 再生設定")

loop_single = st.checkbox("区間ループする", value=True)
loop_multi = st.checkbox("複数動画を順番に再生する", value=True)

# -----------------------------
# タイマー設定
# -----------------------------
st.subheader("④ 学習タイマー")

col1, col2 = st.columns(2)
with col1:
    hour = st.number_input("時間", min_value=0, max_value=10, value=0)
with col2:
    minute = st.number_input("分", min_value=0, max_value=59, value=0)

use_chime = st.checkbox("時間終了時にチャイムを鳴らす", value=True)
stop_after_time = st.checkbox("時間終了後に再生停止", value=True)

# -----------------------------
# 再生制御
# -----------------------------
st.subheader("⑤ 再生制御")

col1, col2 = st.columns(2)
with col1:
    if st.button("▶ 再生"):
        st.session_state.play = True
        st.session_state.video_index = 0
        st.session_state.start_time = time.time()
        st.session_state.limit_seconds = hour * 3600 + minute * 60

with col2:
    if st.button("⏹ 停止"):
        st.session_state.play = False

# -----------------------------
# 再生処理
# -----------------------------
if st.session_state.play and video_ids:
    current_video = video_ids[st.session_state.video_index]

    iframe_url = (
        f"https://www.youtube.com/embed/{current_video}"
        f"?start={start_sec}&end={end_sec}&autoplay=1&mute=1"
    )

    st.markdown(
        f"""
        <iframe width="560" height="315"
        src="{iframe_url}"
        frameborder="0"
        allow="autoplay">
        </iframe>
        """,
        unsafe_allow_html=True
    )

    # 経過時間チェック
    elapsed = time.time() - st.session_state.start_time
    remaining = st.session_state.limit_seconds - elapsed

    st.info(
        f"再生中：{st.session_state.video_index + 1} 本目 / "
        f"残り時間：{max(0, int(remaining))} 秒"
    )

    # タイマー終了判定
    if st.session_state.limit_seconds > 0 and remaining <= 0:
        st.session_state.play = False
        if use_chime:
            st.audio(
                "https://actions.google.com/sounds/v1/alarms/alarm_clock.ogg"
            )
        st.warning("⏰ 指定した学習時間が終了しました")

    # ループ制御
    if loop_single:
        time.sleep(end_sec - start_sec)
        if loop_multi:
            st.session_state.video_index += 1
            if st.session_state.video_index >= len(video_ids):
                st.session_state.video_index = 0
        st.rerun()

elif st.session_state.play and not video_ids:
    st.error("有効なYouTube URLがありません")
