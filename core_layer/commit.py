import json
import os
import streamlit as st

UPLOAD_DIR = "data"
GITHUB_TOKEN = st.secrets["GITHUB_TOKEN"]
GITHUB_REPO = "HangTo102/SH-AI-"
GITHUB_BRANCH = "main"

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

            # 保存文件至本地数据库
            # os.makedirs(UPLOAD_DIR, exist_ok=True)
            # safe_name = data["name"].replace(" ", "_")
            # filename = f"{safe_name}.json"
            # path = os.path.join(UPLOAD_DIR, filename)

            # 保存文件
            safe_name = data["name"].replace(" ", "_")
            filename = f"{safe_name}.json"
            file_path = f"data/{filename}"
            content = json.dumps(data, ensure_ascii=False, indent=2)
            content_b64 = base64.b64encode(content.encode("utf-8")).decode("utf-8")
            
            # 检查文件是否已存在（更新需要sha）
            api_url = f"https://api.github.com/repos/{GITHUB_REPO}/contents/{file_path}"
            headers = {"Authorization": f"token {GITHUB_TOKEN}"}
            check = requests.get(api_url, headers=headers)
            sha = check.json().get("sha") if check.status_code == 200 else None

            payload = {
                "message": f"上传活动信息：{data['name']}",
                "content": content_b64,
                "branch": GITHUB_BRANCH,
            }
            if sha:
                payload["sha"] = sha  # 更新已有文件必须带sha

            response = requests.put(api_url, headers=headers, json=payload)

            if response.status_code in [200, 201]:
                st.success("✅ 活动信息上传成功！Streamlit 将在约1分钟内自动更新。")
                if "activities" in st.session_state:
                    del st.session_state["activities"]
            else:
                st.error(f"上传失败：{response.json().get('message')}")

            
            # 写入本地数据库中，运行负担比较大
            # with open(path, "w", encoding="utf-8") as f:
            #     json.dump(data, f, ensure_ascii=False, indent=2)

            
            st.success("活动信息上传成功！")

        except Exception as e:
            st.error(f"上传失败：{e}")

