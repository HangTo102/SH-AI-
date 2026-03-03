import json
import os
import base64
import requests
import streamlit as st

UPLOAD_DIR = "data"
GITHUB_TOKEN = st.secrets["GITHUB_TOKEN"]
GITHUB_REPO = "HangTo102/SH-AI-"
GITHUB_BRANCH = "main"

def upload_activity_page():
    st.header("📤 主办方活动信息上传")

    # 新增：格式说明
    st.markdown("### 📋 JSON 文件格式要求")
    st.markdown("请严格按照以下模板格式上传，字段名称不可更改：")
    st.code("""
{
  "name": "活动名称",
  "date": "2025-08-01",
  "location": "场馆名称",
  "address": "详细地址",
  "description": "活动简介",
  "tickets": [
    {"type": "普通票", "price": 100, "remaining": 200}
  ],
  "exhibitors": [
    {"name": "参展商名称", "booth": "展位号", "category": "类别"}
  ],
  "navigation": {
    "subway": "地铁乘坐方式",
    "bus": "公交乘坐方式",
    "parking": "停车信息"
  },
  "contact": {
    "phone": "联系电话",
    "email": "联系邮箱"
  }
}
    """, language="json")
    st.warning("⚠️ name、date、location、address 为必填字段，其余为选填")

    # 新增：查看和下载现有活动
    st.markdown("### 📂 查看/修改已有活动信息")
    GITHUB_TOKEN = st.secrets["GITHUB_TOKEN"]
    headers = {"Authorization": f"token {GITHUB_TOKEN}"}

    # 获取data目录下所有json文件列表
    list_url = f"https://api.github.com/repos/{GITHUB_REPO}/contents/data"
    list_resp = requests.get(list_url, headers=headers, params={"ref": GITHUB_BRANCH})

    if list_resp.status_code == 200:
        files = [f for f in list_resp.json() if f["name"].endswith(".json")]
        if files:
            file_names = [f["name"] for f in files]
            selected = st.selectbox("选择要修改的活动文件", ["（不修改，直接上传新活动）"] + file_names)
        
            if selected != "（不修改，直接上传新活动）":
                # 获取对应文件内容
                file_info = next(f for f in files if f["name"] == selected)
                file_resp = requests.get(file_info["download_url"])
                file_content = file_resp.text
            
                # 提供下载按钮
                st.download_button(
                    label=f"⬇️ 下载 {selected}",
                    data=file_content,
                    file_name=selected,
                    mime="application/json"
                )
                st.info("请下载文件修改后，在下方重新上传，系统会自动覆盖原文件。")
        else:
            st.caption("暂无已上传的活动信息")
    else:
        st.caption("暂时无法获取活动列表")

    st.markdown("---")
    st.markdown("### 📤 上传新活动 / 覆盖已有活动")

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

            # 写入GitHub仓库
            safe_name = data["name"].replace(" ", "_")
            filename = f"{safe_name}.json"
            file_path = f"data/{filename}"
            content = json.dumps(data, ensure_ascii=False, indent=2)
            content_b64 = base64.b64encode(content.encode("utf-8")).decode("utf-8")

            GITHUB_TOKEN = st.secrets["GITHUB_TOKEN"]
            api_url = f"https://api.github.com/repos/{GITHUB_REPO}/contents/{file_path}"
            headers = {"Authorization": f"token {GITHUB_TOKEN}"}
            
            # 检查文件是否已存在（更新时需要sha）
            check = requests.get(api_url, headers=headers)
            check_data = check.json()
            # 确保拿到的是字符串类型的sha，避免拿到错误数据
            sha = check_data.get("sha") if check.status_code == 200 and isinstance(check_data, dict) else None

            payload = {
                "message": f"上传活动信息：{data['name']}",
                "content": content_b64,
                "branch": GITHUB_BRANCH,
            }
            if sha:
                payload["sha"] = sha

            response = requests.put(api_url, headers=headers, json=payload)

            if response.status_code in [200, 201]:
                st.success("活动信息上传成功！")  # 保持原样
                if "activities" in st.session_state:
                    del st.session_state["activities"]
            else:
                st.error(f"上传失败：{response.json().get('message')}")

            
            # 写入本地数据库中，运行负担比较大
            # with open(path, "w", encoding="utf-8") as f:
            #     json.dump(data, f, ensure_ascii=False, indent=2)

            
            # st.success("活动信息上传成功！")

        except Exception as e:
            st.error(f"上传失败：{e}")





