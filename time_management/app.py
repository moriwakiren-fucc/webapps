import streamlit as st
import json
import os
from datetime import date
import pandas as pd
import plotly.express as px
from icalendar import Calendar

DATA_FILE = "data.json"


def load_data():
    if not os.path.exists(DATA_FILE):
        return {"periods": [], "tasks": [], "logs": [], "events": []}
    with open(DATA_FILE, "r", encoding="utf-8") as f:
        return json.load(f)


def save_data(data):
    with open(DATA_FILE, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)


data = load_data()

st.title("📘 勉強管理アプリ")

menu = st.sidebar.radio(
    "メニュー",
    ["ホーム", "期間登録", "タスク登録", "完了入力", "カレンダー"]
)

# --------------------
# ホーム画面
# --------------------
if menu == "ホーム":
    st.header("📊 進捗状況")

    if len(data["logs"]) == 0:
        st.info("まだ完了データがありません")
    else:
        df = pd.DataFrame(data["logs"])
        summary = df.groupby("task")["amount"].sum().reset_index()
        fig = px.bar(summary, x="task", y="amount", title="タスク別進捗")
        st.plotly_chart(fig, use_container_width=True)

# --------------------
# 期間登録
# --------------------
elif menu == "期間登録":
    st.header("📅 期間登録")

    name = st.text_input("期間名")
    start = st.date_input("開始日")
    end = st.date_input("終了日")

    if st.button("登録"):
        data["periods"].append({
            "name": name,
            "start": str(start),
            "end": str(end)
        })
        save_data(data)
        st.success("期間を登録しました")

# --------------------
# タスク登録
# --------------------
elif menu == "タスク登録":
    st.header("📝 タスク登録")

    period_names = [p["name"] for p in data["periods"]]
    period = st.selectbox("期間", period_names)

    task_name = st.text_input("タスク名")
    amount = st.number_input("量（任意）", min_value=0, step=1)

    if st.button("登録"):
        data["tasks"].append({
            "name": task_name,
            "total": amount if amount > 0 else None,
            "period": period
        })
        save_data(data)
        st.success("タスクを登録しました")

# --------------------
# 完了入力
# --------------------
elif menu == "完了入力":
    st.header("✅ 完了入力")

    task_names = [t["name"] for t in data["tasks"]]
    task = st.selectbox("タスク", task_names)

    task_info = next(t for t in data["tasks"] if t["name"] == task)

    if task_info["total"] is None:
        amount = st.number_input("進捗（％）", min_value=0, max_value=100)
    else:
        amount = st.number_input("完了量", min_value=0)

    if st.button("登録"):
        data["logs"].append({
            "task": task,
            "amount": amount,
            "date": str(date.today())
        })
        save_data(data)
        st.success("完了を記録しました")

# --------------------
# カレンダー
# --------------------
elif menu == "カレンダー":
    st.header("🗓 カレンダー")

    uploaded = st.file_uploader("iCalファイル(.ics)を読み込む", type="ics")

    if uploaded:
        cal = Calendar.from_ical(uploaded.read())
        for event in cal.walk("VEVENT"):
            data["events"].append({
                "summary": str(event.get("summary")),
                "start": str(event.get("dtstart").dt)
            })
        save_data(data)
        st.success("iCalを読み込みました")

    if len(data["events"]) == 0:
        st.info("イベントがありません")
    else:
        df = pd.DataFrame(data["events"])
        st.dataframe(df)
