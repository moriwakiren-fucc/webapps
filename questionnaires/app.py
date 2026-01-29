import streamlit as st
import pandas as pd
import random
import string
from openpyxl import Workbook, load_workbook
import os

st.set_page_config(page_title="アンケート管理", page_icon="📝")

EXCEL_FILE = "questionnaires.xlsx"

# =====================
# ユーティリティ
# =====================
def generate_id():
    return "".join(random.choices(string.ascii_lowercase + string.digits, k=15))

def valid_password(pw):
    return 1 <= len(pw) <= 15 and all(c in string.ascii_lowercase + string.digits for c in pw)

def get_wb():
    if not os.path.exists(EXCEL_FILE):
        wb = Workbook()
        ws = wb.active
        ws.title = "TOP"
        ws.append(["title", "id", "password", "one_time", "result_free"])
        wb.save(EXCEL_FILE)
    return load_workbook(EXCEL_FILE)

# =====================
# URL解析
# =====================
params = st.query_params

def norm(v):
    return v[0] if isinstance(v, list) else v

page = norm(params.get("page")) or "make_new"
qid = norm(params.get("id"))

# =====================
# 作成ページ
# =====================
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

            qid = generate_id()
            ws.append([title, qid, password, one_time, result_free])

            qws = wb.create_sheet(qid)
            wb.save(EXCEL_FILE)

            st.success("作成完了")
            st.code(f"?page=edit&id={qid}")
            st.code(f"?page=answer&id={qid}")

# =====================
# 編集ページ（PW必須）
# =====================
elif page == "edit":
    if not qid:
        st.error("IDが指定されていません")
        st.stop()

    wb = get_wb()
    top = wb["TOP"]

    record = None
    for r in top.iter_rows(min_row=2, values_only=True):
        if r[1] == qid:
            record = r
            break

    if not record:
        st.error("アンケートが存在しません")
        st.stop()

    pw = st.text_input("編集用パスワード", type="password")
    if pw != record[2]:
        st.warning("正しいパスワードを入力してください")
        st.stop()

    st.title(f"編集：{record[0]}")
    ws = wb[qid]

    q_type = st.selectbox(
        "質問タイプ",
        ["ラジオボタン", "ドロップダウン", "チェックボックス", "スライダー", "1行記述", "複数行記述"]
    )

    q_text = st.text_area("質問文（改行可・URL自動リンク）")
    required = st.checkbox("必須")
    choices = st.text_area("選択肢（改行区切り）※記述式は空欄")

    if st.button("質問を追加"):
        col = ws.max_column + 1 if ws.max_column >= 2 else 2
        ws.cell(row=1, column=col, value=q_type)
        ws.cell(row=2, column=col, value=q_text)
        ws.cell(row=3, column=col, value=str(required))
        ws.cell(row=4, column=col, value=choices)
        wb.save(EXCEL_FILE)
        st.success("質問を追加しました")

# =====================
# 回答ページ
# =====================
elif page == "answer":
    if not qid:
        st.error("IDが指定されていません")
        st.stop()

    wb = get_wb()
    top = wb["TOP"]

    record = None
    for r in top.iter_rows(min_row=2, values_only=True):
        if r[1] == qid:
            record = r
            break

    if not record:
        st.error("アンケートが存在しません")
        st.stop()

    ws = wb[qid]
    st.title(record[0])

    answers = []

    for col in range(2, ws.max_column + 1):
        q_type = ws.cell(1, col).value
        q_text = ws.cell(2, col).value
        choices = ws.cell(4, col).value

        st.markdown(q_text)

        if q_type in ["ラジオボタン", "ドロップダウン"]:
            opts = choices.split("\n")
            ans = st.radio("", opts, key=col) if q_type == "ラジオボタン" else st.selectbox("", opts, key=col)
        elif q_type == "チェックボックス":
            ans = st.checkbox("チェック", key=col)
        elif q_type == "スライダー":
            ans = st.slider("", 0, 10, key=col)
        elif q_type == "複数行記述":
            ans = st.text_area("", key=col)
        else:
            ans = st.text_input("", key=col)

        answers.append(ans)

    if st.button("送信"):
        row = ws.max_row + 1
        for i, a in enumerate(answers):
            ws.cell(row=row, column=i + 2, value=str(a))
        wb.save(EXCEL_FILE)
        st.success("回答ありがとうございました")

# =====================
# 結果ページ
# =====================
elif page == "result":
    if not qid:
        st.error("IDが指定されていません")
        st.stop()

    wb = get_wb()
    ws = wb[qid]

    headers = [ws.cell(2, c).value for c in range(2, ws.max_column + 1)]
    data = [
        [ws.cell(r, c).value for c in range(2, ws.max_column + 1)]
        for r in range(5, ws.max_row + 1)
    ]

    st.dataframe(pd.DataFrame(data, columns=headers))
