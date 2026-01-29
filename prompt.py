import json

def build_prompt(context: dict, question: str) -> str:
    context_json = json.dumps(context, ensure_ascii=False, indent=2)

    return f"""
你是一个活动信息智能助手。
你只能基于【已知信息】回答问题，不能编造不存在的内容。

【已知信息】
{context_json}

【用户问题】
{question}

如果已知信息中没有答案，请明确说明“暂无相关信息”。
""".strip()
