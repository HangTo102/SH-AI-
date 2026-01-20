def render_block(semantic: str, block: dict) -> list[str]:
    t = block["type"]
    v = block["value"]

    lines = []

    if t == "string":
        lines.append(f"{v}")

    elif t == "object":
        lines.append("📌 相关信息：")
        for _, value in v.items():
            lines.append(f"  - {value}")

    elif t == "list":
        lines.append("📋 相关安排：")
        for item in v:
            parts = [str(x) for x in item.values()]
            lines.append("  - " + " | ".join(parts))
    elif t == "navigation":
        address = v
        lines.append(f"📍 活动地址：{address}")
        lines.append("🧭 导航提示：")
        lines.append("  - 可在高德 / 百度 / Google 地图中搜索上述地址进行导航")

    return lines


def render_response(extracted: dict) -> str:
    lines = []

    for semantic, block in extracted.items():
        if "type" not in block or "value" not in block:
            raise ValueError(
                f"Invalid block structure for '{semantic}': {block}"
            )

        lines.extend(render_block(semantic, block))

    return "\n".join(lines) if lines else "暂无相关信息"

# 废案设计函数，其设计将极大增加工作量和维护成本，逻辑走得通但是需要对每一个会场信息进行拟合，极其繁琐
# def format_response(extracted: dict) -> str:
#     lines = []
#
#     for semantic, block in extracted.items():
#         lines.extend(render_block(semantic, block))
#
#     return "\n".join(lines) if lines else "暂无相关信息"
#
#
# def format_extracted_data(extracted: dict) -> str:
#     if not extracted:
#         return "暂无相关信息"
#
#     lines = []
#
#     if "location" in extracted:
#         loc = extracted["location"]
#         if "location" in loc:
#             lines.append(f"举办地点：{loc['location']}")
#         if "address" in loc:
#             lines.append(f"详细地址：{loc['address']}")
#
#     if "time" in extracted:
#         t = extracted["time"]
#         if "date" in t:
#             lines.append(f"日期：{t['date']}")
#         if "time" in t:
#             lines.append(f"时间：{t['time']}")
#
#     if "contact" in extracted:
#         c = extracted["contact"]
#         if "contact.phone" in c:
#             lines.append(f"联系电话：{c['contact.phone']}")
#         if "contact.email" in c:
#             lines.append(f"联系邮箱：{c['contact.email']}")
#         if "contact.website" in c:
#             lines.append(f"官网地址：{c['contact.website']}")
#
#     if "facilities" in extracted:
#         f = extracted["facilities"]
#         if "facilities" in f:
#             lines.append(f"提供设施：{f['facilities']}")
#
#     if "rules" in extracted:
#         r = extracted["rules"]
#         if "rules" in r:
#             lines.append(r"要求如下：{r['rules']}")
#
#     if "ticket" in extracted:
#         t = extracted["ticket"]
#
#         # t 里可能直接是 ticket_info
#         ticket_info = t.get("ticket_info") if isinstance(t, dict) else None
#
#         if isinstance(ticket_info, dict):
#             lines.append("🎫 票务信息：")
#
#             for key, value in ticket_info.items():
#                 if key == "registration_url":
#                     lines.append(f"🔗 购票链接：{value}")
#                 else:
#                     lines.append(f"  - {value}")
#
#     if "lineup" in extracted:
#         lineup = extracted["lineup"]
#
#         lines.append(" 演出阵容：")
#
#         for item in lineup:
#             artist = item.get("artist")
#             time = item.get("time")
#             stage = item.get("stage")
#
#             parts = []
#
#             if artist:
#                 parts.append(artist)
#             if stage:
#                 parts.append(f"（{stage}）")
#             if time:
#                 parts.append(f"- {time}")
#
#             lines.append("  - " + " ".join(parts))
#
#     return "\n".join(lines)
