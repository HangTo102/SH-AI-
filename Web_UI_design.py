# 基于 .streamlit 的 web_UI 开发
from core_layer.retriever import retrieve_activity_candidates, select_activity
from core_layer.extractor import extract_blocks
from core_layer.responder import render_response
from core_layer.loader import load_all_activities
import streamlit as st
from config import USE_AI  # 保持原导入
from prompt_layer.ai_client import ai_generate_answer  # 确保导入 AI 函数
from prompt_layer.utils import show_error  # 导入错误显示函数


# 初始化
st.set_page_config(
    page_title="活动信息智能助手",
    page_icon="🎫",
    layout="centered"
)

# 侧边栏设计
st.sidebar.title("管理入口")
mode = st.sidebar.selectbox(
    "选择功能",
    ["用户查询", "主办方上传"]
)

st.title("🎫 活动信息智能助手")
st.caption("支持查询活动时间、地点、票务、参展信息、导航方式等")

# Session State
if "activities" not in st.session_state:
    st.session_state.activities = load_all_activities()

if "current_activity" not in st.session_state:
    st.session_state.current_activity = None

if "chat_history" not in st.session_state:
    st.session_state.chat_history = []

# 输入框
question = st.text_input(
    "请输入你的问题，例如：国际创新博览会在哪里？",
    placeholder="例如：怎么去现场？有哪些参展公司？"
)

ask = st.button("提问")

# 主逻辑（这里是关键改动：添加 AI 润色逻辑，与 main.py 同步）
if ask and question.strip():

    activities = st.session_state.activities
    current_activity = st.session_state.current_activity

    # st.info("调试：开始处理问题...")  # 加调试：确认进入主逻辑

    # ① 如果当前没有活动，先检索活动（保持原样）
    if current_activity is None:
        st.write("调试：当前无活动，正在检索 candidates...")
        candidates = retrieve_activity_candidates(activities, question)
        selected = select_activity(candidates, len(activities))

        if selected is None:
            answer = "我找到了多个可能的活动，请你说得更具体一点 😊"
        else:
            current_activity = selected
            st.session_state.current_activity = selected
            # st.write("调试：检索到活动：" + selected.get('name', '未知'))  # 加调试

    # ② 已经有活动 → 抽取 + 回答（改动点：添加 AI 判断和调用）
    if current_activity:
        # st.write("调试：当前活动存在，正在提取 blocks...")
        extracted = extract_blocks(current_activity, question)
        st.write("调试：extracted 是否有内容？", bool(extracted))  # 加调试

        if extracted:
            st.write("调试：USE_AI 值（进入分支前）：", USE_AI)  # 加调试

            if USE_AI:
                st.info("已进入 AI 润色分支，正在调用 DashScope...")  # 加调试 + 用户提示
                try:
                    text = ai_generate_answer(extracted, question)  # 调用 AI 函数
                    # st.success("调试：AI 调用成功，返回内容长度：" + str(len(text)))  # 加调试
                except Exception as e:
                    error_msg = show_error(f"AI 调用异常：{str(e)}", e)  # 用兼容函数显示错误
                    text = render_response(extracted)  # fallback 原文
                    st.warning("调试：AI 调用失败，已 fallback 到原文")
            else:
                st.warning("USE_AI 为 False，跳过 AI，直接用 render_response")  # 加调试
                text = render_response(extracted)
        else:
            st.warning("extracted 为空，没有可用的块信息")  # 加调试
            text = "暂无相关信息"

        answer = text  # 最终输出

    # ③ 记录对话（保持原样）
    st.session_state.chat_history.append(
        {"question": question, "answer": answer}
    )

# =========================
# 对话展示（保持原样）
# =========================
for item in st.session_state.chat_history:
    st.markdown(f"**你：** {item['question']}")
    st.markdown(f"**助手：** {item['answer']}")
    st.markdown("---")

# =========================
# 当前活动提示（保持原样）
# =========================
if st.session_state.current_activity:
    st.info(f"📌 当前活动：{st.session_state.current_activity.get('name')}")

