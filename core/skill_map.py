import os
import json
from datetime import datetime
from core.analytics import load_logs, compute_stats, compute_scores, detect_depth_signal

SKILL_FILE = "data/skills/skill_progress.json"

# -------------------------
# Predefined Core Skills
# -------------------------

CORE_SKILLS = {
    # Deep Learning
    "gradient descent": "Optimization",
    "backprop": "Backpropagation",
    "loss function": "Loss Functions",
    "regularization": "Regularization",
    "cnn": "CNN Internals",
    "rnn": "RNN Mechanics",
    "transformer": "Attention & Transformers",
    "attention": "Attention & Transformers",
    "overfitting": "Generalization",
    "numerical stability": "Numerical Stability",

    # End-to-End AIML
    "data cleaning": "Data Preprocessing",
    "feature engineering": "Feature Engineering",
    "cross validation": "Model Evaluation",
    "metrics": "Model Evaluation",
    "hyperparameter": "Hyperparameter Tuning",
    "deployment": "Deployment",
    "pipeline": "ML Pipeline"
}


def ensure_skill_file():
    if not os.path.exists("data/skills"):
        os.makedirs("data/skills")

    if not os.path.exists(SKILL_FILE):
        with open(SKILL_FILE, "w") as f:
            json.dump({}, f)


def load_skills():
    ensure_skill_file()
    with open(SKILL_FILE, "r") as f:
        return json.load(f)


def save_skills(data):
    with open(SKILL_FILE, "w") as f:
        json.dump(data, f, indent=4)


def match_skill(query):
    lower = query.lower()
    for keyword, skill in CORE_SKILLS.items():
        if keyword in lower:
            return skill
    return None


def compute_mastery_score(skill_data, global_csi):
    interaction = skill_data["interaction_count"]
    depth_hits = skill_data["depth_hits"]

    depth_ratio = depth_hits / interaction if interaction else 0

    # Recency weight
    last_updated = datetime.fromisoformat(skill_data["last_updated"])
    days_since = (datetime.now() - last_updated).days
    recency_weight = max(0, 1 - (days_since / 30))  # decay over 30 days

    mastery = (
        depth_ratio * 0.5 +
        recency_weight * 0.3 +
        (global_csi / 10) * 0.2
    )

    return round(mastery * 10, 2)  # scale to 0–10


def update_skill_progress(query):
    skill = match_skill(query)
    if not skill:
        return  # No skill matched

    skills = load_skills()
    logs = load_logs()
    stats = compute_stats(logs)
    scores = compute_scores(stats)
    global_csi = scores["csi"]

    if skill not in skills:
        skills[skill] = {
            "interaction_count": 0,
            "depth_hits": 0,
            "last_updated": datetime.now().isoformat(),
            "mastery_score": 0
        }

    skills[skill]["interaction_count"] += 1

    if detect_depth_signal(query):
        skills[skill]["depth_hits"] += 1

    skills[skill]["last_updated"] = datetime.now().isoformat()

    # Recompute mastery
    skills[skill]["mastery_score"] = compute_mastery_score(
        skills[skill],
        global_csi
    )

    save_skills(skills)
def generate_skill_diagnostics():
    skills = load_skills()

    if not skills:
        return "No skill data available yet."

    from datetime import datetime

    report = []
    report.append("🧠 SKILL INTELLIGENCE REPORT")
    report.append("=" * 60)

    ranked = sorted(
        skills.items(),
        key=lambda x: x[1]["mastery_score"]
    )

    # Weakest
    report.append("\n📉 Weakest Skills:")
    for skill, data in ranked[:3]:
        report.append(f"{skill} → Mastery: {round(data['mastery_score'],2)}")

    # Strongest
    report.append("\n📈 Strongest Skills:")
    for skill, data in ranked[-3:]:
        report.append(f"{skill} → Mastery: {round(data['mastery_score'],2)}")

    # Neglected Skills
    neglected = []
    for skill, data in skills.items():
        last = datetime.fromisoformat(data["last_updated"])
        days_since = (datetime.now() - last).days
        if days_since > 7:
            neglected.append(skill)

    if neglected:
        report.append("\n⏳ Neglected Skills (>7 days):")
        for s in neglected:
            report.append(s)

    # Recommendation Logic
    report.append("\n🎯 Recommended Focus:")

    dl_priority = [
        "Optimization",
        "Backpropagation",
        "Loss Functions",
        "Regularization",
        "CNN Internals",
        "RNN Mechanics",
        "Attention & Transformers",
        "Generalization",
        "Numerical Stability"
    ]

    dl_skills = [
        (skill, data)
        for skill, data in skills.items()
        if skill in dl_priority
    ]

    dl_skills_sorted = sorted(dl_skills, key=lambda x: x[1]["mastery_score"])

    if dl_skills_sorted:
        weakest_dl = dl_skills_sorted[0]
        report.append(
            f"🔬 Deep Learning Focus → {weakest_dl[0]} "
            f"(Mastery: {round(weakest_dl[1]['mastery_score'],2)})"
        )
    else:
        weakest = ranked[0]
        report.append(
            f"🚀 Overall Focus → {weakest[0]} "
            f"(Mastery: {round(weakest[1]['mastery_score'],2)})"
        )

    report.append("\n" + "=" * 60)

    return "\n".join(report)


    # Detect neglected skills
    from datetime import datetime
    neglected = []

    for skill, data in skills.items():
        last = datetime.fromisoformat(data["last_updated"])
        days_since = (datetime.now() - last).days
        if days_since > 7:
            neglected.append(skill)

    if neglected:
        print("\n⏳ Neglected Skills (>7 days):")
        for s in neglected:
            print(f"  {s}")

    # Recommendation Logic (B + C)
    print("\n🎯 Recommended Focus:")

    # Deep Learning priority keywords
    dl_priority = [
        "Optimization",
        "Backpropagation",
        "Loss Functions",
        "Regularization",
        "CNN Internals",
        "RNN Mechanics",
        "Attention & Transformers",
        "Generalization",
        "Numerical Stability"
    ]

    # Sort deep learning skills first by mastery
    dl_skills = [
        (skill, data)
        for skill, data in skills.items()
        if skill in dl_priority
    ]

    dl_skills_sorted = sorted(dl_skills, key=lambda x: x[1]["mastery_score"])

    if dl_skills_sorted:
        weakest_dl = dl_skills_sorted[0]
        print(f"  🔬 Deep Learning Focus → {weakest_dl[0]} (Mastery: {weakest_dl[1]['mastery_score']})")
    else:
        # fallback to weakest overall
        weakest = ranked[0]
        print(f"  🚀 Overall Focus → {weakest[0]} (Mastery: {weakest[1]['mastery_score']})")

    print("\n" + "=" * 60 + "\n")
