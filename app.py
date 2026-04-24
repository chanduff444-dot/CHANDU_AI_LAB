from chandu_lab.executor import run_python_file
from chandu_lab.experiment_tracker import (
    log_experiment,
    list_experiments,
    analyze_experiments
)

from core.rag_engine import rag_generate
from core.analytics import generate_report, load_logs, compute_stats, compute_scores
from core.skill_map import generate_skill_diagnostics, load_skills
from core.curriculum_engine import generate_curriculum


INTERACTION_ALERT_THRESHOLD = 5
CSI_ALERT_THRESHOLD = 4
CURRICULUM_MASTERY_THRESHOLD = 4


def should_trigger_auto_report():
    logs = load_logs()
    if not logs:
        return False

    stats = compute_stats(logs)
    scores = compute_scores(stats)

    if scores["csi"] < CSI_ALERT_THRESHOLD:
        return True

    if len(logs) % INTERACTION_ALERT_THRESHOLD == 0:
        return True

    return False


def should_trigger_curriculum():
    logs = load_logs()
    if not logs:
        return False

    stats = compute_stats(logs)
    scores = compute_scores(stats)

    if scores["csi"] >= 5:
        return False

    skills = load_skills()
    if not skills:
        return False

    weakest = min(skills.items(), key=lambda x: x[1]["mastery_score"])
    weakest_score = weakest[1]["mastery_score"]

    return weakest_score < CURRICULUM_MASTERY_THRESHOLD


def main():
    print("\n🧠 CHANDU AI LAB v1.1")
    print("Personal Intelligent ML Workspace Initialized.")
    print("Commands:")
    print("  report                    → Show intelligence report")
    print("  run <file.py>             → Execute Python file")
    print("  log                       → Log new experiment")
    print("  experiments               → View experiment history")
    print("  analyze experiments       → Analyze experiment trends")
    print("  exit                      → Quit\n")

    while True:
        query = input("You: ").strip()

        # ---------------- EXIT ---------------- #
        if query.lower() == "exit":
            print("\n👋 Shutting down Chandu AI Lab.")
            break

        # ---------------- REPORT ---------------- #
        if query.lower() == "report":
            generate_report()
            generate_skill_diagnostics()
            continue

        # ---------------- CODE EXECUTION ---------------- #
        if query.lower().startswith("run "):
            file_name = query[4:].strip()
            result = run_python_file(file_name)

            print("\n🛠 AI Lab Execution Result:\n")

            if result["status"] == "success":
                print("✅ Execution Successful\n")
                print("STDOUT:\n", result.get("stdout", ""))
                if result.get("stderr"):
                    print("\nSTDERR:\n", result["stderr"])
            else:
                print("❌ Execution Failed\n")
                print(result)

            print("\n" + "=" * 70 + "\n")
            continue

        # ---------------- LOG EXPERIMENT ---------------- #
        if query.lower() == "log":
            print("\n🧪 Log New Experiment\n")

            name = input("Project Name: ")
            model = input("Model Name: ")
            dataset = input("Dataset Used: ")
            accuracy = float(input("Accuracy: "))
            loss = float(input("Loss: "))
            notes = input("Notes: ")

            message = log_experiment(name, model, dataset, accuracy, loss, notes)

            print("\n✅", message)
            print("\n" + "=" * 70 + "\n")
            continue

        # ---------------- LIST EXPERIMENTS ---------------- #
        if query.lower() == "experiments":
            experiments = list_experiments()

            if not experiments:
                print("\nNo experiments logged yet.\n")
            else:
                print("\n📊 Experiment History:\n")
                for i, exp in enumerate(experiments, 1):
                    print(
                        f"{i}. {exp['name']} | Model: {exp['model']} | "
                        f"Dataset: {exp['dataset']} | "
                        f"Acc: {exp['accuracy']} | Loss: {exp['loss']} | "
                        f"Time: {exp['timestamp']}"
                    )

            print("\n" + "=" * 70 + "\n")
            continue

        # ---------------- ANALYZE EXPERIMENTS ---------------- #
        if query.lower() == "analyze experiments":
            result = analyze_experiments()
            print("\n🧠 Experiment Analysis:\n")
            print(result)
            print("\n" + "=" * 70 + "\n")
            continue

        # ---------------- NORMAL BRAIN MODE ---------------- #
        print("\n⏳ Thinking...\n")

        response = rag_generate(query)

        print("Chandu Core:")
        print(response)
        print("\n" + "=" * 70 + "\n")

        # ---------------- AUTO PERFORMANCE ALERT ---------------- #
        if should_trigger_auto_report():
            print("\n⚠ Performance Alert Triggered:\n")
            generate_report()

        # ---------------- ADAPTIVE CURRICULUM ---------------- #
        if should_trigger_curriculum():
            print("\n🎓 Adaptive Curriculum Activated:\n")
            generate_curriculum()


if __name__ == "__main__":
    main()
