import os
import json
from datetime import datetime

LOG_DIR = "data/logs"
LOG_FILE = os.path.join(LOG_DIR, "interactions.json")


def ensure_log_file():
    if not os.path.exists(LOG_DIR):
        os.makedirs(LOG_DIR)

    if not os.path.exists(LOG_FILE):
        with open(LOG_FILE, "w") as f:
            json.dump([], f)


def log_interaction(query, response, model_used, retrieval_used):
    ensure_log_file()

    log_entry = {
        "timestamp": datetime.now().isoformat(),
        "query": query,
        "response_length": len(response),
        "model_used": model_used,
        "retrieval_used": retrieval_used
    }

    with open(LOG_FILE, "r") as f:
        data = json.load(f)

    data.append(log_entry)

    with open(LOG_FILE, "w") as f:
        json.dump(data, f, indent=4)
