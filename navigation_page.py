import streamlit as st
import urllib.parse
import requests
from streamlit_javascript import st_javascript

def navigation_page(activity):
    st.header("🗺️ 会场导航")
    
    if not activity:
        st.warning("请先在「用户查询」页面查询活动，再使用导航功能。")
        return

    name = activity.get("name", "会场")
    address = activity.get("address", "")
    AMAP_KEY = st.secrets["AMAP_KEY"]

    st.info(f"📌 目的地：{name}  |  {address}")

    # 获取用户当前位置（浏览器JS定位）
    coords = st_javascript("""
    (async () => {
        if (navigator.geolocation) {
            return new Promise((resolve, reject) => {
                navigator.geolocation.getCurrentPosition(
                    pos => resolve({lat: pos.coords.latitude, lng: pos.coords.longitude}),
                    err => resolve(null)
                );
            });
        } else {
            return null;
        }
    })()
    """)

    # 地址转坐标（只算一次）
    geo_url = "https://restapi.amap.com/v3/geocode/geo"
    geo_resp = requests.get(geo_url, params={"address": address, "key": AMAP_KEY})
    geo_data = geo_resp.json()

    location = None
    if geo_data.get("status") == "1" and geo_data["geocodes"]:
        location = geo_data["geocodes"][0]["location"]
        dest_lng, dest_lat = location.split(",")

        # 显示静态地图
        static_map_url = (
            f"https://restapi.amap.com/v3/staticmap"
            f"?location={location}&zoom=15&size=750*400"
            f"&markers=mid,,A:{location}"
            f"&key={AMAP_KEY}"
        )
        st.image(static_map_url, caption=f"📍 {name}", use_container_width=True)
    else:
        st.warning("地址解析失败，无法显示地图，但仍可点击下方链接导航")

    # 导航跳转链接
    nav_mode = st.radio("出行方式", ["🚗 驾车", "🚇 公交", "🚶 步行"], horizontal=True)
    mode_map = {"🚗 驾车": "driving", "🚇 公交": "transit", "🚶 步行": "walking"}
    mode = mode_map[nav_mode]

    # 构建终点
    if location:
        to_part = f"{dest_lng},{dest_lat},{urllib.parse.quote(name)}"
    else:
        to_part = f"{urllib.parse.quote(address)},{urllib.parse.quote(name)}"

    # 构建起点（用户定位）
    if coords and isinstance(coords, dict) and "lat" in coords and "lng" in coords:
        from_part = f"{coords['lng']},{coords['lat']},{urllib.parse.quote('我的位置')}"
        amap_url = f"https://uri.amap.com/navigation?from={from_part}&to={to_part}&mode={mode}&callnative=1"
    else:
        amap_url = f"https://uri.amap.com/navigation?to={to_part}&mode={mode}&callnative=1"

    st.markdown(f"### [📍 点击前往高德地图导航]({amap_url})")
    st.caption("手机端自动唤起高德地图App，电脑端在浏览器中打开。若定位失败，请刷新页面允许浏览器定位。")
