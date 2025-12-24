import streamlit as st
import base64
import io
import requests
from PIL import Image

st.set_page_config(page_title="Base64 Image Share App")
st.title("Base64 画像共有アプリ")

# =========================
# クエリパラメータ取得（新APIのみ使用）
# =========================
query_params = st.query_params
code_param = query_params.get("code")

# =========================
# URL短縮関数
# =========================
def shorten_url(long_url):
    api_url = "https://tinyurl.com/api-create.php"
    response = requests.get(api_url, params={"url": long_url})
    return response.text

# =========================
# 共有URLから画像を復元
# =========================
if code_param:
    st.header("共有された画像")

    try:
        image_bytes = base64.urlsafe_b64decode(code_param)
        image = Image.open(io.BytesIO(image_bytes))
        st.image(image, use_container_width=True)
        st.success("URLから画像を復元しました")

    except Exception:
        st.error("画像の復元に失敗しました")

st.divider()

# =========================
# 画像アップロード → URL生成
# =========================
st.header("画像をアップロードして共有URLを作成")

uploaded_file = st.file_uploader(
    "画像を選択",
    type=["png", "jpg", "jpeg"]
)

if uploaded_file:
    image_bytes = uploaded_file.read()
    encoded = base64.urlsafe_b64encode(image_bytes).decode("utf-8")

    # 現在のアプリURLを取得
    base_url = st.request.url_root.rstrip("/")

    full_url = f"{base_url}?code={encoded}"
    short_url = shorten_url(full_url)

    st.image(image_bytes)
    st.text_input("短縮URL（コピー可）", short_url)

st.divider()

# =========================
# 通常の Base64 エンコード / デコード
# =========================
st.header("Base64 エンコード / デコード（テキスト）")

text_input = st.text_area("テキストを入力")

col1, col2 = st.columns(2)

with col1:
    if st.button("エンコード"):
        encoded_text = base64.b64encode(text_input.encode()).decode()
        st.text_area("エンコード結果", encoded_text)

with col2:
    if st.button("デコード"):
        try:
            decoded_text = base64.b64decode(text_input).decode()
            st.text_area("デコード結果", decoded_text)
        except Exception:
            st.error("デコードに失敗しました")
