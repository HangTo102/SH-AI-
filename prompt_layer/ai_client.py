import os
from dashscope import Generation
import streamlit as st
import traceback  # 新增，用于打印详细 traceback

MODEL_NAME = "qwen-plus"


def ai_generate_answer(known_info: dict, question: str) -> str:
    """
    使用大模型基于「已知信息」生成自然语言回答
    """
    api_key = st.secrets.get("DASHSCOPE_API_KEY", None)
    if not api_key:
        st.error("❌ 无法读取 DASHSCOPE_API_KEY，请检查 Streamlit Cloud 的 Secrets 设置")
        st.write("当前 st.secrets 内容（调试）：", dict(st.secrets))
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
        st.info("正在调用 DashScope API...")  # 可选：给用户一个等待提示

        response = Generation.call(
            model=MODEL_NAME,
            prompt=prompt,
            temperature=0.3,
            max_tokens=500,
            api_key=api_key,  # 显式传 api_key（虽然 SDK 可能内部读环境变量，但这里保险）
        )

        # 检查 response 是否正常（DashScope 有时返回 status_code != 200 但不抛异常）
        if hasattr(response, 'status_code') and response.status_code != 200:
            error_msg = f"DashScope 返回非 200 状态码: {response.status_code}\n响应内容: {response}"
            st.error(error_msg)
            return f"⚠️ AI 服务返回异常 - {error_msg}"

        # 正常返回
        if hasattr(response, 'output') and hasattr(response.output, 'text'):
            content = response.output.text.strip()
            return "【AI生成】\n" + content
        else:
            st.warning("API 返回格式异常，没有 output.text")
            return "⚠️ AI 返回格式异常"

    except Exception as e:
        # 显示到页面（最关键！）
        st.error(f"DashScope API 调用失败：{str(e)}")
        st.caption(f"异常类型：{type(e).__name__}")

        # 额外输出详细 traceback（方便你调试）
        st.code(traceback.format_exc(), language="python")

        # 可选：根据常见错误给出提示
        error_str = str(e).lower()
        if "timeout" in error_str or "connection" in error_str:
            st.warning(
                "提示：可能是网络超时或 Streamlit Cloud（美国服务器）无法连接阿里云 DashScope API（中国境内）。建议检查 IP 限制或加代理。")
        elif "forbidden" in error_str or "403" in error_str or "ip" in error_str:
            st.warning("提示：403 Forbidden 或 IP 相关错误。阿里云 DashScope 可能限制了海外 IP 访问。")

        return f"⚠️ AI 服务暂时不可用（{str(e)}）"
