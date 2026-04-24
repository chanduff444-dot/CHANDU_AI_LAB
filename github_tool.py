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

import streamlit as st
from dotenv import load_dotenv

load_dotenv()

TOKEN    = os.getenv("GITHUB_TOKEN", "")
USERNAME = os.getenv("GITHUB_USERNAME", "")


# ═══════════════════════════════════════════════════════════════════════════
# GitHub client (lazy init)
# ═══════════════════════════════════════════════════════════════════════════

def _get_github():
    try:
        from github import Github
        return Github(TOKEN)
    except ImportError:
        st.error("❌ PyGithub not installed. Run: `pip install PyGithub python-dotenv`")
        st.stop()


def _get_user():
    g = _get_github()
    try:
        return g.get_user()
    except Exception as e:
        st.error(f"❌ GitHub auth failed: {e}\nCheck your token in `.env`")
        st.stop()


# ═══════════════════════════════════════════════════════════════════════════
# Tab 1 — My Repos
# ═══════════════════════════════════════════════════════════════════════════

def tab_my_repos():
    st.markdown("### 👁️ Your Repositories")

    col1, col2, col3 = st.columns([1, 1, 1])
    filter_type     = col1.selectbox("Type", ["all", "public", "private"])
    sort_by         = col2.selectbox("Sort", ["updated", "created", "pushed", "full_name"])
    search_query    = col3.text_input("🔍 Search repos", placeholder="e.g. snake")

    if st.button("🔄 Load Repos", use_container_width=True):
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
                        value=f"C:/Users/{USERNAME}/Documents/GitHub",
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

    selected_name = st.selectbox("Select repo", repo_names)
    repo_obj = next((r for r in repos if r.name == selected_name), None)

    branch = st.text_input("Branch", value="main")
    path   = st.text_input("Path (leave blank for root)", value="")

    if st.button("📂 Load Files", use_container_width=True):
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
        value=f"C:/Users/{USERNAME}/Documents/GitHub",
        placeholder="e.g. C:/Users/chandrajit/Documents/GitHub/myrepo",
    )

    # Quick command buttons
    st.markdown("**⚡ Quick Commands**")
    qc1, qc2, qc3, qc4, qc5 = st.columns(5)

    quick_cmd = None
    if qc1.button("📊 Status"):    quick_cmd = "git status"
    if qc2.button("📜 Log"):       quick_cmd = "git log --oneline -10"
    if qc3.button("⬇️ Pull"):      quick_cmd = "git pull"
    if qc4.button("📤 Push"):      quick_cmd = "git push"
    if qc5.button("🌿 Branches"):  quick_cmd = "git branch -a"

    st.markdown("**📝 Custom Command**")
    custom_cmd = st.text_input(
        "Command",
        value=quick_cmd or "git status",
        placeholder="git status / git log / git pull ...",
        label_visibility="collapsed",
    )

    # Commit helper
    with st.expander("📦 Quick Commit + Push"):
        commit_msg = st.text_input("Commit message", placeholder="e.g. fix: updated snake game")
        if st.button("🚀 Add → Commit → Push", use_container_width=True):
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

    if st.button("▶ Run Command", use_container_width=True):
        if custom_cmd.strip():
            result = _run_git(custom_cmd, repo_path)
            st.markdown("**Output:**")
            if result["success"]:
                st.code(result["output"] or "✅ Command completed (no output)", language="text")
            else:
                st.error("Command failed:")
                st.code(result["output"], language="text")


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


def _git_clone(clone_url: str, folder: str, repo_name: str):
    # Inject token into URL for private repos
    if TOKEN:
        clone_url = clone_url.replace("https://", f"https://{TOKEN}@")
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

    name        = st.text_input("Repo name", placeholder="e.g. chandu-ai-lab")
    description = st.text_input("Description", placeholder="e.g. My personal AI OS")
    private     = st.checkbox("🔒 Private repo", value=True)
    auto_init   = st.checkbox("📄 Initialize with README", value=True)

    if st.button("🚀 Create Repo on GitHub", use_container_width=True):
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

    if st.button("Load Profile", use_container_width=True):
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

    # Token check
    if not TOKEN:
        st.error(
            "❌ No GitHub token found.\n\n"
            "Create a `.env` file in your CHANDU_CORE folder with:\n"
            "```\nGITHUB_TOKEN=ghp_yourtoken\nGITHUB_USERNAME=yourusername\n```"
        )
        return

    st.success(f"✅ Connected as **{USERNAME}**")
    st.divider()

    tab1, tab2, tab3, tab4, tab5 = st.tabs([
        "👁️ My Repos",
        "📂 Browse Files",
        "🖥️ Git Terminal",
        "➕ Create Repo",
        "👤 Profile",
    ])

    with tab1: tab_my_repos()
    with tab2: tab_browse_files()
    with tab3: tab_git_commands()
    with tab4: tab_create_repo()
    with tab5: tab_profile()