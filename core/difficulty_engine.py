from core.analytics import compute_stats, compute_scores, load_logs, detect_depth_signal

DEPTH_THRESHOLD = 7  # higher = less aggressive


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

    # ❌ Do NOT interfere with code generation
    if mode == "Code":
        return original_response

    depth_score = scores.get("depth_score", 0)

    # Check if user already asked a deep question
    user_is_deep = detect_depth_signal(user_query)

    # ✅ If user is already deep → no need to push
    if user_is_deep:
        return original_response

    # ✅ Only escalate if system depth is low
    if depth_score >= DEPTH_THRESHOLD:
        return original_response

    # ✅ Optional: avoid escalation on very short/simple queries
    if len(user_query.split()) < 4:
        return original_response

    # ✅ Escalation message
    escalation = (
        "\n\n🧠 Adaptive Challenge:\n"
        "Try approaching this more deeply.\n"
        "- Add mathematical reasoning\n"
        "- Analyze complexity\n"
        "- Discuss limitations and optimizations"
    )

    return original_response + escalation