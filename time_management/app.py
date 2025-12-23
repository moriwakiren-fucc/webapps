import streamlit as st
import json
import os
from datetime import date

# =========================
# データ保存用ファイル名
# =========================
DATA_FILE = "study_data.json"


# =========================
# データの読み込み
# =========================
def load_data():
    if os.path.exists(DATA_FILE):
        with open(DATA_FILE, "r", encoding="utf-8") as f:
            return json.load(f)
    else:
        return {
            "periods": [],
            "tasks": [],
            "records": []
        }


# =========================
# データの保存
# =========================
def save_data(data):
    with open(DATA_FILE, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)


# =========================
# 初期データ読み込み
# =========================
data = load_data()


# =========================
# タイトル
# =========================
st.title("📘 勉強管理アプリ")


# =========================
# 機能選択
# =========================
menu = st.radio(
    "機能を選んでください",
    ["ホーム", "期間登録", "タスク登録", "完了入力"]
)


# =========================
# ホーム
# =========================
if menu == "ホーム":
    st.subheader("ホーム画面")
    st.write("左のメニューから操作を選んでください。")

    st.write("### 登録済み期間")
    if len(data["periods"]) == 0:
        st.write("（まだ登録されていません）")
    else:
        for p in data["periods"]:
            st.write(f"- {p['name']}（{p['start']} ～ {p['end']}）")

    st.write("### 登録済みタスク")
    if len(data["tasks"]) == 0:
        st.write("（まだ登録されていません）")
    else:
        for t in data["tasks"]:
            if t["amount"] is None:
                st.write(f"- {t['name']}（量なし）")
            else:
                st.write(f"- {t['name']}（量：{t['amount']}）")


# =========================
# 期間登録
# =========================
elif menu == "期間登録":
    st.subheader("期間登録")

    period_name = st.text_input("期間名")
    start_date = st.date_input("開始日", value=date.today())
    end_date = st.date_input("終了日", value=date.today())

    if st.button("期間を登録"):
        if period_name == "":
            st.warning("期間名を入力してください")
        else:
            data["periods"].append({
                "name": period_name,
                "start": str(start_date),
                "end": str(end_date)
            })
            save_data(data)
            st.success("期間を登録しました！")


# =========================
# タスク登録
# =========================
elif menu == "タスク登録":
    st.subheader("タスク登録")

    task_name = st.text_input("タスク名")
    amount_input = st.text_input("量（未入力でもOK）")

    if st.button("タスクを登録"):
        if task_name == "":
            st.warning("タスク名を入力してください")
        else:
            if amount_input == "":
                amount = None
            else:
                amount = int(amount_input)

            data["tasks"].append({
                "name": task_name,
                "amount": amount
            })
            save_data(data)
            st.success("タスクを登録しました！")


# =========================
# 完了入力
# =========================
elif menu == "完了入力":
    st.subheader("完了入力")

    # タスクが1件もない場合の安全処理
    if len(data["tasks"]) == 0:
        st.warning("先にタスクを登録してください")
        st.stop()

    task_names = [t["name"] for t in data["tasks"]]
    selected_task = st.selectbox("タスクを選択", task_names)

    task_info = None
    for t in data["tasks"]:
        if t["name"] == selected_task:
            task_info = t
            break

    if task_info["amount"] is None:
        done = st.number_input("完了率（％）", min_value=0, max_value=100)
        unit = "%"
    else:
        done = st.number_input("完了量", min_value=0)
        unit = "量"

    if st.button("完了を記録"):
        data["records"].append({
            "task": selected_task,
            "done": done,
            "unit": unit
        })
        save_data(data)
        st.success("完了を記録しました！")
