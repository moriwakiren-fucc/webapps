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

# ===== 反転スイッチ =====
flip_image = st.toggle("🔄 画像を左右反転する", value=False)

# 現在の保存枚数
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

# iPad対応カメラ入力
camera_input = st.camera_input("ページを撮影")

if camera_input is not None:
    # PIL形式で読み込み
    image = Image.open(camera_input)

    # OpenCV形式へ変換
    frame = cv2.cvtColor(np.array(image), cv2.COLOR_RGB2BGR)

    # ===== 反転処理 =====
    if flip_image:
        frame = cv2.flip(frame, 1)

    # スキャン風加工
    processed = scan_like_process(frame)

    # ページ番号更新
    page_count += 1
    filename = f"{SAVE_DIR}/page_{page_count:03}.png"

    # 保存
    cv2.imwrite(filename, processed)

    st.success(f"{page_count} ページ保存しました")

    # プレビュー表示
    st.image(
        processed,
        caption="スキャン後プレビュー",
        use_container_width=True
    )
