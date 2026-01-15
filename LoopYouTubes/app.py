import streamlit as st
import time
import re

# -----------------------------
# 初期設定
# -----------------------------
st.set_page_config(
    page_title="YouTube 学習ループツール",
    layout="wide"
)

# -----------------------------
# 補助関数
# -----------------------------
def extract_video_id(url):
    match = re.search(r"(?:v=|youtu.be/)([A-Za-z0-9_-]{11})", url)
    return match.group(1) if match else None


def format_time(sec, has_hour):
    h = sec // 3600
    m = (sec % 3600) // 60
    s = sec % 60
    if has_hour:
        return f"{h}:{m:02}:{s:02}"
    else:
        return f"{m}:{s:02}"


# -----------------------------
# session_state 初期化
# -----------------------------
if "videos" not in st.session_state:
    st.session_state.videos = [
        {"url": "", "start": 0, "end": 30}
        for _ in range(5)
    ]

if "playing" not in st.session_state:
    st.session_state.playing = False

if "video_index" not in st.session_state:
    st.session_state.video_index = 0

# -----------------------------
# タイトル
# -----------------------------
st.title("📺 YouTube 学習用 区間ループ再生ツール")

# -----------------------------
# URL & 区間プリセット
# -----------------------------
st.subheader("① URL & 区間プリセット")

for i, v in enumerate(st.session_state.videos):
    with st.expander(f"動画 {i+1}", expanded=(i == 0)):
        v["url"] = st.text_input(
            "YouTube URL",
            v["url"],
            key=f"url_{i}"
        )

        has_hour = v["end"] >= 3600

        start, end = st.slider(
            "再生区間",
            0,
            7200,
            (v["start"], v["end"]),
            format="%d",
            key=f"slider_{i}"
        )

        v["start"] = start
        v["end"] = end

        st.caption(
            f"区間：{format_time(start, has_hour)} "
            f"〜 {format_time(end, has_hour)}"
        )

# -----------------------------
# 再生設定
# -----------------------------
st.subheader("② 再生設定")

loop_section = st.checkbox("区間ループ", value=True)
loop_multi = st.checkbox("複数動画を順番にループ", value=True)

# -----------------------------
# 再生制御
# -----------------------------
st.subheader("③ 再生制御")

col1, col2 = st.columns(2)
with col1:
    if st.button("▶ 再生", use_container_width=True):
        st.session_state.playing = True
        st.session_state.video_index = 0

with col2:
    if st.button("⏹ 停止", use_container_width=True):
        st.session_state.playing = False

# -----------------------------
# 再生処理
# -----------------------------
valid_videos = []
for v in st.session_state.videos:
    vid = extract_video_id(v["url"])
    if vid and v["end"] > v["start"]:
        valid_videos.append(
            {"id": vid, "start": v["start"], "end": v["end"]}
        )

if st.session_state.playing and valid_videos:
    v = valid_videos[st.session_state.video_index]

    iframe_url = (
        f"https://www.youtube.com/embed/{v['id']}"
        f"?start={v['start']}&end={v['end']}&autoplay=1&mute=1"
    )

    st.markdown(
        f"""
        <div style="position:relative;padding-top:56.25%;">
          <iframe
            src="{iframe_url}"
            style="position:absolute;top:0;left:0;width:100%;height:100%;"
            frameborder="0"
            allow="autoplay">
          </iframe>
        </div>
        """,
        unsafe_allow_html=True
    )

    st.info(
        f"{st.session_state.video_index + 1} / {len(valid_videos)} 本目"
    )

    # 再生区間分待つ
    time.sleep(v["end"] - v["start"])

    # 次の挙動
    if loop_section:
        # 同じ動画・同じ区間を再生
        pass
    else:
        if loop_multi:
            st.session_state.video_index += 1
            if st.session_state.video_index >= len(valid_videos):
                st.session_state.video_index = 0
        else:
            st.session_state.playing = False

    st.rerun()

elif st.session_state.playing:
    st.error("再生可能な動画がありません")
