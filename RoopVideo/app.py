import streamlit as st
from streamlit.components.v1 import html

st.set_page_config(page_title="YouTube自動ループ再生", layout="centered")
st.title("📺 YouTube自動ループ再生ツール")

urls = []
ranges = []

st.subheader("🔗 YouTube URL と再生区間")

for i in range(5):
    url = st.text_input(f"YouTube URL {i+1}", "")
    urls.append(url)

    start, end = st.slider(
        f"再生区間 {i+1}（秒）",
        min_value=0,
        max_value=1,   # ← JS側で上書きされる
        value=(0, 1),
        step=1,
        key=f"slider_{i}"
    )
    ranges.append((start, end))

st.subheader("⏱ 時間指定")
h = st.number_input("時間（h）", min_value=0, max_value=24, value=0)
m = st.number_input("分（m）", min_value=0, max_value=59, value=0)
auto_stop = st.checkbox("指定時間経過後に自動で再生を止める")

total_seconds = h * 3600 + m * 60

html_code = f"""
<!DOCTYPE html>
<html>
<body>

<div id="players"></div>

<audio id="chime">
  <source src="https://actions.google.com/sounds/v1/alarms/digital_watch_alarm_long.ogg">
</audio>

<script src="https://www.youtube.com/iframe_api"></script>

<script>
const urls = {urls};
const ranges = {ranges};
let players = [];
let index = 0;
let startTime = Date.now();
const limit = {total_seconds * 1000};
const autoStop = {str(auto_stop).lower()};

function extractID(url) {{
  const m = url.match(/(?:v=|youtu\\.be\\/)([^&]+)/);
  return m ? m[1] : null;
}}

function onYouTubeIframeAPIReady() {{
  urls.forEach((url, i) => {{
    const id = extractID(url);
    if (!id) return;

    const wrapper = document.createElement("div");
    wrapper.id = "wrap_" + i;
    wrapper.style.display = "none";   // ← 非再生中は見えない
    document.getElementById("players").appendChild(wrapper);

    players[i] = new YT.Player(wrapper, {{
      videoId: id,
      playerVars: {{
        autoplay: 0,
        controls: 1,
        playsinline: 1
      }},
      events: {{
        onReady: e => onReady(e, i),
        onStateChange: e => onStateChange(e, i)
      }}
    }});
  }});

  playCurrent();
}}

function onReady(event, i) {{
  const d = event.target.getDuration();
  if (ranges[i][1] <= 1) {{
    ranges[i][1] = d;
  }}
}}

function playCurrent() {{
  players.forEach((p, i) => {{
    document.getElementById("wrap_" + i).style.display =
      i === index ? "block" : "none";
  }});

  const p = players[index];
  p.seekTo(ranges[index][0], true);
  p.playVideo();
  monitor();
}}

function onStateChange(event, i) {{
  if (i === index && event.data === YT.PlayerState.PLAYING) {{
    monitor();
  }}
}}

function monitor() {{
  const now = Date.now();

  if (limit > 0 && now - startTime >= limit) {{
    document.getElementById("chime").play();
    if (autoStop) {{
      players[index].pauseVideo();
      return;
    }}
  }}

  const p = players[index];
  if (p.getCurrentTime() >= ranges[index][1]) {{
    p.pauseVideo();
    index = (index + 1) % players.length;
    playCurrent();
    return;
  }}

  requestAnimationFrame(monitor);
}}
</script>

</body>
</html>
"""

html(html_code, height=450)
