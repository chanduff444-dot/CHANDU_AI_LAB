import subprocess
import sys
import os
import json
from datetime import datetime

PROJECTS_FILE = "chandu_lab/projects.json"


def run_python_file(file_path):
    if not os.path.exists(file_path):
        return {"status": "error", "output": "File does not exist."}

    try:
        result = subprocess.run(
            [sys.executable, file_path],
            capture_output=True,
            text=True,
            timeout=60
        )

        return {
            "status": "success" if result.returncode == 0 else "error",
            "stdout": result.stdout,
            "stderr": result.stderr,
            "returncode": result.returncode
        }

    except subprocess.TimeoutExpired:
        return {"status": "error", "output": "Execution timed out."}
