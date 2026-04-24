"""
ai_file_assistant.py  —  AI File Assistant for Chandu AI Lab

Drop this file in your CHANDU_CORE folder.

Usage in lab_app.py:
    from ai_file_assistant import show_ai_file_assistant_page

    elif page_name == "AI File Assistant":
        show_ai_file_assistant_page(page_header)
"""

import os
import json
import datetime
import platform
import traceback

import streamlit as st
from langchain_ollama import OllamaLLM

# ═══════════════════════════════════════════════════════════════════════════
# Constants
# ═══════════════════════════════════════════════════════════════════════════

IS_WINDOWS = platform.system() == "Windows"
HOME       = os.path.expanduser("~")

TEXT_EXTENSIONS = {
    ".py", ".txt", ".json", ".md", ".csv", ".yaml", ".yml",
    ".html", ".js", ".css", ".log", ".ini", ".cfg", ".env",
    ".xml", ".ts", ".jsx", ".tsx", ".sh", ".bat", ".toml",
    ".rst", ".sql", ".r", ".kt", ".java", ".cpp", ".c",
    ".h", ".go", ".rs", ".php", ".rb", ".swift",
}

QUICK_PATHS = {
    "🖥️ Desktop":     os.path.join(HOME, "Desktop"),
    "📥 Downloads":   os.path.join(HOME, "Downloads"),
    "📄 Documents":   os.path.join(HOME, "Documents"),
    "🧠 CHANDU_CORE": os.path.join(HOME, "Desktop", "TRASH", "chandu_core"),
}

# Preset AI tasks — label: (button_label, system_prompt, user_template)
TASKS = {
    "📋 Summarize": {
        "icon": "📋",
        "label": "Summarize",
        "system": "You are a senior software engineer. Be concise and clear.",
        "prompt": "Summarize this file in 3-5 bullet points. Tell me: what it does, key functions/sections, and anything important to know.\n\nFile: {filename}\n\n{content}",
    },
    "🐛 Fix Bugs": {
        "icon": "🐛",
        "label": "Fix Bugs",
        "system": "You are an expert debugger. Find all bugs and return the COMPLETE corrected code. Always return the full file, not just the changed parts.",
        "prompt": "Find and fix ALL bugs in this code. Return the complete corrected file.\n\nFile: {filename}\n\n```\n{content}\n```\n\nAfter the code, list what you changed and why.",
    },
    "💬 Explain": {
        "icon": "💬",
        "label": "Explain Code",
        "system": "You are a patient teacher explaining code to a junior developer.",
        "prompt": "Explain this code line by line, in plain English. Group related lines together. Make it easy to understand.\n\nFile: {filename}\n\n{content}",
    },
    "📝 Add Comments": {
        "icon": "📝",
        "label": "Add Comments",
        "system": "You are a senior developer who writes clear, helpful docstrings and inline comments. Return the COMPLETE file with comments added.",
        "prompt": "Add docstrings and inline comments to this code. Return the complete file.\n\nFile: {filename}\n\n```\n{content}\n```",
    },
    "♻️ Refactor": {
        "icon": "♻️",
        "label": "Refactor",
        "system": "You are a clean code expert. Return the COMPLETE refactored file. Follow PEP8 for Python.",
        "prompt": "Refactor this code to be cleaner, more readable, and more efficient. Return the complete improved file.\n\nFile: {filename}\n\n```\n{content}\n```\n\nAfter the code, explain the main improvements.",
    },
    "🔒 Security Check": {
        "icon": "🔒",
        "label": "Security Check",
        "system": "You are a security auditor. Be thorough and specific.",
        "prompt": "Audit this code for security vulnerabilities. Check for: SQL injection, hardcoded secrets, unsafe inputs, insecure dependencies, exposed credentials, and any other risks.\n\nFile: {filename}\n\n{content}",
    },
    "⚡ Optimize": {
        "icon": "⚡",
        "label": "Optimize",
        "system": "You are a performance optimization expert. Return the COMPLETE optimized file.",
        "prompt": "Optimize this code for speed and memory efficiency. Return the complete optimized file.\n\nFile: {filename}\n\n```\n{content}\n```\n\nAfter the code, list the performance improvements made.",
    },
    "🧪 Write Tests": {
        "icon": "🧪",
        "label": "Write Tests",
        "system": "You are a QA engineer who writes comprehensive pytest tests.",
        "prompt": "Write comprehensive pytest unit tests for this code. Cover edge cases, happy paths, and error conditions.\n\nFile: {filename}\n\n{content}",
    },
    "📊 Analyze Data": {
        "icon": "📊",
        "label": "Analyze Data",
        "system": "You are a data analyst. Be specific with numbers and insights.",
        "prompt": "Analyze this data file. Tell me: structure, row/column counts, data types, key statistics, patterns, anomalies, and suggestions for use.\n\nFile: {filename}\n\n{content}",
    },
    "🔍 Find TODOs": {
        "icon": "🔍",
        "label": "Find TODOs",
        "system": "You are a thorough code reviewer.",
        "prompt": "Find all TODO, FIXME, HACK, NOTE, and unfinished sections in this file. For each one, suggest how to complete it.\n\nFile: {filename}\n\n{content}",
    },
}


# ═══════════════════════════════════════════════════════════════════════════
# Helpers
# ═══════════════════════════════════════════════════════════════════════════

def _file_icon(name: str) -> str:
    ext = os.path.splitext(name)[1].lower()
    icons = {
        ".py": "🐍", ".js": "📜", ".html": "🌐", ".css": "🎨",
        ".json": "📋", ".md": "📝", ".txt": "📄", ".csv": "📊",
        ".log": "🧾", ".env": "🔐", ".yaml": "⚙️", ".yml": "⚙️",
        ".sql": "🗄️", ".sh": "🔧", ".bat": "🔧",
    }
    return icons.get(ext, "📄")


def _fmt_size(b: int) -> str:
    if b < 1024:       return f"{b} B"
    elif b < 1024**2:  return f"{b/1024:.1f} KB"
    return f"{b/1024**2:.1f} MB"


def _read_file(path: str, max_chars: int = 30000) -> tuple[str, bool]:
    """Returns (content, truncated)"""
    try:
        with open(path, encoding="utf-8", errors="replace") as f:
            content = f.read()
        if len(content) > max_chars:
            return content[:max_chars], True
        return content, False
    except Exception as e:
        return f"Error reading file: {e}", False


def _save_file(path: str, content: str) -> bool:
    try:
        with open(path, "w", encoding="utf-8") as f:
            f.write(content)
        return True
    except Exception:
        return False


def _get_ollama_models() -> list[str]:
    try:
        import subprocess
        result = subprocess.run(["ollama", "list"], capture_output=True, text=True, timeout=5)
        lines  = result.stdout.strip().split("\n")[1:]
        models = [line.split()[0] for line in lines if line.strip()]
        return models if models else ["llama3.2", "mistral", "codellama"]
    except Exception:
        return ["llama3.2", "mistral", "codellama"]


def _ask_ai(prompt: str, system: str, model: str) -> str:
    try:
        llm = OllamaLLM(model=model, temperature=0.2)
        full_prompt = f"System: {system}\n\n{prompt}"
        return llm.invoke(full_prompt)
    except Exception as e:
        return f"❌ Error connecting to Ollama: {e}\n\nMake sure Ollama is running: `ollama serve`"


def _log_action(action: str, filename: str):
    log_path = "data/ai_file_log.json"
    os.makedirs("data", exist_ok=True)
    try:
        logs = []
        if os.path.exists(log_path):
            with open(log_path) as f:
                logs = json.load(f)
        logs.append({
            "time":   datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            "action": action,
            "file":   filename,
        })
        logs = logs[-100:]
        with open(log_path, "w") as f:
            json.dump(logs, f, indent=2)
    except Exception:
        pass


def _extract_code_block(text: str) -> str | None:
    """Extract first code block from AI response."""
    import re
    match = re.search(r"```(?:\w+)?\n(.*?)```", text, re.DOTALL)
    if match:
        return match.group(1).strip()
    return None


# ═══════════════════════════════════════════════════════════════════════════
# File Picker Panel
# ═══════════════════════════════════════════════════════════════════════════

def _file_picker() -> str | None:
    """Returns selected file path or None."""
    st.markdown("#### 📂 Select File")

    # Manual path input
    manual = st.text_input(
        "Paste file path directly",
        placeholder="C:/Users/chandrajit/Desktop/TRASH/chandu_core/snake_game.py",
        label_visibility="collapsed",
    )
    if manual and os.path.isfile(manual):
        return manual

    # Quick access buttons
    st.caption("Quick access:")
    cols = st.columns(len(QUICK_PATHS))
    for i, (label, path) in enumerate(QUICK_PATHS.items()):
        if cols[i].button(label, key=f"fp_qa_{label}"):
            if os.path.exists(path):
                st.session_state["fa_browse_path"] = path

    # Browser
    browse_path = st.session_state.get("fa_browse_path", HOME)
    new_path    = st.text_input("📍 Browse path", value=browse_path, label_visibility="collapsed")
    if new_path != browse_path and os.path.exists(new_path):
        st.session_state["fa_browse_path"] = new_path
        browse_path = new_path

    col_up, col_ref = st.columns(2)
    if col_up.button("⬆️ Up", key="fa_up"):
        parent = os.path.dirname(browse_path)
        if os.path.exists(parent):
            st.session_state["fa_browse_path"] = parent
            st.rerun()
    if col_ref.button("🔄 Refresh", key="fa_ref"):
        st.rerun()

    if not os.path.exists(browse_path):
        st.error("Path not found.")
        return None

    try:
        entries = sorted(os.scandir(browse_path), key=lambda e: (not e.is_dir(), e.name.lower()))
    except PermissionError:
        st.error("Permission denied.")
        return None

    selected = None
    for entry in entries[:60]:
        try:
            is_dir = entry.is_dir()
            ext    = os.path.splitext(entry.name)[1].lower()
            if is_dir:
                if st.button(f"📁 {entry.name}/", key=f"fa_dir_{entry.path}", use_container_width=True):
                    st.session_state["fa_browse_path"] = entry.path
                    st.rerun()
            elif ext in TEXT_EXTENSIONS:
                size = _fmt_size(entry.stat().st_size)
                if st.button(f"{_file_icon(entry.name)} {entry.name}  ({size})",
                             key=f"fa_file_{entry.path}", use_container_width=True):
                    selected = entry.path
        except Exception:
            pass

    return selected


# ═══════════════════════════════════════════════════════════════════════════
# Single File Mode
# ═══════════════════════════════════════════════════════════════════════════

def _single_file_mode(model: str):
    col_picker, col_main = st.columns([1, 2])

    with col_picker:
        picked = _file_picker()
        if picked:
            st.session_state["fa_selected_file"] = picked

    selected = st.session_state.get("fa_selected_file")

    with col_main:
        if not selected:
            st.markdown(
                "<div style='text-align:center;padding:80px 20px;color:#555;'>"
                "<div style='font-size:48px;'>👈</div>"
                "<div style='font-size:16px;margin-top:12px;'>Select a file to get started</div>"
                "</div>",
                unsafe_allow_html=True,
            )
            return

        if not os.path.exists(selected):
            st.error("File no longer exists.")
            st.session_state.pop("fa_selected_file", None)
            return

        fname   = os.path.basename(selected)
        content, truncated = _read_file(selected)
        size    = os.path.getsize(selected)
        ext     = os.path.splitext(fname)[1].lower()

        # File header
        st.markdown(
            f"<div style='background:#161616;border:1px solid #2a2a2a;border-radius:10px;"
            f"padding:14px 18px;margin-bottom:16px;'>"
            f"<span style='font-size:22px;'>{_file_icon(fname)}</span> "
            f"<span style='font-size:16px;font-weight:700;color:#e8eaed;'>{fname}</span>"
            f"<span style='color:#555;font-size:11px;margin-left:12px;'>{_fmt_size(size)}</span>"
            f"<br><span style='color:#666;font-size:11px;'>{selected}</span>"
            f"</div>",
            unsafe_allow_html=True,
        )

        if truncated:
            st.warning("⚠️ File is large — showing first 30,000 characters to AI.")

        # Quick action buttons
        st.markdown("**⚡ Quick Actions**")
        task_keys = list(TASKS.keys())
        rows = [task_keys[i:i+5] for i in range(0, len(task_keys), 5)]
        chosen_task = None
        for row in rows:
            cols = st.columns(len(row))
            for j, key in enumerate(row):
                t = TASKS[key]
                if cols[j].button(f"{t['icon']} {t['label']}", key=f"task_{key}", use_container_width=True):
                    chosen_task = key

        st.divider()

        # Custom prompt
        st.markdown("**💬 Custom Prompt**")
        custom_prompt = st.text_area(
            "Ask anything about this file",
            placeholder='e.g. "add a save_game() function that stores the score in a JSON file"',
            height=80,
            label_visibility="collapsed",
        )
        run_custom = st.button("🚀 Ask AI", use_container_width=True)

        st.divider()

        # Handle action
        prompt_to_run = None
        system_to_use = "You are a senior software engineer. Be helpful and precise."

        if chosen_task:
            t = TASKS[chosen_task]
            prompt_to_run = t["prompt"].format(filename=fname, content=content)
            system_to_use = t["system"]
            _log_action(t["label"], fname)

        elif run_custom and custom_prompt.strip():
            prompt_to_run = (
                f"File: {fname}\n\n"
                f"File content:\n```\n{content}\n```\n\n"
                f"Task: {custom_prompt.strip()}"
            )
            _log_action("Custom", fname)

        if prompt_to_run:
            with st.spinner(f"🤖 AI is analyzing `{fname}`..."):
                response = _ask_ai(prompt_to_run, system_to_use, model)
            st.session_state["fa_last_response"] = response
            st.session_state["fa_last_file"]     = selected
            st.session_state["fa_last_content"]  = content

        # Show response
        if "fa_last_response" in st.session_state and st.session_state.get("fa_last_file") == selected:
            response = st.session_state["fa_last_response"]

            st.markdown("### 🤖 AI Response")
            st.markdown(
                f"<div style='background:#0d1117;border:1px solid #2a2a2a;border-radius:10px;"
                f"padding:16px;max-height:500px;overflow-y:auto;white-space:pre-wrap;"
                f"font-family:monospace;font-size:13px;color:#e8eaed;line-height:1.6;'>"
                f"{response}</div>",
                unsafe_allow_html=True,
            )

            # Action buttons on response
            ra1, ra2, ra3, ra4 = st.columns(4)

            # Copy to clipboard via download
            ra1.download_button(
                "📋 Download Response",
                data=response,
                file_name=f"ai_response_{fname}.txt",
                use_container_width=True,
            )

            # Save response as new file
            save_name = ra2.text_input(
                "Save as", value=f"ai_{fname}", label_visibility="collapsed", key="fa_save_name"
            )
            if ra2.button("💾 Save Response", use_container_width=True):
                save_path = os.path.join(os.path.dirname(selected), save_name)
                if _save_file(save_path, response):
                    st.success(f"Saved to `{save_path}`")
                else:
                    st.error("Failed to save.")

            # Overwrite original with code block
            code_block = _extract_code_block(response)
            if code_block and ra3.button("✏️ Apply to File", use_container_width=True):
                if _save_file(selected, code_block):
                    st.success(f"✅ Applied to `{fname}`! Reload to see changes.")
                    st.session_state["fa_last_response"] = None
                else:
                    st.error("Failed to save.")

            if ra4.button("🗑️ Clear", use_container_width=True):
                st.session_state.pop("fa_last_response", None)
                st.rerun()

        # Chat follow-up
        if "fa_last_response" in st.session_state and st.session_state.get("fa_last_response"):
            st.divider()
            st.markdown("**💬 Follow-up Question**")
            follow_up = st.text_input(
                "Ask a follow-up",
                placeholder='e.g. "can you also add error handling?" or "explain that refactor more"',
                label_visibility="collapsed",
                key="fa_followup",
            )
            if st.button("↩️ Follow Up", use_container_width=True):
                if follow_up.strip():
                    prev = st.session_state.get("fa_last_response", "")
                    follow_prompt = (
                        f"File: {fname}\n\n"
                        f"Previous AI response:\n{prev[:3000]}\n\n"
                        f"Follow-up question: {follow_up}"
                    )
                    with st.spinner("🤖 Thinking..."):
                        new_resp = _ask_ai(follow_prompt, system_to_use, model)
                    st.session_state["fa_last_response"] = new_resp
                    st.rerun()


# ═══════════════════════════════════════════════════════════════════════════
# Compare Mode
# ═══════════════════════════════════════════════════════════════════════════

def _compare_mode(model: str):
    st.markdown("### 🆚 Compare Two Files")
    st.caption("AI reads both files and tells you differences, similarities, and which is better.")

    col1, col2 = st.columns(2)

    with col1:
        st.markdown("**File 1**")
        path1 = st.text_input("File 1 path", placeholder="Paste path...", key="fa_cmp1")

    with col2:
        st.markdown("**File 2**")
        path2 = st.text_input("File 2 path", placeholder="Paste path...", key="fa_cmp2")

    compare_type = st.radio(
        "What to compare",
        ["🔄 General differences", "⚡ Performance comparison", "🏗️ Architecture comparison", "🐛 Bug comparison"],
        horizontal=True,
    )

    if st.button("🆚 Compare with AI", use_container_width=True):
        if not path1 or not path2:
            st.warning("Enter both file paths.")
            return
        if not os.path.exists(path1):
            st.error(f"File 1 not found: `{path1}`")
            return
        if not os.path.exists(path2):
            st.error(f"File 2 not found: `{path2}`")
            return

        c1, _ = _read_file(path1, 15000)
        c2, _ = _read_file(path2, 15000)
        f1    = os.path.basename(path1)
        f2    = os.path.basename(path2)

        system = "You are a senior code reviewer comparing two files. Be structured and thorough."
        prompts = {
            "🔄 General differences": f"Compare these two files. List: key differences, similarities, what each does better, and a recommendation.\n\nFile 1 ({f1}):\n```\n{c1}\n```\n\nFile 2 ({f2}):\n```\n{c2}\n```",
            "⚡ Performance comparison": f"Compare the performance of these two files. Which is faster? More memory efficient? Explain why.\n\nFile 1 ({f1}):\n```\n{c1}\n```\n\nFile 2 ({f2}):\n```\n{c2}\n```",
            "🏗️ Architecture comparison": f"Compare the architecture and code structure of these files. Which has better design patterns?\n\nFile 1 ({f1}):\n```\n{c1}\n```\n\nFile 2 ({f2}):\n```\n{c2}\n```",
            "🐛 Bug comparison": f"Check both files for bugs. Which has more issues? List all bugs found in each.\n\nFile 1 ({f1}):\n```\n{c1}\n```\n\nFile 2 ({f2}):\n```\n{c2}\n```",
        }

        with st.spinner("🤖 AI is comparing both files..."):
            response = _ask_ai(prompts[compare_type], system, model)

        st.markdown("### 🤖 Comparison Result")
        st.markdown(response)


# ═══════════════════════════════════════════════════════════════════════════
# Batch Mode
# ═══════════════════════════════════════════════════════════════════════════

def _batch_mode(model: str):
    st.markdown("### 📦 Batch Analysis")
    st.caption("Run the same task on every file in a folder.")

    folder = st.text_input("📁 Folder path", placeholder="e.g. C:/Users/chandrajit/Desktop/TRASH/chandu_core")
    ext_filter = st.multiselect("File types", [".py", ".js", ".json", ".md", ".txt", ".csv", ".log"],
                                 default=[".py"])
    batch_task = st.selectbox("Task to run on each file", list(TASKS.keys()))
    max_files  = st.slider("Max files", 1, 20, 5)

    if st.button("🚀 Run Batch", use_container_width=True):
        if not folder or not os.path.exists(folder):
            st.error("Folder not found.")
            return

        files = [
            os.path.join(folder, f)
            for f in os.listdir(folder)
            if os.path.isfile(os.path.join(folder, f))
            and os.path.splitext(f)[1].lower() in ext_filter
        ][:max_files]

        if not files:
            st.warning("No matching files found.")
            return

        st.info(f"Running on {len(files)} files...")
        t = TASKS[batch_task]
        results = {}

        progress = st.progress(0)
        for i, fpath in enumerate(files):
            fname = os.path.basename(fpath)
            content, _ = _read_file(fpath, 10000)
            prompt = t["prompt"].format(filename=fname, content=content)
            with st.spinner(f"Analyzing {fname}..."):
                results[fname] = _ask_ai(prompt, t["system"], model)
            progress.progress((i + 1) / len(files))

        st.success(f"✅ Done! Analyzed {len(files)} files.")

        for fname, result in results.items():
            with st.expander(f"{_file_icon(fname)} {fname}"):
                st.markdown(result)

        # Save batch report
        report = "\n\n".join([f"=== {k} ===\n{v}" for k, v in results.items()])
        ts = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
        st.download_button(
            "⬇️ Download Full Report",
            data=report,
            file_name=f"batch_report_{ts}.txt",
            use_container_width=True,
        )


# ═══════════════════════════════════════════════════════════════════════════
# Recent Actions
# ═══════════════════════════════════════════════════════════════════════════

def _show_history():
    log_path = "data/ai_file_log.json"
    if not os.path.exists(log_path):
        st.info("No actions yet.")
        return
    try:
        with open(log_path) as f:
            logs = json.load(f)
        for entry in reversed(logs[-15:]):
            st.markdown(
                f"<span style='color:#555;font-size:10px;'>{entry['time']}</span>  "
                f"<span style='color:#c8960c;'>[{entry['action']}]</span>  "
                f"<span style='color:#e8eaed;'>{os.path.basename(entry['file'])}</span>",
                unsafe_allow_html=True,
            )
    except Exception:
        st.info("No history yet.")


# ═══════════════════════════════════════════════════════════════════════════
# Main Page
# ═══════════════════════════════════════════════════════════════════════════

def show_ai_file_assistant_page(page_header):
    page_header(
        "🤖", "AI File Assistant",
        "Select any file → AI summarizes, fixes bugs, explains, refactors, and more"
    )

    # Sidebar config
    with st.sidebar:
        st.divider()
        st.markdown("**🤖 AI File Assistant**")
        models   = _get_ollama_models()
        model    = st.selectbox("Model", models, key="fa_model")
        st.caption(f"Using: `{model}` via Ollama")
        st.divider()
        with st.expander("🧾 Recent Actions"):
            _show_history()

    # Mode tabs
    mode = st.radio(
        "Mode",
        ["🗂️ Single File", "🆚 Compare Files", "📦 Batch Analysis"],
        horizontal=True,
        label_visibility="collapsed",
    )
    st.divider()

    if mode == "🗂️ Single File":
        _single_file_mode(model)
    elif mode == "🆚 Compare Files":
        _compare_mode(model)
    elif mode == "📦 Batch Analysis":
        _batch_mode(model)