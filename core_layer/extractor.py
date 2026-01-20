from .semantic_map import SEMANTIC_MAP

# 将函数处理后的信息喂给 AI　进行自然语言处理
def get_value_by_path(data: dict, path: str):
    """
    支持 contact.phone 这种路径
    """
    cur = data
    for key in path.split("."):
        if not isinstance(cur, dict):
            return None
        cur = cur.get(key)
        if cur is None:
            return None
    return cur

def extract_blocks(activity: dict, question: str) -> dict:
    q = question.lower()
    result = {}

    for semantic, config in SEMANTIC_MAP.items():
        if not any(k in q for k in config["keywords"]):
            continue

        t = config["type"]

        # 复合字段
        if t == "composite":
            values = {}
            for f in config.get("fields", []):
                if f in activity:
                    values[f] = activity[f]

            if values:
                result[semantic] = {
                    "type": "object",
                    "value": values
                }

        # 普通字段
        else:
            field = config.get("field")
            if not field:
                continue

            value = activity.get(field)
            if value is not None:
                result[semantic] = {
                    "type": t,
                    "value": value
                }

    return result

def extract_relevant_data(activity: dict, question: str) -> dict:
    q = question.lower()
    result = {}

    for semantic, config in SEMANTIC_MAP.items():
        if any(k in q for k in config["keywords"]):
            for field in config["field"]:
                if field == "lineup":
                    lineup = activity.get("lineup")
                    if lineup:
                        result["lineup"] = lineup
                else:
                    value = get_value_by_path(activity, field)
                    if value is not None:
                        result.setdefault(semantic, {})[field] = value

    return result
