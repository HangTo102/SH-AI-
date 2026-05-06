# 基于 .streamlit 的 web_UI 开发
from core_layer.retriever import retrieve_activity_candidates, select_activity
from core_layer.extractor import extract_blocks
from core_layer.responder import render_response
from core_layer.loader import load_all_activities
from core_layer.commit import upload_activity_page
import streamlit as st
from config import USE_AI  # 保持原导入
from prompt_layer.ai_client import ai_generate_answer  # 确保导入 AI 函数
from prompt_layer.utils import show_error  # 导入错误显示函数
from core_layer.navigation_page import navigation_page # 地图导航系统函数


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
    ["用户查询", "主办方上传", "地图导航"]
)

# 地图导航函数调用
if mode == "地图导航":
    navigation_page(st.session_state.get("current_activity"))
    st.stop()
    
# 主办方上传页面函数
if mode == "主办方上传":
    upload_activity_page()
    # 上传成功后清空缓存，让问答页重新加载新文件
    if "activities" in st.session_state:
        del st.session_state["activities"]
    st.stop()
    
st.title("🎫 活动信息智能助手")
st.caption("支持查询活动时间、地点、票务、参展信息、导航方式等")

# 当前活动提示（下方也有提示信息）
if st.session_state.get("current_activity"):
    st.info(f"📌 当前活动：{st.session_state.current_activity.get('name')}")
    
# Session State
if "activities" not in st.session_state:
    st.session_state.activities = load_all_activities()

if "current_activity" not in st.session_state:
    st.session_state.current_activity = None

if "chat_history" not in st.session_state:
    st.session_state.chat_history = []

# 输入框
question = st.text_input(
    "请输入你的问题，例如：夏日音乐节在哪里？",
    placeholder="例如：怎么去现场？有哪些参展公司？"
)

ask = st.button("提问")

# 主逻辑（修改版：展示多个候选活动让用户选择）
if ask and question.strip():

    activities = st.session_state.activities
    current_activity = st.session_state.current_activity

    # ① 如果当前没有活动，先检索活动
    if current_activity is None:
        candidates = retrieve_activity_candidates(activities, question)
        
        if len(candidates) == 0:
            answer = "没有找到相关活动 😊"
            st.session_state.chat_history.append(
                {"question": question, "answer": answer}
            )
        elif len(candidates) == 1:
            # 只有一个候选，直接选
            current_activity = candidates[0]["activity"]
            st.session_state.current_activity = current_activity
            # 继续处理这个活动
        else:
            # 多个候选，展示给用户选择（取前3个）
            st.info("🔍 找到多个相似的活动，请选择一个：")
            top_candidates = candidates[:3]
            
            # 显示候选活动信息
            col1, col2 = st.columns([3, 1])
            with col1:
                st.write("**候选活动列表：**")
            with col2:
                st.write("")
            
            for i, cand in enumerate(top_candidates, 1):
                activity = cand["activity"]
                score = cand["score"]
                matched = cand.get("matched", [])
                st.write(f"{i}. **{activity.get('name')}** (匹配度: {score}) - 匹配项: {', '.join(matched)}")
            
            # 用户选择
            selected_idx = st.radio(
                "选择活动：", 
                [f"{i}. {c['activity'].get('name')} (匹配度: {c['score']})" 
                 for i, c in enumerate(top_candidates, 1)],
                key=f"activity_select_{question}"
            )
            
            if selected_idx:
                idx = int(selected_idx[0]) - 1
                current_activity = top_candidates[idx]["activity"]
                st.session_state.current_activity = current_activity
                st.success(f"✅ 已选择活动：{current_activity.get('name')}")
                # 继续处理这个活动

    # ② 已经有活动 → 抽取 + 回答（添加 AI 判断和调用）
    if current_activity:
        extracted = extract_blocks(current_activity, question)

        if extracted:
            if USE_AI:
                st.info("已进入 AI 润色分支，正在调用 DashScope...")
                try:
                    text = ai_generate_answer(extracted, question)
                except Exception as e:
                    error_msg = show_error(f"AI 调用异常：{str(e)}", e)
                    text = render_response(extracted)  # fallback 原文
                    st.warning("AI 调用失败，已 fallback 到原文")
            else:
                text = render_response(extracted)
        else:
            st.warning("暂无相关信息")
            text = "暂无相关信息"

        answer = text  # 最终输出

        # ③ 记录对话
        st.session_state.chat_history.append(
            {"question": question, "answer": answer}
        )

# 对话展示
for item in reversed(st.session_state.chat_history):
    st.markdown(f"**你：** {item['question']}")
    st.markdown(f"**助手：** {item['answer']}")
    st.markdown("---")

# 当前活动提示
if st.session_state.current_activity:
    st.info(f"📌 当前活动：{st.session_state.current_activity.get('name')}")
