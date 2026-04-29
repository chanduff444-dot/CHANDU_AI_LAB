"""
github_tool.py  —  GitHub Tool page for Chandu AI Lab

Drop this file in your CHANDU_CORE folder.

Requirements:
    pip install PyGithub python-dotenv

.env file (in CHANDU_CORE/):
    GITHUB_TOKEN=ghp_yourtoken
    GITHUB_USERNAME=yourchandrajit

Usage in lab_app.py:
    from github_tool import show_github_tool_page

    elif page_name == "GitHub":
        show_github_tool_page(page_header)

Add to sidebar navigation:
    "🐙 GitHub",
"""

import os
import subprocess
import datetime
import threading
import time
from pathlib import Path

import streamlit as st
from dotenv import load_dotenv

load_dotenv(override=True)

TOKEN    = os.getenv("GITHUB_TOKEN", "")
USERNAME = os.getenv("GITHUB_USERNAME", "")

AUTO_SYNC_WATCHERS = {}
AUTO_SYNC_LOCK = threading.Lock()


# ═══════════════════════════════════════════════════════════════════════════
# GitHub client (lazy init)
# ═══════════════════════════════════════════════════════════════════════════

def _env_value(key: str) -> str:
    load_dotenv(override=True)
    return os.getenv(key, "").strip()


def _github_token() -> str:
    return _env_value("GITHUB_TOKEN")


def _github_username() -> str:
    return _env_value("GITHUB_USERNAME") or USERNAME


def _github_auth_message(error: Exception | None = None) -> str:
    detail = f"\n\nGitHub returned: `{error}`" if error else ""
    return (
        "GitHub token is missing or invalid. Create a new token and update `.env`:\n\n"
        "```env\n"
        "GITHUB_TOKEN=your_new_token_here\n"
        "GITHUB_USERNAME=your_github_username\n"
        "```\n\n"
        "For classic tokens, enable the `repo` scope. For fine-grained tokens, give it access "
        "to the repositories you want Chandu AI Lab to manage, with repository read/write permissions."
        f"{detail}"
    )


def _get_github():
    try:
        from github import Github
        return Github(_github_token())
    except ImportError:
        st.error("❌ PyGithub not installed. Run: `pip install PyGithub python-dotenv`")
        st.stop()


def _get_user(stop_on_error=True):
    g = _get_github()
    try:
        return g.get_user()
    except Exception as e:
        if stop_on_error:
            st.error(_github_auth_message(e))
            st.stop()
        raise


# ═══════════════════════════════════════════════════════════════════════════
# Tab 1 — My Repos
# ═══════════════════════════════════════════════════════════════════════════

def tab_my_repos():
    st.markdown("### 👁️ Your Repositories")

    col1, col2, col3 = st.columns([1, 1, 1])
    filter_type     = col1.selectbox("Type", ["all", "public", "private"], key="gh_repos_type")
    sort_by         = col2.selectbox("Sort", ["updated", "created", "pushed", "full_name"], key="gh_repos_sort")
    search_query    = col3.text_input("🔍 Search repos", placeholder="e.g. snake", key="gh_repos_search")

    if st.button("🔄 Load Repos", use_container_width=True, key="gh_repos_load"):
        with st.spinner("Fetching from GitHub..."):
            try:
                user  = _get_user()
                repos = list(user.get_repos(type=filter_type, sort=sort_by))

                if search_query:
                    repos = [r for r in repos
                             if search_query.lower() in r.name.lower()]

                st.session_state["gh_repos"] = repos
                st.success(f"✅ Found {len(repos)} repos")
            except Exception as e:
                st.error(f"Error: {e}")

    repos = st.session_state.get("gh_repos", [])

    if repos:
        for repo in repos:
            private_badge = "🔒" if repo.private else "🌐"
            updated = repo.updated_at.strftime("%Y-%m-%d") if repo.updated_at else "—"

            with st.expander(f"{private_badge} **{repo.name}** — ⭐ {repo.stargazers_count}  •  {updated}"):
                col_a, col_b = st.columns([2, 1])

                with col_a:
                    st.markdown(f"**Description:** {repo.description or '—'}")
                    st.markdown(f"**Language:** `{repo.language or '—'}`")
                    st.markdown(f"**URL:** [{repo.html_url}]({repo.html_url})")
                    st.caption(f"Forks: {repo.forks_count}  •  Watchers: {repo.watchers_count}  •  Size: {repo.size} KB")

                with col_b:
                    # Open in browser
                    st.markdown(
                        f"<a href='{repo.html_url}' target='_blank'>"
                        f"<button style='background:#1a73e8;color:#fff;border:none;"
                        f"border-radius:6px;padding:6px 14px;cursor:pointer;width:100%;'>"
                        f"🌐 Open in Browser</button></a>",
                        unsafe_allow_html=True,
                    )

                    # Clone button
                    clone_path = st.text_input(
                        "Clone to folder",
                        value=f"C:/Users/{_github_username()}/Documents/GitHub",
                        key=f"clone_path_{repo.name}",
                        label_visibility="collapsed",
                    )
                    if st.button("⬇️ Clone", key=f"clone_{repo.name}"):
                        _git_clone(repo.clone_url, clone_path, repo.name)

                    # Browse files
                    if st.button("📂 Browse Files", key=f"browse_{repo.name}"):
                        st.session_state["gh_browse_repo"] = repo.name
                        st.session_state["gh_browse_obj"]  = repo


# ═══════════════════════════════════════════════════════════════════════════
# Tab 2 — Browse Repo Files
# ═══════════════════════════════════════════════════════════════════════════

def tab_browse_files():
    st.markdown("### 📂 Browse Repository Files")

    repos = st.session_state.get("gh_repos", [])
    repo_names = [r.name for r in repos] if repos else []

    if not repo_names:
        st.info("Load your repos first from the **My Repos** tab.")
        return

    selected_name = st.selectbox("Select repo", repo_names, key="gh_browse_selected_repo")
    repo_obj = next((r for r in repos if r.name == selected_name), None)

    branch = st.text_input("Branch", value="main", key="gh_browse_branch")
    path   = st.text_input("Path (leave blank for root)", value="", key="gh_browse_path")

    if st.button("📂 Load Files", use_container_width=True, key="gh_browse_load_files"):
        with st.spinner("Loading files..."):
            try:
                contents = repo_obj.get_contents(path or "", ref=branch)
                st.session_state["gh_contents"] = contents
                st.session_state["gh_repo_obj"] = repo_obj
                st.session_state["gh_branch"]   = branch
            except Exception as e:
                st.error(f"Error: {e}")

    contents = st.session_state.get("gh_contents", [])

    if contents:
        for item in contents:
            icon = "📁" if item.type == "dir" else "📄"
            col1, col2 = st.columns([3, 1])
            col1.markdown(f"{icon} `{item.name}` — {item.size} bytes")

            if item.type == "file":
                if col2.button("👁️ View", key=f"view_{item.sha}"):
                    try:
                        content = item.decoded_content.decode("utf-8", errors="replace")
                        ext = os.path.splitext(item.name)[1].lstrip(".")
                        st.code(content[:3000], language=ext or "text")
                        if len(content) > 3000:
                            st.caption("Showing first 3000 chars")
                    except Exception as e:
                        st.error(f"Cannot decode: {e}")


# ═══════════════════════════════════════════════════════════════════════════
# Tab 3 — Git Commands
# ═══════════════════════════════════════════════════════════════════════════

def tab_git_commands():
    st.markdown("### 🖥️ Git Terminal")
    st.caption("Run git commands on your local repos.")

    repo_path = st.text_input(
        "Local repo path",
        value=f"C:/Users/{_github_username()}/Documents/GitHub",
        placeholder="e.g. C:/Users/chandrajit/Documents/GitHub/myrepo",
        key="gh_terminal_repo_path",
    )

    # Quick command buttons
    st.markdown("**⚡ Quick Commands**")
    qc1, qc2, qc3, qc4, qc5 = st.columns(5)

    quick_cmd = None
    if qc1.button("📊 Status", key="gh_qc_status"):    quick_cmd = "git status"
    if qc2.button("📜 Log", key="gh_qc_log"):          quick_cmd = "git log --oneline -10"
    if qc3.button("⬇️ Pull", key="gh_qc_pull"):        quick_cmd = "git pull"
    if qc4.button("📤 Push", key="gh_qc_push"):        quick_cmd = "git push"
    if qc5.button("🌿 Branches", key="gh_qc_branches"): quick_cmd = "git branch -a"

    st.markdown("**📝 Custom Command**")
    custom_cmd = st.text_input(
        "Command",
        value=quick_cmd or "git status",
        placeholder="git status / git log / git pull ...",
        label_visibility="collapsed",
        key="gh_terminal_command",
    )

    # Commit helper
    with st.expander("📦 Quick Commit + Push"):
        commit_msg = st.text_input("Commit message", placeholder="e.g. fix: updated snake game", key="gh_terminal_commit_msg")
        if st.button("🚀 Add → Commit → Push", use_container_width=True, key="gh_terminal_commit_push"):
            if commit_msg.strip():
                cmds = [
                    "git add .",
                    f'git commit -m "{commit_msg}"',
                    "git push",
                ]
                for cmd in cmds:
                    result = _run_git(cmd, repo_path)
                    st.markdown(f"`{cmd}`")
                    if result["success"]:
                        st.success(result["output"] or "✅ Done")
                    else:
                        st.error(result["output"])
                        break
            else:
                st.warning("Enter a commit message.")

    if st.button("▶ Run Command", use_container_width=True, key="gh_terminal_run"):
        if custom_cmd.strip():
            result = _run_git(custom_cmd, repo_path)
            st.markdown("**Output:**")
            if result["success"]:
                st.code(result["output"] or "✅ Command completed (no output)", language="text")
            else:
                st.error("Command failed:")
                st.code(result["output"], language="text")


def tab_auto_sync():
    st.markdown("### Auto Commit + Push")
    st.caption("Watch a local git repo and push a new commit whenever files change.")

    default_path = f"C:/Users/{_github_username()}/Documents/GitHub"
    repo_path = st.text_input(
        "Local repo path",
        value=st.session_state.get("gh_auto_sync_path", default_path),
        placeholder="e.g. C:/Users/chandrajit/Documents/GitHub/myrepo",
        key="gh_auto_sync_path",
    )

    normalized_path = ""
    is_repo = False
    if repo_path.strip() and os.path.isdir(repo_path):
        try:
            normalized_path = _normalize_repo_path(repo_path)
            is_repo, _ = _is_git_repo(normalized_path)
        except Exception:
            normalized_path = ""

    remotes = _remote_names(normalized_path) if is_repo else ["origin"]
    branch_default = _current_branch(normalized_path) if is_repo else "main"

    col1, col2, col3 = st.columns([1, 1, 1])
    remote = col1.selectbox("Remote", remotes, index=0, key="gh_auto_remote")
    branch = col2.text_input("Branch", value=branch_default, key="gh_auto_branch")
    interval = col3.number_input("Check every seconds", min_value=10, max_value=3600, value=60, step=10, key="gh_auto_interval")
    prefix = st.text_input("Commit prefix", value="auto", placeholder="auto / backup / sync", key="gh_auto_prefix")

    st.info(
        "This uses your repo's configured git remote. Make sure `git push` works in this folder first, "
        "and keep generated or secret files out with `.gitignore`."
    )

    start_col, stop_col, once_col = st.columns(3)
    if start_col.button("Start Auto Sync", use_container_width=True, key="gh_auto_start"):
        ok, message = _start_auto_sync(repo_path, remote, branch, prefix, int(interval))
        if ok:
            st.success(message)
        else:
            st.error(message)

    if stop_col.button("Stop Auto Sync", use_container_width=True, key="gh_auto_stop"):
        ok, message = _stop_auto_sync(repo_path)
        if ok:
            st.success(message)
        else:
            st.warning(message)

    if once_col.button("Sync Once Now", use_container_width=True, key="gh_auto_once"):
        try:
            path = _normalize_repo_path(repo_path)
            ok, message = _is_git_repo(path)
            if not ok:
                st.error(message)
            else:
                result = _auto_commit_push_once(path, remote, branch, prefix)
                if result["success"]:
                    st.success(result["output"])
                else:
                    st.error(result["output"])
        except Exception as e:
            st.error(str(e))

    st.divider()
    st.markdown("**Running watchers**")
    with AUTO_SYNC_LOCK:
        watchers = list(AUTO_SYNC_WATCHERS.values())

    active_watchers = [watcher for watcher in watchers if watcher["running"]]
    if not active_watchers:
        st.caption("No auto sync watcher is running.")
        return

    for watcher in active_watchers:
        status_icon = "OK" if watcher["last_success"] else "ERROR"
        with st.expander(f"{status_icon} {watcher['repo_path']}"):
            st.markdown(f"**Remote:** `{watcher['remote']}`")
            st.markdown(f"**Branch:** `{watcher['branch'] or '(default)'}`")
            st.markdown(f"**Interval:** `{watcher['interval']}s`")
            st.markdown(f"**Last checked:** `{watcher['last_checked']}`")
            st.markdown(f"**Successful syncs:** `{watcher['sync_count']}`")
            if watcher["last_result"]:
                st.code(watcher["last_result"], language="text")


def _run_git(cmd: str, cwd: str) -> dict:
    try:
        result = subprocess.run(
            cmd, shell=True, cwd=cwd,
            capture_output=True, text=True, timeout=30,
        )
        output = (result.stdout + result.stderr).strip()
        return {"success": result.returncode == 0, "output": output}
    except subprocess.TimeoutExpired:
        return {"success": False, "output": "⏱ Timed out"}
    except Exception as e:
        return {"success": False, "output": str(e)}


def _run_git_args(args, cwd: str, timeout: int = 60) -> dict:
    try:
        result = subprocess.run(
            ["git", *args],
            shell=False,
            cwd=cwd,
            capture_output=True,
            text=True,
            timeout=timeout,
        )
        output = (result.stdout + result.stderr).strip()
        return {"success": result.returncode == 0, "output": output}
    except subprocess.TimeoutExpired:
        return {"success": False, "output": "Timed out"}
    except FileNotFoundError:
        return {"success": False, "output": "Git is not installed or not available in PATH."}
    except Exception as e:
        return {"success": False, "output": str(e)}


def _normalize_repo_path(repo_path: str) -> str:
    return str(Path(repo_path).expanduser().resolve())


def _is_git_repo(repo_path: str) -> tuple[bool, str]:
    if not repo_path.strip():
        return False, "Enter a local repository path."
    if not os.path.isdir(repo_path):
        return False, "Folder does not exist."

    result = _run_git_args(["rev-parse", "--is-inside-work-tree"], repo_path)
    if result["success"] and result["output"].splitlines()[-1].strip() == "true":
        return True, ""
    return False, result["output"] or "This folder is not a git repository."


def _current_branch(repo_path: str) -> str:
    result = _run_git_args(["branch", "--show-current"], repo_path)
    if result["success"] and result["output"].strip():
        return result["output"].strip()
    return "main"


def _remote_names(repo_path: str) -> list[str]:
    result = _run_git_args(["remote"], repo_path)
    if not result["success"] or not result["output"].strip():
        return ["origin"]
    return [line.strip() for line in result["output"].splitlines() if line.strip()] or ["origin"]


def _auto_commit_push_once(repo_path: str, remote: str, branch: str, prefix: str) -> dict:
    status = _run_git_args(["status", "--porcelain"], repo_path)
    if not status["success"]:
        return {"success": False, "output": status["output"]}
    if not status["output"].strip():
        return {"success": True, "output": "No changes found.", "changed": False}

    add_result = _run_git_args(["add", "-A"], repo_path)
    if not add_result["success"]:
        return {"success": False, "output": add_result["output"]}

    staged = _run_git_args(["diff", "--cached", "--name-only"], repo_path)
    changed_files = len([line for line in staged["output"].splitlines() if line.strip()]) if staged["success"] else 0
    timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    message = f"{prefix.strip() or 'auto'}: sync local changes {timestamp}"

    commit_result = _run_git_args(["commit", "-m", message], repo_path)
    if not commit_result["success"]:
        if "nothing to commit" in commit_result["output"].lower():
            return {"success": True, "output": "No staged changes to commit.", "changed": False}
        return {"success": False, "output": commit_result["output"]}

    push_args = ["push", remote.strip() or "origin"]
    if branch.strip():
        push_args.append(branch.strip())
    push_result = _run_git_args(push_args, repo_path, timeout=120)
    if not push_result["success"]:
        return {"success": False, "output": f"Committed locally, but push failed:\n{push_result['output']}"}

    return {
        "success": True,
        "output": f"Committed and pushed {changed_files} file(s): {message}",
        "changed": True,
    }


def _watcher_loop(key: str, repo_path: str, remote: str, branch: str, prefix: str, interval: int):
    while True:
        with AUTO_SYNC_LOCK:
            watcher = AUTO_SYNC_WATCHERS.get(key)
            if not watcher or not watcher["running"]:
                return

        result = _auto_commit_push_once(repo_path, remote, branch, prefix)
        with AUTO_SYNC_LOCK:
            watcher = AUTO_SYNC_WATCHERS.get(key)
            if not watcher:
                return
            watcher["last_checked"] = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            watcher["last_result"] = result["output"]
            watcher["last_success"] = result["success"]
            if result.get("changed"):
                watcher["sync_count"] += 1

        time.sleep(max(10, int(interval)))


def _start_auto_sync(repo_path: str, remote: str, branch: str, prefix: str, interval: int) -> tuple[bool, str]:
    try:
        normalized_path = _normalize_repo_path(repo_path)
    except Exception as e:
        return False, str(e)

    is_repo, message = _is_git_repo(normalized_path)
    if not is_repo:
        return False, message

    key = normalized_path.lower()
    with AUTO_SYNC_LOCK:
        existing = AUTO_SYNC_WATCHERS.get(key)
        if existing and existing["running"]:
            return True, "Auto sync is already running for this repository."

        AUTO_SYNC_WATCHERS[key] = {
            "repo_path": normalized_path,
            "remote": remote.strip() or "origin",
            "branch": branch.strip(),
            "prefix": prefix.strip() or "auto",
            "interval": max(10, int(interval)),
            "running": True,
            "last_checked": "Waiting for first scan...",
            "last_result": "",
            "last_success": True,
            "sync_count": 0,
        }

    thread = threading.Thread(
        target=_watcher_loop,
        args=(key, normalized_path, remote, branch, prefix, interval),
        daemon=True,
    )
    AUTO_SYNC_WATCHERS[key]["thread"] = thread
    thread.start()
    return True, "Auto sync started."


def _stop_auto_sync(repo_path: str) -> tuple[bool, str]:
    try:
        key = _normalize_repo_path(repo_path).lower()
    except Exception as e:
        return False, str(e)

    with AUTO_SYNC_LOCK:
        watcher = AUTO_SYNC_WATCHERS.get(key)
        if not watcher:
            return False, "Auto sync is not running for this repository."
        watcher["running"] = False
    return True, "Auto sync stopped."


def _git_clone(clone_url: str, folder: str, repo_name: str):
    # Inject token into URL for private repos
    token = _github_token()
    if token:
        clone_url = clone_url.replace("https://", f"https://{token}@")
    result = _run_git(f"git clone {clone_url}", folder)
    if result["success"]:
        st.success(f"✅ Cloned to `{folder}/{repo_name}`")
    else:
        st.error(f"Clone failed: {result['output']}")


# ═══════════════════════════════════════════════════════════════════════════
# Tab 4 — Create Repo
# ═══════════════════════════════════════════════════════════════════════════

def tab_create_repo():
    st.markdown("### ➕ Create New Repository")

    name        = st.text_input("Repo name", placeholder="e.g. chandu-ai-lab", key="gh_create_name")
    description = st.text_input("Description", placeholder="e.g. My personal AI OS", key="gh_create_description")
    private     = st.checkbox("🔒 Private repo", value=True, key="gh_create_private")
    auto_init   = st.checkbox("📄 Initialize with README", value=True, key="gh_create_auto_init")

    if st.button("🚀 Create Repo on GitHub", use_container_width=True, key="gh_create_submit"):
        if not name.strip():
            st.warning("Enter a repo name.")
            return
        with st.spinner("Creating..."):
            try:
                user = _get_user()
                repo = user.create_repo(
                    name=name.strip(),
                    description=description.strip(),
                    private=private,
                    auto_init=auto_init,
                )
                st.success(f"✅ Created: [{repo.html_url}]({repo.html_url})")
                st.balloons()
            except Exception as e:
                st.error(f"Failed: {e}")


# ═══════════════════════════════════════════════════════════════════════════
# Tab 5 — Profile
# ═══════════════════════════════════════════════════════════════════════════

def tab_profile():
    st.markdown("### 👤 GitHub Profile")

    if st.button("Load Profile", use_container_width=True, key="gh_profile_load"):
        with st.spinner("Loading..."):
            try:
                user = _get_user()

                col1, col2 = st.columns([1, 2])
                col1.image(user.avatar_url, width=120)
                col2.markdown(f"## {user.name or user.login}")
                col2.markdown(f"**@{user.login}**")
                col2.markdown(f"📍 {user.location or '—'}")
                col2.markdown(f"🔗 [{user.html_url}]({user.html_url})")

                st.divider()

                m1, m2, m3, m4 = st.columns(4)
                m1.metric("Public Repos",   user.public_repos)
                m2.metric("Followers",      user.followers)
                m3.metric("Following",      user.following)
                m4.metric("Public Gists",   user.public_gists)

                if user.bio:
                    st.info(f"💬 {user.bio}")

            except Exception as e:
                st.error(f"Error: {e}")


# ═══════════════════════════════════════════════════════════════════════════
# Main page
# ═══════════════════════════════════════════════════════════════════════════

def show_github_tool_page(page_header):
    page_header(
        "🐙", "GitHub",
        "Manage your repos, browse files, run git commands — all from AI Lab"
    )

    token = _github_token()
    if not token:
        st.error(_github_auth_message())
        return

    try:
        user = _get_user(stop_on_error=False)
    except Exception as e:
        st.error(_github_auth_message(e))
        return

    st.success(f"✅ Connected as **{user.login}**")
    st.divider()

    tab1, tab2, tab3, tab4, tab5, tab6 = st.tabs([
        "👁️ My Repos",
        "📂 Browse Files",
        "🖥️ Git Terminal",
        "Auto Sync",
        "➕ Create Repo",
        "👤 Profile",
    ])

    with tab1: tab_my_repos()
    with tab2: tab_browse_files()
    with tab3: tab_git_commands()
    with tab4: tab_auto_sync()
    with tab5: tab_create_repo()
    with tab6: tab_profile()
