import streamlit as st

st.set_page_config(page_title="アンケート", page_icon="📝")

st.title("アンケートご協力のお願い")

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
    st.success("アンケートを送信しました。ありがとうございます！")

    st.subheader("あなたの回答")
    st.write("名前：", name if name else "未記入")
    st.write("満足度：", satisfaction)
    st.write("良かった点：", features)
    st.write("コメント：", comment if comment else "なし")
