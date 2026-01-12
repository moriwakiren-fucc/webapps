import streamlit as st
import cv2
import numpy as np
from PIL import Image
import os

# 保存フォルダ
SAVE_DIR = "pages"
os.makedirs(SAVE_DIR, exist_ok=True)

st.title("📚 教科書スキャン（iPad対応）")

st.write("📷 ページをめくって、ボタンを押すだけ")

# -------------------------
# カメラ向きの状態管理
# -------------------------
if "camera_mode" not in st.session_state:
    # 初期状態は背面カメラ
    st.session_state.camera_mode = "environment"

# 切り替えボタン
if st.button("🔄 前面 / 背面 カメラ切り替え"):
    if st.session_state.camera_mode == "environment":
        st.session_state.camera_mode = "user"
    else:
        st.session_state.camera_mode = "environment"

# 現在のカメラ表示
if st.session_state.camera_mode == "environment":
    st.info("📷 背面カメラ使用中")
else:
    st.info("🤳 前面カメラ使用中")

# 既存ページ数取得
page_count = len(os.listdir(SAVE_DIR))

def scan_like_process(img):
    """スキャナ風に画像を加工する"""
    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    blur = cv2.GaussianBlur(gray, (5, 5), 0)
    th = cv2.adaptiveThreshold(
        blur,
        255,
        cv2.ADAPTIVE_THRESH_GAUSSIAN_C,
        cv2.THRESH_BINARY,
        11,
        2
    )
    return th

# カメラ入力（前面 / 背面 切り替え対応）
camera_input = st.camera_input(
    "ページを撮影",
    facing_mode=st.session_state.camera_mode,
    key=st.session_state.camera_mode
)

if camera_input is not None:
    # PIL形式で読み込み
    image = Image.open(camera_input)

    # OpenCV形式へ変換
    frame = cv2.cvtColor(np.array(image), cv2.COLOR_RGB2BGR)

    # スキャン風加工
    processed = scan_like_process(frame)

    # ページ番号更新
    page_count += 1
    filename = f"{SAVE_DIR}/page_{page_count:03}.png"

    # 保存
    cv2.imwrite(filename, processed)

    st.success(f"{page_count} ページ保存しました")

    # プレビュー
    st.image(
        processed,
        caption="スキャン後プレビュー",
        use_container_width=True
    )
