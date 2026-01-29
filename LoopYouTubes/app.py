import streamlit as st
import pandas as pd
from datetime import datetime
import os

st.set_page_config(page_title="アンケートアプリ", page_icon="📝")

CSV_FILE = "survey_results.csv"

# ------------------------
# 初期化
# ------------------------
if "submitted" not in st.session_state:
    st.session_state.submitted = False

# CSVがなければ作成
if not os.path.exists(CSV_FILE):
    df_init = pd.DataFrame(
        columns=["timestamp", "name", "satisfaction", "features", "comment"]
    )
    df_init.to_csv(CSV_FILE, index=False)

# ------------------------
# ページ選択
# ------------------------
page = st.sidebar.selectbox(
    "ページ選択",
    ["アンケート回答", "回答一覧", "集計"]
)

# ========================
# アンケート回答ページ
# ========================
if page == "アンケート回答":
    st.title("アンケートご協力のお願い")

    if st.session_state.submitted:
        st.warning("このアンケートは1人1回までです。ご協力ありがとうございました。")
    else:
        name = st.text_input("お名前（任意）")

        satisfaction = st.radio(
            "今回の内容の満足度を教えてください",
            ["とても満足", "満足", "普通", "不満", "とても不満"]
        )

        features = st.multiselect(
            "良かった点を選んでください（複数可）",
            ["内容", "説明の分かりやすさ", "スピード", "デザイン", "その他"]
        )

        comment = st.text_area("ご意見・ご感想")

        if st.button("送信"):
            new_data = pd.DataFrame(
                [[
                    datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                    name,
                    satisfaction,
                    ",".join(features),
                    comment
                ]],
                columns=["timestamp", "name", "satisfaction", "features", "comment"]
            )

            new_data.to_csv(CSV_FILE, mode="a", header=False, index=False)

            st.session_state.submitted = True
            st.success("アンケートを送信しました。ありがとうございます！")

# ========================
# 回答一覧ページ
# ========================
elif page == "回答一覧":
    st.title("回答一覧")

    df = pd.read_csv(CSV_FILE)

    if df.empty:
        st.info("まだ回答がありません。")
    else:
        st.dataframe(df)

# ========================
# 集計ページ
# ========================
elif page == "集計":
    st.title("集計結果")

    df = pd.read_csv(CSV_FILE)

    if df.empty:
        st.info("まだ集計できるデータがありません。")
    else:
        st.subheader("満足度の件数")
        st.bar_chart(df["satisfaction"].value_counts())

        st.subheader("良かった点の集計")
        features_series = df["features"].dropna().str.split(",").explode()
        st.bar_chart(features_series.value_counts())
