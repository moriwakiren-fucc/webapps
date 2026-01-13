import streamlit as st
from streamlit.components.v1 import html

st.set_page_config(page_title="YouTube自動ループ再生", layout="centered")

st.title("📺 YouTube自動ループ再生ツール")

urls = []

st.subheader("🔗 YouTube URL（最大5本）")
for i in range(5):
    urls.append(st.text_input(f"YouTube URL {i+1}", ""))

st.subheader("⏱ 時間指定")
h = st.number_input("時間（h）", min_value=0, max_value=24, value=0)
m = st.number_input("分（m）", min_value=0, max_value=59, value=0)
auto_stop = st.checkbox("指定時間経過後に自動で再生を止める")

total_seconds = h * 3600 + m * 60

html_code = f"""
<!DOCTYPE html>
<html>
<body>

<div id="player" style="width:100%;"></div>

<audio id="chime">
  <source src="https://actions.google.com/sounds/v1/alarms/digital_watch_alarm_long.ogg">
</audio>

<script src="https://www.youtube.com/iframe_api"></script>

<script>
const urls = {urls};
let index = 0;
let player;
let duration = 0;
let start = 0;
let end = 0;
let startTime = Date.now();
const limit = {total_seconds * 1000};
const autoStop = {str(auto_stop).lower()};

function extractID(url) {{
  const m = url.match(/(?:v=|youtu\\.be\\/)([^&]+)/);
  return m ? m[1] : null;
}}

function onYouTubeIframeAPIReady() {{
  loadVideo();
}}

function loadVideo() {{
  const id = extractID(urls[index]);
  if (!id) {{
    index = (index + 1) % urls.length;
    loadVideo();
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
      onReady: onReady,
      onStateChange: onStateChange
    }}
  }});
}}

function onReady(event) {{
  duration = player.getDuration();
  start = 0;
  end = duration;
  player.seekTo(start, true);
  player.playVideo();
}}

function onStateChange(event) {{
  if (event.data === YT.PlayerState.PLAYING) {{
    monitor();
  }}
}}

function monitor() {{
  const now = Date.now();

  if (limit > 0 && now - startTime >= limit) {{
    document.getElementById("chime").play();
    if (autoStop) {{
      player.pauseVideo();
      return;
    }}
  }}

  if (player.getCurrentTime() >= end) {{
    index = (index + 1) % urls.length;
    player.destroy();
    loadVideo();
    return;
  }}

  requestAnimationFrame(monitor);
}}
</script>

</body>
</html>
"""

html(html_code, height=420)
