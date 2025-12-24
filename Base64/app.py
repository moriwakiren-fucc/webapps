import streamlit as st
import base64
import gzip
import io
from PIL import Image

st.set_page_config(page_title="Base64 GZIP Image Share App")
st.title("Base64 + GZIP 画像共有アプリ（自動圧縮）")

# =========================
# 設定
# =========================
MAX_BYTES = 80_000
MAX_WIDTH = 800
QUALITY_START = 85
QUALITY_MIN = 30

# =========================
# クエリ取得
# =========================
query_params = st.query_params
code_param = query_params.get("code")

# ★ 重要：list → str に変換
if isinstance(code_param, list):
    code_param = code_param[0]

# =========================
# URL → 復元
# =========================
if code_param:
    st.header("共有された画像")

    try:
        compressed_bytes = base64.urlsafe_b64decode(code_param)
        image_bytes = gzip.decompress(compressed_bytes)
        image = Image.open(io.BytesIO(image_bytes))
        st.image(image, use_container_width=True)
        st.success("画像を復元しました")

    except Exception as e:
        st.error("画像の復元に失敗しました")
        st.exception(e)  # ← デバッグ用（後で消してOK）

st.divider()

# =========================
# アップロード → 自動圧縮
# =========================
st.header("画像をアップロードして共有URLを作成")

uploaded_file = st.file_uploader(
    "画像を選択",
    type=["png", "jpg", "jpeg"]
)

if uploaded_file:
    original = Image.open(uploaded_file).convert("RGB")

    # 解像度縮小
    if original.width > MAX_WIDTH:
        ratio = MAX_WIDTH / original.width
        new_size = (MAX_WIDTH, int(original.height * ratio))
        original = original.resize(new_size, Image.LANCZOS)

    # JPEG再エンコード（画質調整）
    jpeg_bytes = None
    for quality in range(QUALITY_START, QUALITY_MIN - 1, -5):
        buffer = io.BytesIO()
        original.save(buffer, format="JPEG", quality=quality, optimize=True)
        data = buffer.getvalue()

        if len(data) <= MAX_BYTES:
            jpeg_bytes = data
            break

    if jpeg_bytes is None:
        st.error("サイズを十分に小さくできませんでした")
    else:
        compressed_bytes = gzip.compress(jpeg_bytes)
        encoded = base64.urlsafe_b64encode(compressed_bytes).decode("utf-8")

        st.query_params.clear()
        st.query_params["code"] = encoded

        st.image(jpeg_bytes)
        st.success("自動圧縮完了。ブラウザURLが共有URLです")
