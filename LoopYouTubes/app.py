import streamlit as st
import re

# -----------------------------
# 初期設定
# -----------------------------
st.set_page_config(
    page_title="YouTube 学習用 区間ループツール",
    layout="wide"
)

# -----------------------------
# 補助関数
# -----------------------------
def extract_video_id(url):
    m = re.search(r"(?:v=|youtu.be/)([A-Za-z0-9_-]{11})", url)
    return m.group(1) if m else None


def sec_to_label(sec):
    h = sec // 3600
    m = (sec % 3600) // 60
    s = sec % 60
    if h > 0:
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

if "index" not in st.session_state:
    st.session_state.index = 0

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

        start, end = st.slider(
            "再生区間（秒）",
            0,
            7200,
            (v["start"], v["end"]),
            key=f"slider_{i}"
        )

        v["start"] = start
        v["end"] = end

        st.caption(
            f"区間：{sec_to_label(start)} 〜 {sec_to_label(end)}"
        )

# -----------------------------
# 再生設定
# -----------------------------
st.subheader("② 再生設定")

loop_section = st.checkbox("区間ループ", value=True)
loop_multi = st.checkbox("複数動画を順番に再生", value=True)

# -----------------------------
# 再生制御
# -----------------------------
col1, col2 = st.columns(2)

with col1:
    if st.button("▶ 再生", use_container_width=True):
        st.session_state.playing = True
        st.session_state.index = 0

with col2:
    if st.button("⏹ 停止", use_container_width=True):
        st.session_state.playing = False

# -----------------------------
# 有効動画抽出
# -----------------------------
valid = []
for v in st.session_state.videos:
    vid = extract_video_id(v["url"])
    if vid and v["end"] > v["start"]:
        valid.append(
            {"id": vid, "start": v["start"], "end": v["end"]}
        )

# -----------------------------
# 再生表示
# -----------------------------
if st.session_state.playing and valid:

    v = valid[st.session_state.index]

    params = {
        "start": v["start"],
        "end": v["end"],
        "autoplay": 1,
        "mute": 1
    }

    # 🔥 ここが核心
    if loop_section:
        params["loop"] = 1
        params["playlist"] = v["id"]

    url_param = "&".join(
        [f"{k}={v}" for k, v in params.items()]
    )

    iframe_url = f"https://www.youtube.com/embed/{v['id']}?{url_param}"

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
        f"{st.session_state.index + 1} / {len(valid)} 本目"
    )

    # ▶ 次へボタン（順番再生用）
    if loop_multi and not loop_section:
        if st.button("▶ 次の動画へ"):
            st.session_state.index += 1
            if st.session_state.index >= len(valid):
                st.session_state.index = 0
            st.rerun()

elif st.session_state.playing:
    st.error("再生可能な動画がありません")
