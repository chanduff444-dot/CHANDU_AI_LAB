"""
tool_system.py  —  Upgraded Tool System with Full PC Access
Chandu AI Lab

Drop this file in your CHANDU_CORE folder (replace old tool_system.py).

Usage in lab_app.py:
    from tool_system import show_tool_system_page

    elif page_name == "Tool System":
        show_tool_system_page(page_header)
"""

import os
import sys
import json
import time
import shutil
import datetime
import subprocess
import traceback
import tempfile
import platform

import streamlit as st


# ═══════════════════════════════════════════════════════════════════════════
# Constants
# ═══════════════════════════════════════════════════════════════════════════

IS_WINDOWS = platform.system() == "Windows"
HOME       = os.path.expanduser("~")

QUICK_PATHS = {
    "🖥️ Desktop":    os.path.join(HOME, "Desktop"),
    "📥 Downloads":  os.path.join(HOME, "Downloads"),
    "📄 Documents":  os.path.join(HOME, "Documents"),
    "🧠 CHANDU_CORE": os.path.join(HOME, "Desktop", "TRASH", "chandu_core"),
    "💾 C:/":        "C:/",
    "💾 D:/":        "D:/",
}

TEXT_EXTENSIONS = {
    ".py", ".txt", ".json", ".md", ".csv", ".yaml", ".yml",
    ".html", ".js", ".css", ".log", ".ini", ".cfg", ".env",
    ".xml", ".ts", ".jsx", ".tsx", ".sh", ".bat",
}

IMAGE_EXTENSIONS = {".png", ".jpg", ".jpeg", ".gif", ".webp", ".bmp"}


# ═══════════════════════════════════════════════════════════════════════════
# Helpers
# ═══════════════════════════════════════════════════════════════════════════

def _fmt_size(b: int) -> str:
    if b < 1024:        return f"{b} B"
    elif b < 1024**2:   return f"{b/1024:.1f} KB"
    elif b < 1024**3:   return f"{b/1024**2:.1f} MB"
    return f"{b/1024**3:.1f} GB"


def _run_cmd(cmd: str, cwd: str = None, timeout: int = 30) -> dict:
    start = time.time()
    try:
        result = subprocess.run(
            cmd, shell=True, cwd=cwd,
            capture_output=True, text=True,
            timeout=timeout,
            encoding="utf-8", errors="replace",
        )
        output  = (result.stdout + result.stderr).strip()
        elapsed = time.time() - start
        return {"success": result.returncode == 0, "output": output, "elapsed": elapsed}
    except subprocess.TimeoutExpired:
        return {"success": False, "output": f"Timed out after {timeout}s", "elapsed": timeout}
    except Exception as e:
        return {"success": False, "output": str(e), "elapsed": 0}


def _run_python(code: str, timeout: int = 15) -> dict:
    start = time.time()
    try:
        with tempfile.NamedTemporaryFile(suffix=".py", mode="w",
                                         delete=False, encoding="utf-8") as tmp:
            tmp.write(code)
            tmp_path = tmp.name
        result = subprocess.run(
            [sys.executable, tmp_path],
            capture_output=True, text=True,
            timeout=timeout, encoding="utf-8", errors="replace",
        )
        os.unlink(tmp_path)
        elapsed = time.time() - start
        return {
            "success": result.returncode == 0,
            "stdout":  result.stdout,
            "stderr":  result.stderr,
            "elapsed": elapsed,
        }
    except subprocess.TimeoutExpired:
        return {"success": False, "stdout": "", "stderr": f"Timed out after {timeout}s", "elapsed": timeout}
    except Exception as e:
        return {"success": False, "stdout": "", "stderr": traceback.format_exc(), "elapsed": 0}


def _log_action(tool: str, detail: str):
    log_path = "data/tool_log.json"
    os.makedirs("data", exist_ok=True)
    try:
        logs = []
        if os.path.exists(log_path):
            with open(log_path) as f:
                logs = json.load(f)
        logs.append({
            "time":   datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            "tool":   tool,
            "detail": detail,
        })
        logs = logs[-200:]
        with open(log_path, "w") as f:
            json.dump(logs, f, indent=2)
    except Exception:
        pass


def _file_icon(name: str) -> str:
    ext = os.path.splitext(name)[1].lower()
    icons = {
        ".py": "🐍", ".js": "📜", ".html": "🌐", ".css": "🎨",
        ".json": "📋", ".md": "📝", ".txt": "📄", ".csv": "📊",
        ".png": "🖼️", ".jpg": "🖼️", ".jpeg": "🖼️", ".gif": "🖼️",
        ".mp4": "🎬", ".mp3": "🎵", ".pdf": "📕", ".zip": "🗜️",
        ".exe": "⚙️", ".bat": "⚙️", ".log": "🧾", ".env": "🔐",
    }
    return icons.get(ext, "📄")


# ═══════════════════════════════════════════════════════════════════════════
# Tool 1 — Full PC File Explorer
# ═══════════════════════════════════════════════════════════════════════════

def tool_pc_explorer():
    st.markdown("### 📂 PC File Explorer")
    st.caption("Browse, open, edit, copy, move, delete any file on your PC.")

    # Quick access shortcuts
    st.markdown("**Quick Access**")
    cols = st.columns(len(QUICK_PATHS))
    for i, (label, path) in enumerate(QUICK_PATHS.items()):
        if cols[i].button(label, key=f"qa_{label}"):
            if os.path.exists(path):
                st.session_state["explorer_path"] = path
            else:
                st.warning(f"Path not found: `{path}`")

    current_path = st.session_state.get("explorer_path", HOME)
    new_path = st.text_input("📍 Current path", value=current_path)
    if new_path != current_path:
        if os.path.exists(new_path):
            st.session_state["explorer_path"] = new_path
            current_path = new_path
        else:
            st.error(f"Path not found: `{new_path}`")

    col_up, col_open, col_refresh = st.columns(3)
    if col_up.button("⬆️ Go Up"):
        parent = os.path.dirname(current_path)
        if os.path.exists(parent):
            st.session_state["explorer_path"] = parent
            st.rerun()
    if col_open.button("🪟 Open in Explorer"):
        try:
            os.startfile(current_path) if IS_WINDOWS else subprocess.Popen(["xdg-open", current_path])
        except Exception as e:
            st.error(str(e))
    if col_refresh.button("🔄 Refresh"):
        st.rerun()

    st.divider()

    if not os.path.exists(current_path):
        st.error("Path does not exist.")
        return

    try:
        entries = list(os.scandir(current_path))
        items   = sorted(entries, key=lambda e: (not e.is_dir(), e.name.lower()))
    except PermissionError:
        st.error("Permission denied.")
        return

    col_list, col_preview = st.columns([2, 3])

    with col_list:
        st.markdown(f"**{os.path.basename(current_path) or current_path}** — {len(items)} items")
        for entry in items:
            try:
                is_dir = entry.is_dir()
                size   = "" if is_dir else f" ({_fmt_size(entry.stat().st_size)})"
                icon   = "📁" if is_dir else _file_icon(entry.name)
                if st.button(f"{icon} {entry.name}{size}", key=f"entry_{entry.path}", use_container_width=True):
                    if is_dir:
                        st.session_state["explorer_path"] = entry.path
                        st.session_state.pop("preview_file", None)
                        st.rerun()
                    else:
                        st.session_state["preview_file"] = entry.path
            except Exception:
                pass

    with col_preview:
        preview_path = st.session_state.get("preview_file")
        if preview_path and os.path.exists(preview_path):
            fname = os.path.basename(preview_path)
            ext   = os.path.splitext(fname)[1].lower()
            size  = os.path.getsize(preview_path)

            st.markdown(f"**{_file_icon(fname)} {fname}**")
            st.caption(f"`{preview_path}` — {_fmt_size(size)}")

            a1, a2, a3, a4 = st.columns(4)
            if a1.button("🪟 Open"):
                try:
                    os.startfile(preview_path) if IS_WINDOWS else subprocess.Popen(["xdg-open", preview_path])
                except Exception as e:
                    st.error(str(e))
            if a2.button("💻 VS Code"):
                _run_cmd(f'code "{preview_path}"')
                st.success("Opened in VS Code!")

            new_name = st.text_input("Rename to", value=fname, key="rename_input")
            if a3.button("✏️ Rename"):
                new_p = os.path.join(os.path.dirname(preview_path), new_name)
                try:
                    os.rename(preview_path, new_p)
                    st.session_state["preview_file"] = new_p
                    st.success(f"Renamed!")
                    st.rerun()
                except Exception as e:
                    st.error(str(e))
            if a4.button("🗑️ Delete"):
                try:
                    os.remove(preview_path)
                    st.session_state.pop("preview_file", None)
                    st.success("Deleted!")
                    st.rerun()
                except Exception as e:
                    st.error(str(e))

            copy_dest = st.text_input("Copy to folder", placeholder="e.g. C:/Users/chandrajit/Desktop")
            if st.button("📋 Copy File"):
                try:
                    shutil.copy2(preview_path, os.path.join(copy_dest, fname))
                    st.success("Copied!")
                except Exception as e:
                    st.error(str(e))

            st.divider()

            if size > 5_000_000:
                st.warning("File too large to preview")
            elif ext in IMAGE_EXTENSIONS:
                st.image(preview_path)
            elif ext in TEXT_EXTENSIONS:
                try:
                    with open(preview_path, encoding="utf-8", errors="replace") as f:
                        content = f.read()
                    edited = st.text_area("Edit content", value=content[:10000], height=350)
                    if st.button("💾 Save Changes"):
                        with open(preview_path, "w", encoding="utf-8") as f:
                            f.write(edited)
                        st.success("Saved!")
                    st.download_button("⬇️ Download", data=content, file_name=fname)
                except Exception as e:
                    st.error(str(e))
            else:
                with open(preview_path, "rb") as f:
                    st.download_button("⬇️ Download", data=f.read(), file_name=fname)
        else:
            st.info("👈 Click any file to preview or edit it.")

    st.divider()
    st.markdown("**➕ Create New**")
    cn1, cn2, cn3 = st.columns([2, 1, 1])
    new_item_name = cn1.text_input("Name", placeholder="script.py or new_folder", label_visibility="collapsed")
    item_type     = cn2.selectbox("Type", ["📄 File", "📁 Folder"], label_visibility="collapsed")
    if cn3.button("➕ Create"):
        if new_item_name.strip():
            full = os.path.join(current_path, new_item_name.strip())
            try:
                if "Folder" in item_type:
                    os.makedirs(full, exist_ok=True)
                else:
                    open(full, "w").close()
                    st.session_state["preview_file"] = full
                st.success(f"Created `{full}`")
                st.rerun()
            except Exception as e:
                st.error(str(e))


# ═══════════════════════════════════════════════════════════════════════════
# Tool 2 — Real Terminal
# ═══════════════════════════════════════════════════════════════════════════

def tool_terminal():
    st.markdown("### 🖥️ Terminal")
    st.caption("Run any command — CMD, Python, Git, pip, anything.")

    cwd = st.text_input("📍 Working directory", value=st.session_state.get("terminal_cwd", HOME))
    st.session_state["terminal_cwd"] = cwd

    st.markdown("**Quick Commands**")
    qcols = st.columns(6)
    quick_cmds = {
        "📋 Dir":       "dir" if IS_WINDOWS else "ls -la",
        "🐍 Python":    "python --version",
        "📦 Pip list":  "pip list",
        "🌿 Git status":"git status",
        "💾 Disk":      "wmic logicaldisk get size,freespace,caption" if IS_WINDOWS else "df -h",
        "📊 Tasks":     "tasklist" if IS_WINDOWS else "ps aux",
    }

    selected_quick = None
    for i, (label, cmd) in enumerate(quick_cmds.items()):
        if qcols[i].button(label, key=f"qcmd_{label}"):
            selected_quick = cmd

    if "terminal_history" not in st.session_state:
        st.session_state["terminal_history"] = []

    cmd_input = st.text_input("$ Command", value=selected_quick or "",
                               placeholder="dir / git status / pip install numpy ...",
                               label_visibility="collapsed")

    col_run, col_clear = st.columns([3, 1])
    run_clicked   = col_run.button("▶ Run", use_container_width=True)
    clear_clicked = col_clear.button("🗑️ Clear", use_container_width=True)

    if clear_clicked:
        st.session_state["terminal_history"] = []
        st.rerun()

    if run_clicked and cmd_input.strip():
        work_dir = cwd if os.path.exists(cwd) else HOME
        with st.spinner(f"Running..."):
            result = _run_cmd(cmd_input, cwd=work_dir, timeout=60)
        st.session_state["terminal_history"].append({
            "cmd": cmd_input, "output": result["output"],
            "success": result["success"],
            "time": datetime.datetime.now().strftime("%H:%M:%S"),
            "elapsed": result["elapsed"],
        })
        _log_action("terminal", cmd_input)

    for entry in reversed(st.session_state.get("terminal_history", [])[-20:]):
        color = "#43a047" if entry["success"] else "#e53935"
        st.markdown(
            f"<div style='background:#0d0d0d;border-left:3px solid {color};"
            f"border-radius:0 8px 8px 0;padding:8px 12px;margin-bottom:4px;'>"
            f"<span style='color:#c8960c;font-family:monospace;font-size:12px;'>$ {entry['cmd']}</span>"
            f"<span style='color:#555;font-size:10px;float:right;'>{entry['time']} · {entry['elapsed']:.2f}s</span>"
            f"</div>",
            unsafe_allow_html=True,
        )
        if entry["output"]:
            st.code(entry["output"], language="text")


# ═══════════════════════════════════════════════════════════════════════════
# Tool 3 — Code Runner
# ═══════════════════════════════════════════════════════════════════════════

def tool_code_runner():
    st.markdown("### 🐍 Code Runner")

    templates = {
        "— blank —": "",
        "Hello World": 'print("Hello from Chandu AI Lab!")',
        "System info": (
            "import platform, psutil\n"
            "print('OS:', platform.system(), platform.release())\n"
            "print('CPU:', psutil.cpu_percent(), '%')\n"
            "print('RAM:', round(psutil.virtual_memory().used/1e9,2), 'GB')"
        ),
        "List Desktop files": (
            "import os\n"
            "desktop = os.path.expanduser('~/Desktop')\n"
            "for f in os.listdir(desktop): print(f)"
        ),
        "Numpy": "import numpy as np\nprint(np.random.randn(3,3))",
    }

    template = st.selectbox("Template", list(templates.keys()))
    code = st.text_area("Code", value=templates[template], height=300, label_visibility="collapsed")
    timeout = st.slider("Timeout (s)", 1, 60, 15)

    col1, col2 = st.columns(2)
    if col1.button("▶ Run", use_container_width=True):
        if code.strip():
            with st.spinner("Running..."):
                result = _run_python(code, timeout)
            if result["success"]:
                st.code(result["stdout"] or "No output", language="text")
            else:
                st.error("Error:")
                st.code(result["stderr"], language="text")
            st.caption(f"⏱ {result['elapsed']:.2f}s")

    if col2.button("💾 Save + Run", use_container_width=True):
        ts   = datetime.datetime.now().strftime("%H%M%S")
        full = os.path.join(HOME, "Desktop", f"script_{ts}.py")
        with open(full, "w") as f:
            f.write(code)
        st.info(f"Saved to `{full}`")
        with st.spinner("Running..."):
            result = _run_python(code, timeout)
        if result["success"]:
            st.code(result["stdout"] or "No output", language="text")
        else:
            st.error(result["stderr"])


# ═══════════════════════════════════════════════════════════════════════════
# Tool 4 — File Search
# ═══════════════════════════════════════════════════════════════════════════

def tool_file_search():
    st.markdown("### 🔍 File Search")

    search_root  = st.text_input("Search in", value=HOME)
    search_query = st.text_input("Search query", placeholder="e.g. snake_game.py or .py")
    search_mode  = st.radio("Search by", ["File name", "File content"], horizontal=True)
    max_results  = st.slider("Max results", 10, 200, 50)

    if st.button("🔍 Search", use_container_width=True):
        if not search_query.strip():
            st.warning("Enter a search query.")
            return
        if not os.path.exists(search_root):
            st.error("Folder not found.")
            return

        results = []
        with st.spinner("Searching..."):
            try:
                for dirpath, dirnames, filenames in os.walk(search_root):
                    dirnames[:] = [d for d in dirnames
                                   if d not in {"Windows", "System32", "$Recycle.Bin",
                                                "__pycache__", ".git", "node_modules"}
                                   and not d.startswith(".")]
                    for fname in filenames:
                        full = os.path.join(dirpath, fname)
                        if search_mode == "File name":
                            if search_query.lower() in fname.lower():
                                results.append(full)
                        else:
                            ext = os.path.splitext(fname)[1].lower()
                            if ext in TEXT_EXTENSIONS:
                                try:
                                    with open(full, encoding="utf-8", errors="ignore") as f:
                                        if search_query.lower() in f.read().lower():
                                            results.append(full)
                                except Exception:
                                    pass
                        if len(results) >= max_results:
                            break
                    if len(results) >= max_results:
                        break
            except Exception as e:
                st.error(str(e))

        st.success(f"Found {len(results)} results")
        for path in results:
            col1, col2 = st.columns([4, 1])
            col1.markdown(f"{_file_icon(path)} `{path}`")
            if col2.button("Open", key=f"sopen_{path}"):
                st.session_state["preview_file"]  = path
                st.session_state["explorer_path"] = os.path.dirname(path)

        _log_action("search", f"'{search_query}' → {len(results)} results")


# ═══════════════════════════════════════════════════════════════════════════
# Tool 5 — App Launcher
# ═══════════════════════════════════════════════════════════════════════════

def tool_app_launcher():
    st.markdown("### 🚀 App Launcher")

    apps = {
        "💻 VS Code":     "code",
        "📝 Notepad":     "notepad",
        "📁 Explorer":    "explorer",
        "🌐 Chrome":      "chrome",
        "🖥️ CMD":         "cmd",
        "🐍 Python":      "python",
        "📊 Task Manager":"taskmgr",
        "⚙️ Settings":    "ms-settings:",
    }

    app_cols = st.columns(4)
    for i, (label, cmd) in enumerate(apps.items()):
        if app_cols[i % 4].button(label, key=f"app_{label}", use_container_width=True):
            try:
                if cmd.startswith("ms-"):
                    os.startfile(cmd)
                else:
                    subprocess.Popen(cmd, shell=True)
                st.success(f"Launched {label}!")
            except Exception as e:
                st.error(str(e))

    st.divider()
    st.markdown("**Open File / URL / App**")
    target = st.text_input("Path or URL", placeholder="C:/file.py  or  https://github.com",
                            label_visibility="collapsed")
    if st.button("🚀 Open", use_container_width=True):
        if target.strip():
            try:
                os.startfile(target.strip()) if IS_WINDOWS else subprocess.Popen(["xdg-open", target.strip()])
                st.success(f"Opened!")
            except Exception as e:
                st.error(str(e))


# ═══════════════════════════════════════════════════════════════════════════
# Main Page
# ═══════════════════════════════════════════════════════════════════════════

def show_tool_system_page(page_header):
    page_header(
        "🛠️", "Tool System",
        "Full PC access — browse files, run terminal commands, search, launch apps"
    )

    tool = st.radio(
        "Tool",
        ["📂 PC Explorer", "🖥️ Terminal", "🐍 Code Runner", "🔍 File Search", "🚀 App Launcher"],
        horizontal=True,
        label_visibility="collapsed",
    )
    st.divider()

    if tool == "📂 PC Explorer":
        tool_pc_explorer()
    elif tool == "🖥️ Terminal":
        tool_terminal()
    elif tool == "🐍 Code Runner":
        tool_code_runner()
    elif tool == "🔍 File Search":
        tool_file_search()
    elif tool == "🚀 App Launcher":
        tool_app_launcher()

    st.divider()
    with st.expander("🧾 Recent Actions"):
        log_path = "data/tool_log.json"
        if os.path.exists(log_path):
            try:
                with open(log_path) as f:
                    logs = json.load(f)
                for entry in reversed(logs[-10:]):
                    st.markdown(
                        f"<span style='color:#555;font-size:10px;'>{entry['time']}</span> "
                        f"<span style='color:#c8960c;'>[{entry['tool']}]</span> "
                        f"<span style='color:#e8eaed;'>{entry['detail']}</span>",
                        unsafe_allow_html=True,
                    )
            except Exception:
                pass