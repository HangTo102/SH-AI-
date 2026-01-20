# 使用会场名称和 id 信息进行直接定位的函数，减少 AI 检索信息的时间，提高效率

# 对活动名称进行打分的函数
def score_activity(activity: dict, question: str) -> dict:
    q = question.lower()
    score = 0.0
    matched = []

    # 1️⃣ 活动名关键词命中（拆词）
    name = activity.get("name", "")
    for token in name:
        if token and token in q:
            score += 0.4
            matched.append("name_partial")
            break

    # 2️⃣ aliases 命中（如果有）
    for alias in activity.get("aliases", []):
        if alias.lower() in q:
            score += 0.5
            matched.append("alias")
            break

    # 3️⃣ 活动类型词（非常重要）
    type_keywords = activity.get("type_keywords", [])
    for t in type_keywords:
        if t in q:
            score += 0.3
            matched.append("type")
            break

    # 4️⃣ 地点弱命中
    location = activity.get("location", "")
    if location and location.lower() in q:
        score += 0.2
        matched.append("location")

    # 5️⃣ 时间弱命中（很轻）
    date = activity.get("date", "")
    if date and date in q:
        score += 0.1
        matched.append("date")

    return {
        "activity": activity,
        "score": round(min(score, 1.0), 2),
        "matched": matched
    }


# 对找到的活动进行候选排序，进行可能性挑选
def retrieve_activity_candidates(
    activities: list[dict],
    question: str
) -> list[dict]:
    scored = []

    for act in activities:
        result = score_activity(act, question)
        if result["score"] > 0:
            scored.append(result)

    scored.sort(key=lambda x: x["score"], reverse=True)
    return scored


# 核心选择函数
def select_activity(
    candidates: list[dict],
    total_activities: int
) -> dict | None:

    if not candidates:
        return None

    best = candidates[0]

    # 1️⃣ 只有一个活动，直接选
    if total_activities == 1:
        return best["activity"]

    # 2️⃣ 活动数量 ≤ 2：非常宽松
    if total_activities <= 2 and best["score"] >= 0.1:
        return best["activity"]

    # 3️⃣ 分数明显领先
    if len(candidates) > 1:
        second = candidates[1]
        if best["score"] - second["score"] >= 0.3:
            return best["activity"]

    # 4️⃣ 分数本身足够高
    if best["score"] >= 0.6:
        return best["activity"]

    # 5️⃣ 否则不确定
    return None

