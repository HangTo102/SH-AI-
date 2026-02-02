import os
from dashscope import Generation
import streamlit as st

MODEL_NAME = "qwen-plus"


def ai_generate_answer(known_info: dict, question: str) -> str:
    """
    使用大模型基于「已知信息」生成自然语言回答
    """
    # api_key = os.getenv("DASHSCOPE_API_KEY")   # 该关键词只适用于本地部署运行
    api_key = st.secrets.get("DASHSCOPE_API_KEY", None)    # 该关键词用于 streamlit 平台
    if not api_key:
        st.error("❌ 无法读取 keys，请检查 Streamlit Cloud 的 Secrets 设置")
        st.write("当前 st.secrets 内容（调试）：", dict(st.secrets))  # 临时看全部 secrets
        return "⚠️ AI 服务未配置（缺少 API Key）"

    prompt = f"""
你是一个活动信息智能助手。
你只能基于【已知信息】回答问题，不能编造不存在的内容。
请根据用户问题将【已知信息】用更自然、更口语化的语气回答。

【已知信息】
{known_info}

【用户问题】
{question}

如果已知信息中没有答案，请明确说明“暂无相关信息”。
"""

    try:
        response = Generation.call(
            model=MODEL_NAME,
            prompt=prompt,
            temperature=0.3,
            max_tokens=500
        )

        return response.output.text.strip()

    except Exception as e:
        # 非常重要：AI 挂了，系统不能挂
        return f"⚠️ AI 服务暂时不可用（{str(e)}）"



