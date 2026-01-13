import streamlit as st
from streamlit.components.v1 import html
import json

st.set_page_config(page_title="YouTube自動ループ再生", layout="centered")
st.title("📺 YouTube自動ループ再生ツール")

# -----------------------------
# URL入力
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

urls_js = json.dumps(urls)
limit_js = total_seconds * 1000
auto_stop_js = "true" if auto_stop else "false"

html_code = """
<!DOCTYPE html>
<html>
<head>
<style>
.video-block { margin-bottom: 28px; }
.hidden { display: none; }

.range-wrap {
  position: relative;
  height: 32px;
}
.range-wrap input[type=range] {
  position: absolute;
  width: 100%;
  pointer-events: none;
}
.range-wrap input::-webkit-slider-thumb {
  pointer-events: auto;
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

window.onYouTubeIframeAPIReady = function () {
  urls.forEach((url, i) => {
    const id = extractID(url);
    if (!id) return;

    const block = document.createElement("div");
    block.className = "video-block hidden";

    const playerDiv = document.createElement("div");

    const wrap = document.createElement("div");
    wrap.className = "range-wrap";

    const start = document.createElement("input");
    start.type = "range";
    start.step = 1;

    const end = document.createElement("input");
    end.type = "range";
    end.step = 1;

    wrap.appendChild(start);
    wrap.appendChild(end);

    block.appendChild(playerDiv);
    block.appendChild(wrap);
    document.getElementById("container").appendChild(block);

    blocks[i] = block;
    ranges[i] = [0, 0];

    players[i] = new YT.Player(playerDiv, {
      videoId: id,
      playerVars: { controls: 1, playsinline: 1 },
      events: {
        onReady: e => onReady(e, i),
        onStateChange: e => onStateChange(e, i)
      }
    });

    start.oninput = () => {
      if (start.value > end.value) start.value = end.value;
      ranges[i][0] = Number(start.value);
    };

    end.oninput = () => {
      if (end.value < start.value) end.value = start.value;
      ranges[i][1] = Number(end.value);
    };
  });
};

function onReady(event, i) {
  const d = Math.floor(event.target.getDuration());
  const inputs = blocks[i].querySelectorAll("input");

  inputs.forEach(input => input.max = d);
  inputs[1].value = d;

  ranges[i] = [0, d];

  if (i === 0) playCurrent();
}

function playCurrent() {
  blocks.forEach((b, i) => b.classList.toggle("hidden", i !== index));
  const p = players[index];
  p.seekTo(ranges[index][0], true);
  p.playVideo();
  monitor();
}

function onStateChange(event, i) {
  if (i === index && event.data === YT.PlayerState.PLAYING) monitor();
}

function monitor() {
  const now = Date.now();

  if (limit > 0 && now - startTime >= limit) {
    document.getElementById("chime").play();
    if (autoStop) return players[index].pauseVideo();
  }

  const p = players[index];
  if (p.getCurrentTime() >= ranges[index][1]) {
    p.seekTo(ranges[index][0], true);
  }

  requestAnimationFrame(monitor);
}
</script>

</body>
</html>
"""

html_code = (
    html_code
    .replace("__URLS__", urls_js)
    .replace("__LIMIT__", str(limit_js))
    .replace("__AUTOSTOP__", auto_stop_js)
)

html(html_code, height=680)
