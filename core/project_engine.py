import json
import os
from datetime import datetime

PROJECT_FILE = "data/projects/active_project.json"


def ensure_project_folder():
    if not os.path.exists("data/projects"):
        os.makedirs("data/projects")


def create_project(name, goal, milestones):
    ensure_project_folder()

    project = {
        "name": name,
        "goal": goal,
        "milestones": [
            {"title": m, "completed": False}
            for m in milestones
        ],
        "created_at": datetime.now().isoformat(),
        "last_updated": datetime.now().isoformat()
    }

    with open(PROJECT_FILE, "w") as f:
        json.dump(project, f, indent=4)

    return "Project created successfully."


def load_project():
    if not os.path.exists(PROJECT_FILE):
        return None

    with open(PROJECT_FILE, "r") as f:
        return json.load(f)


def complete_milestone(index):
    project = load_project()
    if not project:
        return "No active project."

    if index < 0 or index >= len(project["milestones"]):
        return "Invalid milestone."

    project["milestones"][index]["completed"] = True
    project["last_updated"] = datetime.now().isoformat()

    with open(PROJECT_FILE, "w") as f:
        json.dump(project, f, indent=4)

    return "Milestone marked complete."
