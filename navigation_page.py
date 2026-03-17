import streamlit as st
import urllib.parse
import requests

def navigation_page(activity):
    st.header("🗺️ 会场导航")

    if not activity:
        st.warning("请先在「用户查询」页面查询活动，再使用导航功能。")
        return

    name = activity.get("name", "会场")
    address = activity.get("address", "")
    AMAP_KEY = st.secrets["AMAP_KEY"]

    st.info(f"📌 目的地：{name}  |  {address}")

    # 第一步：用高德API把地址转成坐标
    geo_url = "https://restapi.amap.com/v3/geocode/geo"
    geo_resp = requests.get(geo_url, params={
        "address": address,
        "key": AMAP_KEY
    })
    geo_data = geo_resp.json()

    if geo_data.get("status") == "1" and geo_data["geocodes"]:
        location = geo_data["geocodes"][0]["location"]  # 格式是 "lng,lat"
        lng, lat = location.split(",")

        # 第二步：显示静态地图（内嵌图片）
        static_map_url = (
            f"https://restapi.amap.com/v3/staticmap"
            f"?location={location}&zoom=15&size=750*400"
            f"&markers=mid,,A:{location}"
            f"&key={AMAP_KEY}"
        )
        st.image(static_map_url, caption=f"📍 {name}", use_container_width=True)

    else:
        st.warning("地址解析失败，无法显示地图，但仍可点击下方链接导航")
        lng, lat = "", ""

    # 第三步：导航跳转链接
    nav_mode = st.radio("出行方式", ["🚗 驾车", "🚇 公交", "🚶 步行"], horizontal=True)
    mode_map = {"🚗 驾车": "driving", "🚇 公交": "transit", "🚶 步行": "walking"}
    mode = mode_map[nav_mode]

    encoded_address = urllib.parse.quote(address)
    encoded_name = urllib.parse.quote(name)
    amap_url = f"https://uri.amap.com/navigation?to={encoded_address},{encoded_name}&mode={mode}&callnative=1"

    st.markdown(f"### [📍 点击前往高德地图导航]({amap_url})")
    st.caption("手机端自动唤起高德地图App，电脑端在浏览器中打开")
