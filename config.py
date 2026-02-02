import os

# USE_AI = os.getenv("USE_AI", "false").lower() == "true"      # 仅适用于本地环境变量

USE_AI = st.secrets.get("USE_AI", "false").lower() == "true"     # 适用于 streamlit 平台使用
