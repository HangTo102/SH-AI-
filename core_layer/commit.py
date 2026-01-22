import json
import os
import streamlit as st

UPLOAD_DIR = "data"

def upload_activity_page():
    st.header("📤 主办方活动信息上传")

    uploaded_file = st.file_uploader(
        "请上传活动信息 JSON 文件",
        type=["json"]
    )

    if uploaded_file:
        try:
            data = json.load(uploaded_file)

            # 最小校验
            required_fields = ["name", "date", "location", "address"]
            missing = [f for f in required_fields if f not in data]

            if missing:
                st.error(f"缺少必要字段：{missing}")
                return

            # 保存文件
            os.makedirs(UPLOAD_DIR, exist_ok=True)
            safe_name = data["name"].replace(" ", "_")
            filename = f"{safe_name}.json"
            path = os.path.join(UPLOAD_DIR, filename)

            with open(path, "w", encoding="utf-8") as f:
                json.dump(data, f, ensure_ascii=False, indent=2)

            st.success("活动信息上传成功！")

        except Exception as e:
            st.error(f"上传失败：{e}")
