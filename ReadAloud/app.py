import streamlit as st
import pandas as pd

# -----------------------------
# ページ設定
# -----------------------------
st.set_page_config(
    page_title="CSV表示アプリ",
    layout="centered"
)

st.title("📄 Googleスプレッドシート CSVビューア")

# -----------------------------
# CSV URL 入力
# -----------------------------
csv_url = "https://docs.google.com/spreadsheets/d/e/2PACX-1vTiQ2zC-T-KD08eexHIlfP1-RHvj5Iu7tRA61oQpSBEvTyq0dgqr4bUlnMA2FSu1QrsTgLmnOeag8XQ/pub?gid=360713345&single=true&output=csv"

# -----------------------------
# CSV 読み込み
# -----------------------------
if csv_url:
    try:
        df = pd.read_csv(csv_url)

        # A, B, C列のみ使用
        df = df.iloc[:, :3]
        df.columns = ["timestamp", "name", "body"]

        # -----------------------------
        # HTMLテーブル生成
        # -----------------------------
        html = """
        <style>
        table {
            width: 100%;
            border-collapse: collapse;
        }
        td {
            padding: 8px;
            vertical-align: top;
        }
        .odd td {
            border-bottom: none;
        }
        .even td {
            border-top: none;
        }
        .timestamp {
            width: 30%;
            font-size: 0.9em;
            color: #666;
        }
        .name {
            width: 70%;
            font-weight: bold;
        }
        .body {
            padding-left: 12px;
        }
        </style>
        <table>
        """

        for _, row in df.iterrows():
            html += f"""
            <tr class="odd">
                <td class="timestamp">{row['timestamp']}</td>
                <td class="name">{row['name']}</td>
            </tr>
            <tr class="even">
                <td class="body" colspan="2">{row['body']}</td>
            </tr>
            """

        html += "</table>"

        st.markdown(html, unsafe_allow_html=True)

    except Exception as e:
        st.error("CSVの読み込みに失敗しました")
        st.exception(e)
