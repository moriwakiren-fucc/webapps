import streamlit as st
from streamlit.components.v1 import html

st.set_page_config(page_title="YouTube自動ループ再生", layout="centered")

st.title("📺 YouTube自動ループ再生ツール")

urls = []
ranges = []

st.subheader("🔗 YouTube URL と再生区間")

for i in range(5):
    url = st.text_input(f"YouTube URL {i+1}", "")
    start, end = st.slider(
        f"再生区間 {i+1}（秒）",
        min_value=0,
        max_value=3600,
        value=(0, 60),
        step=1
    )
    urls.append(url)
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
<div id="player"></div>

<audio id="chime">
  <source src="https://actions.google.com/sounds/v1/alarms/digital_watch_alarm_long.ogg">
</audio>

<script src="https://www.youtube.com/iframe_api"></script>

<script>
let urls = {urls};
let ranges = {ranges};
let index = 0;
let player;
let startTime = Date.now();
let limit = {total_seconds * 1000};
let autoStop = {str(auto_stop).lower()};

function extractID(url) {{
  const m = url.match(/(?:v=|youtu\\.be\\/)([^&]+)/);
  return m ? m[1] : null;
}}

function onYouTubeIframeAPIReady() {{
  playVideo();
}}

function playVideo() {{
  const id = extractID(urls[index]);
  if (!id) {{
    index = (index + 1) % urls.length;
    playVideo();
    return;
  }}

  player = new YT.Player('player', {{
    videoId: id,
    playerVars: {{
      autoplay: 1,
      controls: 1,
      playsinline: 1
    }},
    events: {{
      onReady: onPlayerReady,
      onStateChange: onStateChange
    }}
  }});
}}

function onPlayerReady(event) {{
  event.target.seekTo(ranges[index][0], true);
  event.target.playVideo();
}}

function onStateChange(event) {{
  if (event.data === YT.PlayerState.PLAYING) {{
    checkTime();
  }}
}}

function checkTime() {{
  const now = Date.now();

  if (limit > 0 && now - startTime >= limit) {{
    document.getElementById("chime").play();
    if (autoStop) {{
      player.pauseVideo();
      return;
    }}
  }}

  const current = player.getCurrentTime();
  if (current >= ranges[index][1]) {{
    index = (index + 1) % urls.length;
    player.destroy();
    playVideo();
    return;
  }}

  requestAnimationFrame(checkTime);
}}
</script>
</body>
</html>
"""

html(html_code, height=400)
