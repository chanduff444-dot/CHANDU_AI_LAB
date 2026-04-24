# core/escalation.py

from core.analytics import compute_stats, compute_scores, load_logs, detect_depth_signal

DEPTH_THRESHOLD = 5  # moderate threshold


def get_current_scores():
    logs = load_logs()
    if not logs:
        return None

    stats = compute_stats(logs)
    scores = compute_scores(stats)
    return scores


def escalate_response(original_response, user_query, mode=None):
    scores = get_current_scores()

    if not scores:
        return original_response

    # ❌ Never interfere with code mode
    if mode == "Code":
        return original_response

    clean_query = user_query.lower().strip()

    # ❌ Skip very short queries
    if len(clean_query.split()) <= 2:
        return original_response

    # ❌ Skip greetings / casual inputs
    simple_inputs = ["hi", "hello", "hey", "ok", "thanks"]

    if clean_query in simple_inputs:
        return original_response

    if any(clean_query.startswith(word) for word in simple_inputs):
        return original_response

    depth_score = scores.get("depth_score", 0)

    # ❌ If already deep → skip
    if detect_depth_signal(user_query):
        return original_response

    # ❌ Only escalate when system depth is LOW
    if depth_score >= DEPTH_THRESHOLD:
        return original_response

    # 🧠 Final escalation message
    escalation = (
        "\n\n🧠 Adaptive Challenge:\n"
        "Try approaching this more deeply.\n"
        "- Add mathematical reasoning\n"
        "- Analyze complexity\n"
        "- Discuss limitations and optimizations"
    )

    return original_response + escalation