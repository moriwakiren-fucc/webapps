import streamlit as st
import base64
import gzip
import io
from PIL import Image

st.set_page_config(page_title="Base64 GZIP Image Share App")
st.title("Base64 + GZIP 画像共有アプリ")

# =========================
# クエリパラメータ取得
# =========================
query_params = st.query_params
code_param = query_params.get("code")

# =========================
# URL → Base64デコード → GZIP解凍 → 画像表示
# =========================
if code_param:
    st.header("共有された画像")

    try:
        compressed_bytes = base64.urlsafe_b64decode(code_param)
        image_bytes = gzip.decompress(compressed_bytes)
        image = Image.open(io.BytesIO(image_bytes))
        st.image(image, use_container_width=True)
        st.success("画像を復元しました")

    except Exception:
        st.error("画像の復元に失敗しました")

st.divider()

# =========================
# 画像アップロード → GZIP圧縮 → Base64 → URL生成
# =========================
st.header("画像をアップロードして共有URLを作成")

uploaded_file = st.file_uploader(
    "画像を選択",
    type=["png", "jpg", "jpeg"]
)

if uploaded_file:
    image_bytes = uploaded_file.read()

    # GZIP圧縮
    compressed_bytes = gzip.compress(image_bytes)

    # Base64エンコード（URL安全）
    encoded = base64.urlsafe_b64encode(compressed_bytes).decode("utf-8")

    # URLを更新（これが共有URL）
    st.query_params.clear()
    st.query_params["code"] = encoded

    st.image(image_bytes)
    st.success("ブラウザのURLが共有URLです（コピーしてください）")
