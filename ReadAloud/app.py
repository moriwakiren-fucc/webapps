import streamlit as st
import re
import io
import zipfile
from datetime import datetime
from pathlib import Path

st.set_page_config(layout='wide')

# -----------------------------
# ページ設定
# -----------------------------
st.set_page_config(
    page_title="ファイル名ルール統一ツール",
    layout="centered"
)

st.title("📂 ファイル名ルール統一 自動整形ツール")

# -----------------------------
# ファイルアップロード
# -----------------------------
uploaded_files = st.file_uploader(
    "ファイルをアップロード（複数可）",
    accept_multiple_files=True
)

# -----------------------------
# 命名ルール設定
# -----------------------------
st.subheader("① 命名ルール設定")

use_number = st.checkbox("連番を付ける", value=True)
start_number = st.number_input("開始番号", min_value=1, value=1)
digit = st.selectbox("桁数", [2, 3, 4], index=1)

use_date = st.checkbox("日付を付ける", value=True)
date_format = st.selectbox(
    "日付形式",
    ["YYYYMMDD", "YYYY-MM-DD"]
)

use_original = st.checkbox("元のファイル名を使う", value=True)

space_to_underscore = st.checkbox("空白を _ に変換", value=True)
remove_symbol = st.checkbox("記号を削除する", value=True)

case_rule = st.selectbox(
    "大文字・小文字",
    ["変更しない", "小文字に統一", "大文字に統一"]
)

# -----------------------------
# 命名ルール処理関数
# -----------------------------
def normalize_name(name):
    if space_to_underscore:
        name = name.replace(" ", "_")

    if remove_symbol:
        name = re.sub(r"[^\w\-]", "", name)

    if case_rule == "小文字に統一":
        name = name.lower()
    elif case_rule == "大文字に統一":
        name = name.upper()

    return name

# -----------------------------
# プレビュー生成
# -----------------------------
preview = []

if uploaded_files:
    today = datetime.now().strftime(
        "%Y%m%d" if date_format == "YYYYMMDD" else "%Y-%m-%d"
    )

    for i, file in enumerate(uploaded_files):
        original = Path(file.name)
        stem = original.stem
        suffix = original.suffix

        parts = []

        if use_number:
            parts.append(str(start_number + i).zfill(digit))

        if use_date:
            parts.append(today)

        if use_original:
            parts.append(normalize_name(stem))

        new_name = "_".join(parts) + suffix

        preview.append(
            {
                "Before": file.name,
                "After": new_name
            }
        )

# -----------------------------
# プレビュー表示
# -----------------------------
st.subheader("② プレビュー")

if preview:
    st.dataframe(preview, use_container_width=True)
else:
    st.info("ファイルをアップロードしてください")

# -----------------------------
# ZIPダウンロード
# -----------------------------
if preview and st.button("ZIPでダウンロード"):
    zip_buffer = io.BytesIO()

    with zipfile.ZipFile(zip_buffer, "w") as zf:
        for item, file in zip(preview, uploaded_files):
            zf.writestr(item["After"], file.read())

    zip_buffer.seek(0)

    st.download_button(
        label="📥 ダウンロード",
        data=zip_buffer,
        file_name="renamed_files.zip",
        mime="application/zip"
    )
