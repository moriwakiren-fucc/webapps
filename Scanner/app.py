import streamlit as st
import cv2
import numpy as np
from PIL import Image
import time
import os

# 撮影したページ画像を保存するフォルダ
SAVE_DIR = "pages"
os.makedirs(SAVE_DIR, exist_ok=True)

# アプリのタイトル
st.title("📚 教科書 自動スキャンアプリ")

# チェックが入ると撮影開始
run = st.checkbox("撮影を開始する")

# カメラ映像表示用
frame_window = st.image([])

# 状態表示用（ページ保存メッセージなど）
status = st.empty()

# カメラ起動（通常は0でOK）
cap = cv2.VideoCapture(0)

# 前フレーム保存用
last_frame = None

# 保存したページ数
page_count = 0

# 動いていないと判定するための閾値
STILL_THRESHOLD = 3.0

# 静止してから撮影するまでの時間（秒）
STILL_TIME = 0.8

# 最後に動きがあった時刻
last_change_time = time.time()

def scan_like_process(img):
    """スキャナ風に画像を加工する関数"""
    # グレースケール変換
    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)

    # ノイズ除去のためのぼかし
    blur = cv2.GaussianBlur(gray, (5, 5), 0)

    # 自動二値化で文字をくっきりさせる
    th = cv2.adaptiveThreshold(
        blur,
        255,
        cv2.ADAPTIVE_THRESH_GAUSSIAN_C,
        cv2.THRESH_BINARY,
        11,
        2
    )
    return th

# 撮影ループ
while run:
    # カメラから1フレーム取得
    ret, frame = cap.read()
    if not ret:
        break

    # Streamlit表示用に色変換
    display = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
    frame_window.image(display)

    # 前のフレームがある場合のみ動き判定
    if last_frame is not None:
        # 前フレームとの差分を計算
        diff = cv2.absdiff(frame, last_frame)
        motion = np.mean(diff)

        # 動きが少ない場合（ページが止まっている）
        if motion < STILL_THRESHOLD:
            # 一定時間静止していたら撮影
            if time.time() - last_change_time > STILL_TIME:
                page_count += 1

                # スキャン風加工
                processed = scan_like_process(frame)

                # ファイル名作成（連番）
                filename = f"{SAVE_DIR}/page_{page_count:03}.png"

                # 画像保存
                cv2.imwrite(filename, processed)

                # 状態表示
                status.success(f"{page_count} ページ保存")

                # 二重撮影防止のため時刻更新
                last_change_time = time.time()
        else:
            # 動きがあったら時刻更新
            last_change_time = time.time()

    # 現在のフレームを保存
    last_frame = frame.copy()

# カメラ解放
cap.release()
