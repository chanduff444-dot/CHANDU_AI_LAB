from core.analytics import load_logs, compute_stats, compute_scores
from core.skill_map import load_skills
from chandu_lab.experiment_tracker import list_experiments


def generate_guidance():
    logs = load_logs()

    if not logs:
        return None

    stats = compute_stats(logs)
    scores = compute_scores(stats)
    skills = load_skills()
    experiments = list_experiments()

    suggestions = []

    # 1️⃣ CSI Alert
    if scores["csi"] < 4:
        suggestions.append(
            "⚠ Your Cognitive Strength Index is low. "
            "Increase depth-based learning (derivations, complexity analysis)."
        )

    # 2️⃣ Imbalance Detection
    if stats["theory_ratio"] > 0.7:
        suggestions.append(
            "💡 You are heavily theory-focused. "
            "Run an implementation experiment to balance growth."
        )

    if stats["code_ratio"] > 0.7:
        suggestions.append(
            "📚 You are implementation-heavy. "
            "Revisit theory and derivations to deepen understanding."
        )

    # 3️⃣ Weakest Skill Nudge
    if skills:
        weakest = min(
            skills.items(),
            key=lambda x: x[1]["mastery_score"]
        )
        if weakest[1]["mastery_score"] < 4:
            suggestions.append(
                f"🎯 Weak skill detected: {weakest[0]}. "
                "Consider focused practice or an experiment."
            )

    # 4️⃣ Experiment Inactivity
    if len(experiments) == 0:
        suggestions.append(
            "🧪 No experiments logged yet. Start testing your models."
        )

    if suggestions:
        return suggestions[0]  # only show one to avoid spam

    return None
