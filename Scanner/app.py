import streamlit as st
import cv2
import numpy as np
from PIL import Image
import os

# 保存フォルダ
SAVE_DIR = "pages"
os.makedirs(SAVE_DIR, exist_ok=True)

st.title("📚 教科書スキャン（iPad対応）")
st.write("📷 ページをめくって、撮影ボタンを押してください")

# -------------------------
# カメラ向き（UI用）
# -------------------------
camera_mode = st.radio(
    "使用中のカメラ",
    ["背面カメラ", "前面カメラ"],
    horizontal=True
)

if camera_mode == "背面カメラ":
    st.info("📷 iPadのカメラUIで『背面』を選択してください")
else:
    st.info("🤳 iPadのカメラUIで『前面』を選択してください")

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

# カメラ入力（Streamlit公式）
camera_input = st.camera_input("ページを撮影")

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
