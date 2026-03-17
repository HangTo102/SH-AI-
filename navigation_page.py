import streamlit as st
import streamlit.components.v1 as components

def navigation_page(activity):
    st.header("🗺️ 会场导航")

    AMAP_KEY = st.secrets["AMAP_KEY"]

    if not activity:
        st.warning("请先在「用户查询」页面查询活动，再使用导航功能。")
        return

    name = activity.get("name", "会场")
    address = activity.get("address", "")
    # 从活动信息里取坐标，没有就用地址搜索
    lng = activity.get("longitude", "")
    lat = activity.get("latitude", "")

    st.info(f"📌 目的地：{name}  |  {address}")

    # 导航模式选择
    nav_mode = st.radio(
        "出行方式",
        ["🚗 驾车", "🚇 公交", "🚶 步行"],
        horizontal=True
    )
    mode_map = {"🚗 驾车": "driving", "🚇 公交": "transit", "🚶 步行": "walking"}
    mode = mode_map[nav_mode]

    # 高德地图 HTML 嵌入
    html_code = f"""
    <!DOCTYPE html>
    <html>
    <head>
        <meta charset="utf-8">
        <style>
            body {{ margin: 0; }}
            #container {{ width: 100%; height: 550px; }}
            #info {{ padding: 8px; background: #fff; font-size: 14px; }}
        </style>
        <script src="https://webapi.amap.com/maps?v=2.0&key={{AMAP_KEY}}&plugin=AMap.Driving,AMap.Walking,AMap.Transfer,AMap.Geolocation"></script>
    </head>
    <body>
        <div id="info">正在获取当前位置...</div>
        <div id="container"></div>
        <script>
            var map = new AMap.Map('container', {{
                zoom: 15,
                resizeEnable: true
            }});

            // 目的地
            var destination = {{"keyword": "{address}", "lng": "{lng}", "lat": "{lat}"}};

            // 获取用户当前位置
            var geolocation = new AMap.Geolocation({{
                enableHighAccuracy: true,
                timeout: 10000,
            }});

            geolocation.getCurrentPosition(function(status, result) {{
                if (status === 'complete') {{
                    var origin = [result.position.lng, result.position.lat];
                    document.getElementById('info').innerText = '📍 已获取当前位置，正在规划路线...';

                    // 根据出行方式规划路线
                    var mode = "{mode}";
                    if (mode === "driving") {{
                        AMap.plugin('AMap.Driving', function() {{
                            var driving = new AMap.Driving({{ map: map }});
                            driving.search(origin, "{address}", function(status, result) {{
                                if (status === 'complete') {{
                                    document.getElementById('info').innerText = '🚗 驾车路线规划完成';
                                }}
                            }});
                        }});
                    }} else if (mode === "walking") {{
                        AMap.plugin('AMap.Walking', function() {{
                            var walking = new AMap.Walking({{ map: map }});
                            walking.search(origin, "{address}", function(status, result) {{
                                if (status === 'complete') {{
                                    document.getElementById('info').innerText = '🚶 步行路线规划完成';
                                }}
                            }});
                        }});
                    }} else {{
                        AMap.plugin('AMap.Transfer', function() {{
                            var transfer = new AMap.Transfer({{ map: map, city: "全国" }});
                            transfer.search(origin, "{address}", function(status, result) {{
                                if (status === 'complete') {{
                                    document.getElementById('info').innerText = '🚇 公交路线规划完成';
                                }}
                            }});
                        }});
                    }}
                }} else {{
                    document.getElementById('info').innerText = '⚠️ 无法获取位置，请手动在地图上查看目的地';
                    // 定位失败就直接显示目的地
                    map.setCenter(["{lng}" || 116.397428, "{lat}" || 39.90923]);
                    new AMap.Marker({{
                        position: map.getCenter(),
                        title: "{name}"
                    }}).setMap(map);
                }}
            }});
        </script>
    </body>
    </html>
    """
    components.html(html_code, height=600)