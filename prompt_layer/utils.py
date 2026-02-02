import streamlit as st
import sys

def show_error(msg: str, exc=None):
    """兼容终端和 Streamlit 的错误显示"""
    if 'streamlit' in sys.modules and hasattr(st, 'error'):
        # 在 Streamlit 环境中
        st.error(msg)
        if exc:
            st.caption(f"异常类型: {type(exc).__name__}")
            # st.code(traceback.format_exc())  # 如果想显示完整堆栈，可打开
    else:
        # 终端环境
        print(f"【错误】 {msg}")
        if exc:
            print(f"异常类型: {type(exc).__name__}")
            import traceback
            print(traceback.format_exc())

    # 无论哪种环境，都把错误信息加到返回文本里
    return f"⚠️ {msg}"