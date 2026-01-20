import json
import os

def load_json_file(path: str) -> dict:
    """
    通用 JSON 文件加载
    """
    if not os.path.exists(path):
        raise FileNotFoundError(f"JSON 文件不存在: {path}")

    with open(path, "r", encoding="utf-8") as f:
        return json.load(f)


def load_all_activities() -> list[dict]:
    """
    加载 data/activities 目录下的所有活动
    """
    base_dir = os.path.dirname(os.path.abspath(__file__))
    activities_dir = os.path.join(base_dir, "..", "data")

    activities = []

    for filename in os.listdir(activities_dir):
        if not filename.endswith(".json"):
            continue

        path = os.path.join(activities_dir, filename)
        activity = load_json_file(path)
        activity["_source_file"] = filename  # 调试用
        activities.append(activity)

    return activities
