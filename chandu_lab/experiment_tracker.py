import json
import os
from datetime import datetime

PROJECTS_FILE = "chandu_lab/projects.json"


def initialize_storage():
    if not os.path.exists(PROJECTS_FILE):
        with open(PROJECTS_FILE, "w") as f:
            json.dump({"projects": []}, f)


def load_data():
    initialize_storage()

    try:
        with open(PROJECTS_FILE, "r") as f:
            return json.load(f)
    except (json.JSONDecodeError, FileNotFoundError):
        # If corrupted or empty, reset safely
        data = {"projects": []}
        with open(PROJECTS_FILE, "w") as f:
            json.dump(data, f, indent=4)
        return data


def log_experiment(name, model, dataset, accuracy, loss, notes):
    data = load_data()

    experiment = {
        "name": name,
        "model": model,
        "dataset": dataset,
        "accuracy": accuracy,
        "loss": loss,
        "notes": notes,
        "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    }

    data["projects"].append(experiment)

    with open(PROJECTS_FILE, "w") as f:
        json.dump(data, f, indent=4)

    return "Experiment logged successfully."


def list_experiments():
    data = load_data()
    return data["projects"]
def analyze_experiments():
    data = load_data()
    experiments = data["projects"]

    if not experiments:
        return "No experiments available for analysis."

    best_acc = max(experiments, key=lambda x: x["accuracy"])
    lowest_loss = min(experiments, key=lambda x: x["loss"])

    analysis = []
    analysis.append(f"📈 Best Accuracy: {best_acc['accuracy']} ({best_acc['name']})")
    analysis.append(f"📉 Lowest Loss: {lowest_loss['loss']} ({lowest_loss['name']})")

    if len(experiments) >= 2:
        last = experiments[-1]
        prev = experiments[-2]

        acc_diff = last["accuracy"] - prev["accuracy"]
        loss_diff = last["loss"] - prev["loss"]

        analysis.append("\n🔄 Recent Trend:")

        if acc_diff > 0:
            analysis.append(f"Accuracy Improved by {round(acc_diff, 4)}")
        elif acc_diff < 0:
            analysis.append(f"Accuracy Dropped by {round(abs(acc_diff), 4)}")
        else:
            analysis.append("Accuracy unchanged")

        if loss_diff < 0:
            analysis.append(f"Loss Decreased by {round(abs(loss_diff), 4)}")
        elif loss_diff > 0:
            analysis.append(f"Loss Increased by {round(loss_diff, 4)}")
        else:
            analysis.append("Loss unchanged")

        if acc_diff <= 0 and loss_diff >= 0:
            analysis.append("\n⚠ Suggestion: Model may be stagnating. Consider tuning hyperparameters.")
        else:
            analysis.append("\n✅ Model shows positive learning trend.")

    return "\n".join(analysis)
