from core.skill_map import load_skills

# Deep Learning Focus List
DL_PRIORITY = [
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


def get_weakest_dl_skill():
    skills = load_skills()
    if not skills:
        return None

    dl_skills = [
        (skill, data)
        for skill, data in skills.items()
        if skill in DL_PRIORITY
    ]

    if not dl_skills:
        return None

    dl_sorted = sorted(dl_skills, key=lambda x: x[1]["mastery_score"])
    return dl_sorted[0][0]


def generate_curriculum():
    weakest_skill = get_weakest_dl_skill()

    if not weakest_skill:
        print("No Deep Learning skill data available yet.")
        return

    print("\n🧠 DEEP LEARNING CURRICULUM MODE")
    print("=" * 70)
    print(f"\n🎯 Focus Skill: {weakest_skill}\n")

    print("Level 1 — Conceptual Mastery:")
    print(f"• Explain {weakest_skill} clearly.")
    print("• Identify assumptions and limitations.")
    print("• Compare it with alternative methods.\n")

    print("Level 2 — Mathematical Derivation:")
    print(f"• Derive core equations for {weakest_skill}.")
    print("• Prove convergence or stability conditions if applicable.")
    print("• Analyze gradient behavior.\n")

    print("Level 3 — Implementation & Complexity:")
    print(f"• Implement {weakest_skill} from scratch.")
    print("• Analyze time and space complexity.")
    print("• Discuss optimization strategies and edge cases.\n")

    print("=" * 70 + "\n")
