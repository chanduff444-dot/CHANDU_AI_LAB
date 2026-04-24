import subprocess
import tempfile
import traceback
import os


def execute_python_code(code: str):
    """
    Executes Python code in an isolated temporary file.
    Returns (success: bool, output: str)
    """

    try:
        with tempfile.NamedTemporaryFile(
            mode="w",
            suffix=".py",
            delete=False
        ) as tmp_file:

            tmp_file.write(code)
            temp_path = tmp_file.name

        result = subprocess.run(
            ["python", temp_path],
            capture_output=True,
            text=True,
            timeout=10
        )

        os.remove(temp_path)

        if result.returncode == 0:
            return True, result.stdout.strip()

        else:
            return False, result.stderr.strip()

    except Exception:
        return False, traceback.format_exc()
