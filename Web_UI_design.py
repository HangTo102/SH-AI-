# 基于 streamlit 的 web_UI 开发
import streamlit as st

from core_layer.retriever import (retrieve_activity_candidates,select_activity)
from core_layer.extractor import extract_blocks
from core_layer.responder import render_response
from core_layer.loader import load_all_activities


# =========================
# 初始化
# =========================
st.set_page_config(
    page_title="活动信息智能助手",
    page_icon="🎫",
    layout="centered"
)

st.title("🎫 活动信息智能助手")
st.caption("支持查询活动时间、地点、票务、参展信息、导航方式等")


# =========================
# Session State
# =========================
if "activities" not in st.session_state:
    st.session_state.activities = load_all_activities()

if "current_activity" not in st.session_state:
    st.session_state.current_activity = None

if "chat_history" not in st.session_state:
    st.session_state.chat_history = []


# =========================
# 输入框
# =========================
question = st.text_input(
    "请输入你的问题，例如：国际创新博览会在哪里？",
    placeholder="例如：怎么去现场？有哪些参展公司？"
)

ask = st.button("提问")


# =========================
# 主逻辑
# =========================
if ask and question.strip():

    activities = st.session_state.activities
    current_activity = st.session_state.current_activity

    # ① 如果当前没有活动，先检索活动
    if current_activity is None:
        candidates = retrieve_activity_candidates(activities, question)
        selected = select_activity(candidates, len(activities))

        if selected is None:
            answer = "我找到了多个可能的活动，请你说得更具体一点 😊"
        else:
            current_activity = selected
            st.session_state.current_activity = selected

    # ② 已经有活动 → 抽取 + 回答
    if current_activity:
        extracted = extract_blocks(current_activity, question)
        answer = render_response(extracted)

    # ③ 记录对话
    st.session_state.chat_history.append(
        {"question": question, "answer": answer}
    )


# =========================
# 对话展示
# =========================
for item in st.session_state.chat_history:
    st.markdown(f"**你：** {item['question']}")
    st.markdown(f"**助手：** {item['answer']}")
    st.markdown("---")


# =========================
# 当前活动提示
# =========================
if st.session_state.current_activity:
    st.info(f"📌 当前活动：{st.session_state.current_activity.get('name')}")
