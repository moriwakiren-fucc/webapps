import streamlit as st
import pandas as pd
import random
import string
from openpyxl import Workbook, load_workbook
import os

st.set_page_config(page_title="アンケート管理", page_icon="📝")

EXCEL_FILE = "questionnaires.xlsx"

# --------------------
# ユーティリティ
# --------------------
def generate_id():
    return "".join(random.choices(string.ascii_lowercase + string.digits, k=15))

def valid_password(pw):
    return 1 <= len(pw) <= 15 and all(c in string.ascii_lowercase + string.digits for c in pw)

def get_wb():
    if not os.path.exists(EXCEL_FILE):
        wb = Workbook()
        ws = wb.active
        ws.title = "TOP"
        ws.append(["title", "id", "password", "one_time_only", "result_no_password"])
        wb.save(EXCEL_FILE)
    return load_workbook(EXCEL_FILE)

# --------------------
# URL解析
# --------------------
params = st.query_params
page = params.get("page", "make_new")
qid = params.get("id", None)

# ====================
# 作成ページ
# ====================
if page == "make_new":
    st.title("アンケート新規作成")

    title = st.text_input("タイトル")
    password = st.text_input("編集・集計用パスワード", type="password")
    one_time = st.checkbox("1人1回のみ回答可", value=True)
    result_free = st.checkbox("集計ページをパスワードなしで公開")

    if st.button("作成"):
        if not title:
            st.error("タイトルを入力してください")
        elif not valid_password(password):
            st.error("パスワードは英小文字と数字のみ、1〜15文字です")
        else:
            wb = get_wb()
            ws = wb["TOP"]

            new_id = generate_id()
            ws.append([title, new_id, password, one_time, result_free])

            ws_q = wb.create_sheet(new_id)
            wb.save(EXCEL_FILE)

            st.success("作成しました")
            st.write("編集ページ：")
            st.code(f"?page=edit&id={new_id}")

# ====================
# 編集ページ
# ====================
elif page == "edit" and qid:
    wb = get_wb()
    ws_top = wb["TOP"]

    record = None
    for row in ws_top.iter_rows(min_row=2, values_only=True):
        if row[1] == qid:
            record = row
            break

    if not record:
        st.error("IDが存在しません")
        st.stop()

    st.title(f"編集ページ：{record[0]}")

    pw = st.text_input("パスワード", type="password")
    if pw != record[2]:
        st.warning("パスワードを入力してください")
        st.stop()

    ws = wb[qid]

    st.subheader("質問追加")

    q_type = st.selectbox(
        "質問タイプ",
        ["ラジオボタン", "ドロップダウン", "チェックボックス", "スライダー", "1行記述", "複数行記述"]
    )

    q_text = st.text_area("質問文（改行可・URLは自動リンク）")
    required = st.checkbox("必須")

    if st.button("質問を追加"):
        col = ws.max_column + 1 if ws_
