import streamlit as st
from streamlit.components.v1 import html
import json

st.set_page_config(page_title="YouTube自動ループ再生", layout="centered")
st.title("📺 YouTube自動ループ再生ツール")

# -----------------------------
# YouTube URL 入力
# -----------------------------
urls = []
st.subheader("🔗 YouTube URL（最大5本）")
for i in range(5):
    urls.append(st.text_input(f"YouTube URL {i+1}", ""))

# -----------------------------
# 時間指定
# -----------------------------
st.subheader("⏱ 時間指定")
h = st.number_input("時間（h）", min_value=0, max_value=24, value=0)
m = st.number_input("分（m）", min_value=0, max_value=59, value=0)
auto_stop = st.checkbox("指定時間経過後に自動で再生を止める")

total_seconds = h * 3600 + m * 60

# Python → JS に安全に渡す
urls_js = json.dumps(urls)
limit_js = total_seconds * 1000
auto_stop_js = "true" if auto_stop else "false"

# -----------------------------
# HTML + JavaScript
# -----------------------------
html_code = """
<!DOCTYPE html>
<html>
<head>
<style>
.video-block {
  margin-bottom: 24px;
}
.hidden {
  display: none;
}
</style>
</head>
<body>

<div id="container"></div>

<audio id="chime">
  <source src="https://actions.google.com/sounds/v1/alarms/digital_watch_alarm_long.ogg">
</audio>

<script src="https://www.youtube.com/iframe_api"></script>

<script>
const urls = __URLS__;
let players = [];
let blocks = [];
let ranges = [];
let index = 0;

const startTime = Date.now();
const limit = __LIMIT__;
const autoStop = __AUTOSTOP__;

function extractID(url) {
  const m = url.match(/(?:v=|youtu\\.be\\/)([^&]+)/);
  return m ? m[1] : null;
}

function onYouTubeIframeAPIReady() {
  urls.forEach((url, i) => {
    const id = extractID(url);
    if (!id) return;

    const block = document.createElement("div");
    block.className = "video-block hidden";
    block.id = "block_" + i;

    const playerDiv = document.createElement("div");
    playerDiv.id = "player_" + i;

    const slider = document.createElement("input");
    slider.type = "range";
    slider.min = 0;
    slider.step = 1;

    block.appendChild(playerDiv);
    block.appendChild(slider);
    document.getElementById("container").appendChild(block);

    blocks[i] = block;
    ranges[i] = [0, 0];

    players[i] = new YT.Player(playerDiv, {
      videoId: id,
      playerVars: {
        autoplay: 0,
        controls: 1,
        playsinline: 1
      },
      events: {
        onReady: e => onReady(e, i),
        onStateChange: e => onStateChange(e, i)
      }
    });
  });
}

function onReady(event, i) {
  const d = Math.floor(event.target.getDuration());
  const slider = blocks[i].querySelector("input");

  slider.max = d;
  slider.value = d;
  ranges[i] = [0, d];

  slider.oninput = () => {
    ranges[i][1] = Number(slider.value);
  };

  if (i === 0) {
    playCurrent();
  }
}

function playCurrent() {
  blocks.forEach((b, i) => {
    b.classList.toggle("hidden", i !== index);
  });

  const p = players[index];
  p.seekTo(ranges[index][0], true);
  p.playVideo();
  monitor();
}

function onStateChange(event, i) {
  if (i === index && event.data === YT.PlayerState.PLAYING) {
    monitor();
  }
}

function monitor() {
  const now = Date.now();

  if (limit > 0 && now - startTime >= limit) {
    document.getElementById("chime").play();
    if (autoStop) {
      players[index].pauseVideo();
      return;
    }
  }

  const p = players[index];
  if (p.getCurrentTime() >= ranges[index][1]) {
    p.pauseVideo();
    index = (index + 1) % players.length;
    playCurrent();
    return;
  }

  requestAnimationFrame(monitor);
}
</script>

</body>
</html>
"""

# Python の値を安全に埋め込む
html_code = (
    html_code
    .replace("__URLS__", urls_js)
    .replace("__LIMIT__", str(limit_js))
    .replace("__AUTOSTOP__", auto_stop_js)
)

html(html_code, height=600)
