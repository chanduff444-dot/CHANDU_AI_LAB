import os
import streamlit as st
import pandas as pd
from langchain_ollama import OllamaLLM

# ── Theme ─────────────────────────────────────────────────────
from style import apply_theme, page_header, stat_card

# ── Core Engines ──────────────────────────────────────────────
from core.orchestrator import MasterOrchestrator
from core.guidance_engine import generate_guidance
from core.project_engine import load_project
from core.analytics import load_logs, compute_stats, compute_scores
from core.skill_map import generate_skill_diagnostics, load_skills
from core.agent_engine import AgentEngine
from core.escalation import escalate_response

# ── Experiment Tracking ───────────────────────────────────────
from chandu_lab.experiment_tracker import (
    log_experiment,
    list_experiments,
    analyze_experiments,
)

# ── PDF Ingestion ─────────────────────────────────────────────
from ingestion.pdf_ingest import ingest_pdf

# ── Physics Page ──────────────────────────────────────────────
from physics_page import show_physics_page
from game_lab_page import show_game_lab_page
from nn_visualiser import show_nn_visualiser_page
from system_dashboard import show_system_dashboard_page
from tool_system import show_tool_system_page
from github_tool import show_github_tool_page
from ai_file_assistant import show_ai_file_assistant_page
from floating_assistant import inject_floating_assistant
from neocortex_page import show_neocortex_page
# ✅ TO THIS
from style import apply_theme, page_header, stat_card
# ═════════════════════════════════════════════════════════════
# CONSTANTS
# ═════════════════════════════════════════════════════════════

MODEL_MAP = {
    "deepseek-coder:6.7b (Apps 🚀)": "deepseek-coder:6.7b",
    "mistral:latest (Fast ⚡)":       "mistral:latest",
    "llama3:latest (Balanced 🧠)":    "llama3:latest",
    "qwen3:14b (Powerful 💪)":        "qwen3:14b",
}

CODE_KEYWORDS = {
    "code", "python", "function", "class", "script",
    "implement", "write", "build", "create", "program",
}


# ═════════════════════════════════════════════════════════════
# HELPERS
# ═════════════════════════════════════════════════════════════

def is_code_request(text: str) -> bool:
    action_words = {"write", "build", "create", "implement", "generate", "make"}
    words = set(text.lower().split())
    return bool(words & action_words) and bool(words & CODE_KEYWORDS)


def call_llm(model: str, prompt: str) -> str:
    try:
        llm = OllamaLLM(model=model)
        return llm.invoke(prompt)
    except Exception as e:
        return f"❌ LLM Error ({model}): {e}"


def code_mode_llm(user_input: str, model: str = "codellama:34b") -> str:
    prompt = f"""You are an expert programmer.

Rules:
- Only return code
- No explanation
- Proper indentation
- Complete working code

Task:
{user_input}
"""
    return call_llm(model, prompt)


def evaluate_code(code: str, model: str) -> str:
    prompt = f"""Analyze this web app.

Return SHORT bullet points:
- UI issues
- Bugs
- Missing features

Code:
{code[:3000]}
"""
    return call_llm(model, prompt)


def improve_code(code: str, issues: str, model: str) -> str:
    prompt = f"""You are a frontend developer.

STRICT RULE:
- Return ONLY full HTML code
- NO explanation, NO text, NO comments outside code

Fix and improve this app based on these issues:
{issues}

Code:
{code[:4000]}
"""
    return call_llm(model, prompt)


def extract_html(code: str) -> str:
    lower = code.lower()
    start = lower.find("<!doctype html")
    if start == -1:
        start = lower.find("<html")
    return code[start:] if start != -1 else code


def agent_improve_loop(code: str, model: str, steps: int = 2) -> str:
    for i in range(steps):
        st.markdown(f"#### 🔍 Improvement Step {i + 1}")
        with st.spinner("Evaluating..."):
            issues = evaluate_code(code, model)
        st.code(issues)
        if "no issues" in issues.lower():
            st.success("No issues found — stopping early.")
            break
        with st.spinner(f"Improving (step {i + 1})..."):
            code = improve_code(code, issues, model)
    return code


# ═════════════════════════════════════════════════════════════
# PAGE CONFIG
# ═════════════════════════════════════════════════════════════

st.set_page_config(
    page_title="Chandu AI Lab",
    page_icon="🧠",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ── Splash Screen ─────────────────────────────────────────────
from splash import show_splash
show_splash()

# ── Apply theme ───────────────────────────────────────────────
apply_theme()

# ── Sidebar reopen button ─────────────────────────────────────
st.components.v1.html("""
<div id="openBtn" style="
    position: fixed;
    left: 0;
    top: 50vh;
    transform: translateY(-50%);
    z-index: 99999;
    background: #1a73e8;
    color: white;
    width: 28px;
    height: 56px;
    display: flex;
    align-items: center;
    justify-content: center;
    border-radius: 0 8px 8px 0;
    cursor: pointer;
    font-size: 22px;
    box-shadow: 3px 0 12px rgba(26,115,232,0.6);
    user-select: none;
">›</div>
<script>
document.getElementById('openBtn').addEventListener('click', function() {
    var p = window.parent.document;
    var selectors = [
        '[data-testid="collapsedControl"]',
        '[data-testid="stSidebarCollapsedControl"]',
        'button[kind="header"]',
        'section[data-testid="stSidebar"] + div button'
    ];
    selectors.forEach(function(sel) {
        p.querySelectorAll(sel).forEach(function(b) { b.click(); });
    });
});
</script>
""", height=60)
# ── Global orchestrator ───────────────────────────────────────
if "orchestrator" not in st.session_state:
    st.session_state.orchestrator = MasterOrchestrator()

orchestrator: MasterOrchestrator = st.session_state.orchestrator


# ═════════════════════════════════════════════════════════════
# SIDEBAR
# ═════════════════════════════════════════════════════════════
page_name = st.session_state.get("page", "Brain")
with st.sidebar:

    # ── Logo ──────────────────────────────────────────────────
    st.markdown("""
    <div style="
        display: flex;
        align-items: center;
        gap: 10px;
        padding: 0.25rem 0 1rem 0;
        border-bottom: 1px solid #2a2a2a;
        margin-bottom: 1.25rem;
    ">
        <div style="
            width: 36px; height: 36px;
            background: linear-gradient(135deg, #1a73e8, #00897b);
            border-radius: 10px;
            display: flex; align-items: center; justify-content: center;
            font-size: 1.1rem;
            flex-shrink: 0;
            box-shadow: 0 2px 8px rgba(26,115,232,0.3);
        ">⬡</div>
        <div>
            <div style="
                font-family: 'DM Sans', sans-serif;
                font-size: 1rem;
                font-weight: 700;
                color: #e8eaed;
                letter-spacing: -0.3px;
                line-height: 1.2;
            ">Chandu AI Lab</div>
            <div style="
                font-size: 0.68rem;
                color: #9aa0a6;
                font-weight: 400;
                letter-spacing: 0.3px;
            ">Personal AI Operating System</div>
        </div>
    </div>
    """, unsafe_allow_html=True)
    # ── Active Project ─────────────────────────────────────────
    project = load_project()
    if project:
        st.markdown("**📁 Active Project**")
        st.markdown(f"`{project['name']}`")
        st.caption(project["goal"])

        total     = len(project["milestones"])
        completed = sum(1 for m in project["milestones"] if m["completed"])
        progress  = int((completed / total) * 100) if total else 0

        st.progress(progress)
        st.caption(f"{completed}/{total} milestones")
        st.markdown("---")

    # ── System Metrics ─────────────────────────────────────────
    logs = load_logs()
    if logs:
        stats  = compute_stats(logs)
        scores = compute_scores(stats)

        col1, col2 = st.columns(2)
        col1.metric("⚡ CSI",   scores["csi"])
        col2.metric("🧠 Depth", scores["depth_score"])

        skills = load_skills()
        if skills:
            weakest = min(skills.items(), key=lambda x: x[1]["mastery_score"])
            st.markdown("**🎯 Weakest Skill**")
            st.caption(f"{weakest[0]}  ·  {round(weakest[1]['mastery_score'], 2)}")

        st.caption(f"📊 {len(logs)} interactions logged")

        csi = scores["csi"]
        if csi >= 7:
            st.success("System: Strong 🟢")
        elif csi >= 4:
            st.warning("System: Developing 🟡")
        else:
            st.error("System: Needs Focus 🔴")
    else:
        st.info("No data yet — start chatting!")

    # ── Proactive Guidance ─────────────────────────────────────
    guidance = generate_guidance()
    if guidance:
        st.markdown("---")
        st.markdown("**🧠 Suggestion**")
        st.warning(guidance)

    st.markdown("---")

    # ── Navigation ─────────────────────────────────────────────
    page = st.selectbox(
    "Navigate",
    [
        "🧠 Brain",
        "🤖 Builder",
        "📚 Knowledge",
        "🧪 Experiments",
        "📊 Dashboard",
        "NC Neocortex",
        "⚛ Physics",
        "🎮 Game Lab",
        "🧠 Neural Network Visualiser",
        "🖥️ System Dashboard",
        "🛠️ Tool System",
        "🐙 GitHub",  
        "🤖 AI File Assistant", 
             # ✅ ADD THIS
    ],
)
# Strip emoji prefix for comparisons
page_name = page.split(" ", 1)[1]
# ADD THIS RIGHT HERE ↓
inject_floating_assistant(model="gemma3:latest", current_page=page_name)


# ═════════════════════════════════════════════════════════════
# PAGE: BRAIN
# ═════════════════════════════════════════════════════════════

if page_name == "Brain":
    page_header("🧠", "Hybrid Brain", "Auto-routing between code, chat, and retrieval")

    creator_mode = st.checkbox("🛠 Creator Mode — full technical detail")

    if "messages" not in st.session_state:
        st.session_state.messages = []

    for msg in st.session_state.messages:
        with st.chat_message(msg["role"]):
            st.markdown(msg["content"])

    user_input = st.chat_input("Ask your AI Lab...")

    if user_input:
        st.session_state.messages.append({"role": "user", "content": user_input})
        with st.chat_message("user"):
            st.markdown(user_input)

        with st.chat_message("assistant"):
            with st.spinner("Thinking..."):
                if is_code_request(user_input):
                    response      = code_mode_llm(user_input)
                    response_type = "code"
                else:
                    try:
                        result        = orchestrator.process(user_input, creator_mode=creator_mode)
                        response      = result["response"]
                        response_type = result.get("type", "chat")
                    except Exception as e:
                        response      = f"❌ Orchestrator error: {e}"
                        response_type = "error"

            if response_type == "code":
                st.code(response, language="python")
            elif response_type == "error":
                st.error(response)
            else:
                response = escalate_response(response, user_input, mode="Chat")
                st.markdown(response)

        st.session_state.messages.append({"role": "assistant", "content": response})


# ═════════════════════════════════════════════════════════════
# PAGE: BUILDER
# ═════════════════════════════════════════════════════════════

elif page_name == "Builder":
    page_header("🤖", "Builder Mode", "Generate, preview, and download real applications")

    model_choice   = st.selectbox("Model", list(MODEL_MAP.keys()))
    selected_model = MODEL_MAP[model_choice]

    col1, col2, col3 = st.columns([2, 1, 1])
    with col1:
        auto_improve = st.checkbox("🔥 Auto-Improve (agent loop)")
    with col2:
        steps   = st.slider("Max Steps", 1, 10, 3)
    with col3:
        retries = st.slider("Retries",   0,  3, 1)

    user_input = st.text_input(
        "Describe the app you want to build",
        placeholder="e.g. A todo list with dark mode and local storage"
    )

    if "agent_logs" not in st.session_state:
        st.session_state.agent_logs = []

    if st.button("▶ Run Agent") and user_input.strip():
        agent = AgentEngine(orchestrator, model=selected_model)

        with st.spinner("Agent working..."):
            try:
                result       = agent.run(user_input, max_steps=steps, retries=retries)
                final_output = result["final"]
                logs         = result["steps"]
            except Exception as e:
                st.error(f"Agent error: {e}")
                st.stop()

        st.session_state.agent_logs = logs

        if auto_improve:
            st.markdown("### 🔄 Auto-Improvement Loop")
            final_output = agent_improve_loop(final_output, selected_model, steps=steps)

        final_output = extract_html(final_output)
        is_html = "<html" in final_output.lower() or "<!doctype html" in final_output.lower()

        st.markdown("---")
        st.subheader("✅ Live Preview")

        if is_html:
            st.components.v1.html(final_output, height=520, scrolling=True)
            st.divider()
            with st.expander("💻 View Source Code"):
                st.code(final_output, language="html")
            st.download_button(
                "⬇️ Download HTML",
                data=final_output,
                file_name="app.html",
                mime="text/html",
            )
        else:
            st.code(final_output, language="python")

    if st.session_state.agent_logs:
        with st.sidebar:
            st.markdown("---")
            st.markdown("**🧪 Agent Steps**")
            for step in st.session_state.agent_logs:
                with st.expander(f"Step {step['step']} · {step['type']}"):
                    st.code(step["output"])


# ═════════════════════════════════════════════════════════════
# PAGE: KNOWLEDGE
# ═════════════════════════════════════════════════════════════

elif page_name == "Knowledge":
    page_header("📚", "Knowledge Base", "Upload PDFs to expand Chandu's memory")

    uploaded_file = st.file_uploader("Drop a PDF here", type=["pdf"])

    if uploaded_file is not None:
        os.makedirs("datasets", exist_ok=True)
        save_path = os.path.join("datasets", uploaded_file.name)

        with open(save_path, "wb") as f:
            f.write(uploaded_file.getbuffer())

        st.info(f"Saved `{uploaded_file.name}`. Ingesting into memory...")

        with st.spinner("Embedding and storing..."):
            try:
                ingest_pdf(save_path)
                st.success("✅ PDF successfully ingested into Chandu Memory.")
            except Exception as e:
                st.error(f"Ingestion failed: {e}")


# ═════════════════════════════════════════════════════════════
# PAGE: EXPERIMENTS
# ═════════════════════════════════════════════════════════════

elif page_name == "Experiments":
    page_header("🧪", "Experiment Lab", "Track, compare, and analyze your model runs")

    st.subheader("Log New Experiment")

    with st.form("experiment_form"):
        c1, c2   = st.columns(2)
        name     = c1.text_input("Project Name")
        model    = c2.text_input("Model Name")
        dataset  = st.text_input("Dataset Used")
        c3, c4   = st.columns(2)
        accuracy = c3.number_input("Accuracy", step=0.01, format="%.4f")
        loss     = c4.number_input("Loss",     step=0.01, format="%.4f")
        notes    = st.text_area("Notes", height=80)
        submitted = st.form_submit_button("➕ Log Experiment")

    if submitted:
        if not name or not model:
            st.warning("Please fill in at least Project Name and Model Name.")
        else:
            st.success(log_experiment(name, model, dataset, accuracy, loss, notes))

    st.divider()

    experiments = list_experiments()

    if experiments:
        df = pd.DataFrame(experiments)

        st.subheader("📋 Experiment History")
        st.dataframe(df, use_container_width=True)

        st.divider()

        col_a, col_b = st.columns(2)
        with col_a:
            st.subheader("📈 Accuracy")
            if "accuracy" in df.columns:
                st.line_chart(df["accuracy"])
        with col_b:
            st.subheader("📉 Loss")
            if "loss" in df.columns:
                st.line_chart(df["loss"])

        st.divider()
        st.subheader("🏆 Best Performance")

        best_acc    = df.loc[df["accuracy"].idxmax()]
        lowest_loss = df.loc[df["loss"].idxmin()]

        r1, r2 = st.columns(2)
        r1.success(f"Best Accuracy: **{best_acc['accuracy']}** — {best_acc['name']}")
        r2.success(f"Lowest Loss: **{lowest_loss['loss']}** — {lowest_loss['name']}")

        st.divider()
        if st.button("🧠 Analyze Experiments"):
            with st.spinner("Analyzing..."):
                try:
                    st.write(analyze_experiments())
                except Exception as e:
                    st.error(f"Analysis failed: {e}")
    else:
        st.info("No experiments yet — log your first run above.")


# ═════════════════════════════════════════════════════════════
# PAGE: DASHBOARD
# ═════════════════════════════════════════════════════════════

elif page_name == "Dashboard":
    page_header("📊", "Intelligence Dashboard", "Your cognitive performance at a glance")

    logs = load_logs()

    if logs:
        stats  = compute_stats(logs)
        scores = compute_scores(stats)

        c1, c2, c3, c4 = st.columns(4)
        with c1: stat_card("CSI",       scores["csi"])
        with c2: stat_card("Depth",     scores["depth_score"],     color="#7c4dff")
        with c3: stat_card("Balance",   scores["balance_score"],   color="#00897b")
        with c4: stat_card("Ownership", scores["ownership_score"], color="#f29900")

        st.divider()
        st.subheader("📊 Behavioral Ratios")

        ratio_data = {
            "Code":      stats["code_ratio"],
            "Theory":    stats["theory_ratio"],
            "Retrieval": stats["retrieval_ratio"],
            "Depth":     stats["depth_ratio"],
        }
        st.bar_chart(ratio_data)

    else:
        st.info("No interaction data yet — start using the Brain page.")

    st.divider()

    if st.button("🧠 Show Skill Diagnostics"):
        with st.spinner("Generating diagnostics..."):
            try:
                skill_data = generate_skill_diagnostics()
                st.subheader("🧠 Skill Diagnostics")
                st.text(skill_data)
            except Exception as e:
                st.error(f"Diagnostics failed: {e}")


# ═════════════════════════════════════════════════════════════
# PAGE: PHYSICS
# ═════════════════════════════════════════════════════════════

elif page_name == "Neocortex":
    show_neocortex_page(page_header, MODEL_MAP)

elif page_name == "Physics":
    show_physics_page(page_header, MODEL_MAP)

# ═════════════════════════════════════════════════════════════
# PAGE: GAME LAB
# ═════════════════════════════════════════════════════════════

elif page_name == "Game Lab":
    show_game_lab_page(page_header)

elif page_name == "Neural Network Visualiser":
    show_nn_visualiser_page(page_header)
    
elif page_name == "System Dashboard":
    show_system_dashboard_page(page_header)
elif page_name == "Tool System":
    show_tool_system_page(page_header)
elif page_name == "GitHub":
    show_github_tool_page(page_header)
elif page_name == "AI File Assistant":
    show_ai_file_assistant_page(page_header)
