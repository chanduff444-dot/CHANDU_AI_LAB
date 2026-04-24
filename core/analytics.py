import json
import os
from collections import Counter

LOG_FILE = "data/logs/interactions.json"
RECENT_WINDOW = 7


def load_logs():
    if not os.path.exists(LOG_FILE):
        print("No interaction logs found.")
        return []

    with open(LOG_FILE, "r") as f:
        return json.load(f)


def classify_query(query):
    lower = query.lower()

    code_keywords = [
        "code", "python", "function", "class",
        "error", "bug", "debug", "script", "algorithm"
    ]

    theory_keywords = [
        "explain", "define", "theory",
        "concept", "why", "derive", "proof"
    ]

    if any(k in lower for k in code_keywords):
        return "code"
    elif any(k in lower for k in theory_keywords):
        return "theory"
    else:
        return "general"


def detect_depth_signal(query):
    depth_keywords = [
        "derive", "proof", "step by step",
        "deeply", "why does", "mathematical",
        "complexity", "optimize"
    ]

    return any(k in query.lower() for k in depth_keywords)


def compute_stats(logs):
    total = len(logs)
    categories = Counter(classify_query(log["query"]) for log in logs)
    retrieval_count = sum(1 for log in logs if log["retrieval_used"])
    depth_count = sum(1 for log in logs if detect_depth_signal(log["query"]))

    return {
        "total": total,
        "code_ratio": categories["code"] / total if total else 0,
        "theory_ratio": categories["theory"] / total if total else 0,
        "retrieval_ratio": retrieval_count / total if total else 0,
        "depth_ratio": depth_count / total if total else 0,
    }


def compute_scores(stats):
    depth_score = stats["depth_ratio"] * 10
    balance_score = 10 - abs(stats["code_ratio"] - stats["theory_ratio"]) * 8
    ownership_score = stats["retrieval_ratio"] * 10

    csi = (
        depth_score * 0.4 +
        balance_score * 0.3 +
        ownership_score * 0.3
    )

    return {
        "depth_score": round(depth_score, 2),
        "balance_score": round(balance_score, 2),
        "ownership_score": round(ownership_score, 2),
        "csi": round(csi, 2)
    }


def generate_report():
    logs = load_logs()

    if not logs:
        return "No data to analyze."

    full_stats = compute_stats(logs)
    recent_logs = logs[-RECENT_WINDOW:]
    recent_stats = compute_stats(recent_logs)

    scores = compute_scores(full_stats)

    report = []

    report.append("🧠 EXECUTIVE INTELLIGENCE REPORT")
    report.append("=" * 60)

    # Behavioral Ratios
    report.append("\n📊 Behavioral Ratios (Full History)")
    report.append(f"Code Ratio: {round(full_stats['code_ratio'],2)}")
    report.append(f"Theory Ratio: {round(full_stats['theory_ratio'],2)}")
    report.append(f"Retrieval Ratio: {round(full_stats['retrieval_ratio'],2)}")
    report.append(f"Depth Ratio: {round(full_stats['depth_ratio'],2)}")

    # Scores
    report.append("\n🔥 Cognitive Strength Index")
    report.append(f"Depth Score: {scores['depth_score']}")
    report.append(f"Balance Score: {scores['balance_score']}")
    report.append(f"Ownership Score: {scores['ownership_score']}")
    report.append(f"⚡ Overall CSI: {scores['csi']} / 10")

    # Drift Analysis
    report.append("\n📈 Drift Analysis (Recent vs Full)")

    def compare(metric_name):
        full_val = full_stats[metric_name]
        recent_val = recent_stats[metric_name]

        trend = (
            "↑ Increasing" if recent_val > full_val
            else "↓ Decreasing" if recent_val < full_val
            else "→ Stable"
        )

        return f"{metric_name}: {round(full_val,2)} → {round(recent_val,2)} ({trend})"

    report.append(compare("code_ratio"))
    report.append(compare("theory_ratio"))
    report.append(compare("retrieval_ratio"))
    report.append(compare("depth_ratio"))

    # Guidance
    report.append("\n🎯 Growth Guidance")

    if scores["depth_score"] < 4:
        report.append("• Increase rigor. Ask more derivations and complexity analysis.")
    elif scores["depth_score"] < 7:
        report.append("• Moderate depth. Push deeper into optimization and proofs.")
    else:
        report.append("• Strong analytical rigor detected.")

    if scores["balance_score"] < 6:
        report.append("• Improve balance between theory and implementation.")
    else:
        report.append("• Good balance between coding and theory.")

    if scores["ownership_score"] < 5:
        report.append("• Use your own materials more often.")
    else:
        report.append("• Good integration of personal knowledge base.")

    report.append("\n" + "=" * 60)

    return "\n".join(report)


    # Behavioral
    print("\n📊 Behavioral Ratios (Full History)")
    print(f"Code Ratio: {round(full_stats['code_ratio'],2)}")
    print(f"Theory Ratio: {round(full_stats['theory_ratio'],2)}")
    print(f"Retrieval Ratio: {round(full_stats['retrieval_ratio'],2)}")
    print(f"Depth Ratio: {round(full_stats['depth_ratio'],2)}")

    # Scores
    print("\n🔥 Cognitive Strength Index")
    print(f"Depth Score: {scores['depth_score']}")
    print(f"Balance Score: {scores['balance_score']}")
    print(f"Ownership Score: {scores['ownership_score']}")
    print(f"⚡ Overall CSI: {scores['csi']} / 10")

    # Drift
    print("\n📈 Drift Analysis (Recent vs Full)")

    def compare(metric_name):
        full_val = full_stats[metric_name]
        recent_val = recent_stats[metric_name]

        trend = "↑ Increasing" if recent_val > full_val else \
                "↓ Decreasing" if recent_val < full_val else \
                "→ Stable"

        print(f"{metric_name}: {round(full_val,2)} → {round(recent_val,2)} ({trend})")

    compare("code_ratio")
    compare("theory_ratio")
    compare("retrieval_ratio")
    compare("depth_ratio")

    # Guidance
    print("\n🎯 Growth Guidance")

    if scores["depth_score"] < 4:
        print("• Increase rigor. Ask more derivations and complexity analysis.")
    elif scores["depth_score"] < 7:
        print("• Moderate depth. Push deeper into optimization and proofs.")
    else:
        print("• Strong analytical rigor detected.")

    if scores["balance_score"] < 6:
        print("• Improve balance between theory and implementation.")
    else:
        print("• Good balance between coding and theory.")

    if scores["ownership_score"] < 5:
        print("• Use your own materials more often.")
    else:
        print("• Good integration of personal knowledge base.")

    print("\n" + "=" * 70 + "\n")
