from core_layer.loader import load_all_activities
from core_layer.retriever import retrieve_activity_candidates
from core_layer.extractor import extract_blocks
from core_layer.responder import render_block
from core_layer.responder import render_response
from core_layer.retriever import select_activity

current_activity = None
def answer_question(question: str, activities: list[dict], current_activity: dict | None):
    candidates = retrieve_activity_candidates(activities, question)
    activity = select_activity(candidates, len(activities))

    if candidates:
        activity = candidates[0]["activity"]
    else:
        activity = current_activity

    if not activity:
        return None, "暂无相关活动信息"

    extracted = extract_blocks(activity, question)

    if not extracted:
        return activity, "暂无该活动的相关信息"

    text = render_response(extracted)
    return activity, text



def main():
    print("🎵 活动信息助手（输入 exit 退出）")

    # 对话上下文循环
    activities = load_all_activities()
    current_activity = None

    while True:
        question = input("\n你：").strip()
        if question.lower() == "exit":
            break

        current_activity, answer = answer_question(
            question,
            activities,
            current_activity
        )

        print("助手：", answer)


if __name__ == "__main__":
    main()
