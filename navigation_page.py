import streamlit as st
import requests
from streamlit_javascript import st_javascript

def get_route(origin_lng, origin_lat, dest_lng, dest_lat, mode, key):
    origin = f"{origin_lng},{origin_lat}"
    destination = f"{dest_lng},{dest_lat}"
    if mode == "driving":
        url = "https://restapi.amap.com/v3/direction/driving"
        params = {"origin": origin, "destination": destination, "key": key}
    elif mode == "walking":
        url = "https://restapi.amap.com/v3/direction/walking"
        params = {"origin": origin, "destination": destination, "key": key}
    else:
        url = "https://restapi.amap.com/v3/direction/transit/integrated"
        params = {"origin": origin, "destination": destination, "key": key, "city": "全国"}
    return requests.get(url, params=params).json()

def parse_route(route_data, mode):
    steps, duration, distance = [], 0, 0
    try:
        if mode in ["driving", "walking"]:
            path = route_data["route"]["paths"][0]
            duration = int(path["duration"]) // 60
            distance = float(path["distance"]) / 1000
            for step in path["steps"]:
                steps.append(step["instruction"])
        else:
            transit = route_data["route"]["transits"][0]
            duration = int(transit["duration"]) // 60
            distance = float(transit["distance"]) / 1000
            for segment in transit["segments"]:
                if "bus" in segment:
                    for busline in segment["bus"]["buslines"]:
                        steps.append(f"乘坐 {busline['name']}，从【{busline['departure_stop']['name']}】到【{busline['arrival_stop']['name']}】")
                elif "walking" in segment:
                    for s in segment["walking"].get("steps", []):
                        steps.append(s["instruction"])
    except:
        steps = ["路线规划失败，请检查地址是否正确"]
    return steps, duration, distance

def navigation_page(activity):
    st.header("🗺️ 会场导航")

    if not activity:
        st.warning("请先在「用户查询」页面查询活动，再使用导航功能。")
        return

    name = activity.get("name", "会场")
    address = activity.get("address", "")
    AMAP_KEY = st.secrets["AMAP_KEY"]

    st.info(f"📌 目的地：{name}  |  {address}")

    # 获取用户位置
    st.markdown("### 📍 您的当前位置")
    location_method = st.radio(
        "定位方式",
        ["📱 自动定位（允许浏览器权限）", "✏️ 手动输入地址"],
        horizontal=True
    )

    user_lng, user_lat = None, None

    if location_method == "📱 自动定位（允许浏览器权限）":
        coords = st_javascript("""
        (async () => {
            if (navigator.geolocation) {
                return new Promise((resolve) => {
                    navigator.geolocation.getCurrentPosition(
                        pos => resolve({lat: pos.coords.latitude, lng: pos.coords.longitude}),
                        err => resolve(null),
                        {timeout: 10000, enableHighAccuracy: true}
                    );
                });
            }
            return null;
        })()
        """)
        if coords and isinstance(coords, dict) and "lat" in coords:
            user_lng = coords["lng"]
            user_lat = coords["lat"]
            st.success(f"✅ 定位成功：{user_lat:.4f}, {user_lng:.4f}")
        else:
            st.warning("自动定位失败，请切换为手动输入地址")

    else:
        user_address = st.text_input("请输入您的出发地址", placeholder="例如：上海市人民广场")
        if user_address:
            user_geo = requests.get("https://restapi.amap.com/v3/geocode/geo", params={
                "address": user_address, "key": AMAP_KEY
            }).json()
            if user_geo.get("status") == "1" and user_geo.get("geocodes"):
                user_location = user_geo["geocodes"][0]["location"]
                user_lng, user_lat = user_location.split(",")
                st.success(f"✅ 出发地已确认：{user_address}")
            else:
                st.error("地址解析失败，请重新输入")

    # 目的地地址转坐标
    geo_resp = requests.get("https://restapi.amap.com/v3/geocode/geo", params={
        "address": address, "key": AMAP_KEY
    }).json()

    if not (geo_resp.get("status") == "1" and geo_resp.get("geocodes")):
        st.error("目的地地址解析失败，请检查活动信息中的地址是否正确。")
        return

    location = geo_resp["geocodes"][0]["location"]
    dest_lng, dest_lat = location.split(",")

    # 显示目的地静态地图
    static_map_url = (
        f"https://restapi.amap.com/v3/staticmap"
        f"?location={location}&zoom=15&size=750*300"
        f"&markers=mid,,A:{location}"
        f"&key={AMAP_KEY}"
    )
    st.image(static_map_url, caption=f"📍 {name}", use_container_width=True)

    # 出行方式选择
    nav_mode = st.radio("出行方式", ["🚗 驾车", "🚇 公交", "🚶 步行"], horizontal=True)
    mode_map = {"🚗 驾车": "driving", "🚇 公交": "transit", "🚶 步行": "walking"}
    mode = mode_map[nav_mode]

    if st.button("📍 规划路线"):
        if user_lng and user_lat:
            user_lng = coords["lng"]
            user_lat = coords["lat"]

            with st.spinner("正在规划路线..."):
                route_data = get_route(user_lng, user_lat, dest_lng, dest_lat, mode, AMAP_KEY)
                steps, duration, distance = parse_route(route_data, mode)

            st.success(f"🕐 预计用时：{duration} 分钟  |  📏 距离：{distance:.1f} 公里")

            # 显示含路线的静态地图
            route_map_url = (
                f"https://restapi.amap.com/v3/staticmap"
                f"?size=750*400"
                f"&markers=mid,,起:{user_lng},{user_lat}|mid,,终:{location}"
                f"&key={AMAP_KEY}"
            )
            st.image(route_map_url, caption="路线图", use_container_width=True)

            # 逐步导航指引
            st.markdown("### 📋 导航步骤")
            for i, step in enumerate(steps, 1):
                st.markdown(f"**{i}.** {step}")
        else:
            st.warning("请先确认您的出发位置")
