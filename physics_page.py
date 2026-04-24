"""
physics_page.py  —  drop this in your project root
Add to app.py navigation: "⚛ Physics"
Then add the page block at the bottom of app.py.
"""

import streamlit as st
from langchain_ollama import OllamaLLM

from physics_html import PHYSICS_HTML


# ── AI Prompt → Physics Command translator ─────────────────────────────────────

SYSTEM_PROMPT = """You are a physics simulation assistant.
The user will describe what they want to see in a physics simulation.
Translate their request into ONE of these exact commands (output only the command, nothing else):

Commands available:
- add N balls          (e.g. "add 20 balls")
- add N boxes
- rain
- clear
- explode
- zero gravity
- max gravity
- reset gravity
- reverse gravity
- freeze
- slow
- fast
- pendulum
- dominos
- stack
- orbit
- max bounce

If unsure, default to: add 10 balls
Only output the command. No explanation."""


def ai_to_command(user_text: str, model: str) -> str:
    try:
        llm = OllamaLLM(model=model)
        result = llm.invoke(f"{SYSTEM_PROMPT}\n\nUser: {user_text}")
        return result.strip().lower()
    except Exception as e:
        return f"Error: {e}"


# ── Page ───────────────────────────────────────────────────────────────────────

def show_physics_page(page_header, MODEL_MAP):
    page_header("⚛", "Physics Engine", "Real-time simulation — click canvas to spawn objects")

    col_left, col_right = st.columns([3, 1])

    with col_right:
        st.markdown("#### AI Control")
        model_choice = st.selectbox(
            "Model",
            list(MODEL_MAP.keys()),
            key="physics_model"
        )
        selected_model = MODEL_MAP[model_choice]

        ai_input = st.text_area(
            "Describe what you want",
            placeholder="e.g.\n'make it rain balls'\n'show me a pendulum'\n'simulate zero gravity'\n'make everything explode'",
            height=120,
            key="physics_ai_input"
        )

        if st.button("⚛ Ask AI", key="physics_ai_btn"):
            if ai_input.strip():
                with st.spinner("Translating..."):
                    cmd = ai_to_command(ai_input, selected_model)
                st.code(cmd, language="text")
                st.info("Copy this command into the simulator's prompt bar below.")

        st.markdown("---")
        st.markdown("#### Quick Presets")

        presets = {
            "🔵 Pendulum":  "pendulum",
            "🟧 Dominos":   "dominos",
            "⚫ Stack":     "stack",
            "🌀 Orbit":     "orbit",
            "🌧 Rain":      "rain",
        }
        for label, cmd in presets.items():
            if st.button(label, key=f"preset_{cmd}"):
                st.info(f'Type **"{cmd}"** in the simulator prompt bar and hit Run.')

        st.markdown("---")
        st.markdown("#### Prompt Commands")
        st.caption("""
**Objects**
`add 20 balls` · `add 10 boxes` · `rain`

**Physics**
`zero gravity` · `max gravity` · `reverse gravity`
`freeze` · `slow` · `fast` · `explode` · `max bounce`

**Scenes**
`pendulum` · `dominos` · `stack` · `orbit`

**Canvas**
`clear`
        """)

    with col_left:
        st.components.v1.html(PHYSICS_HTML, height=680, scrolling=False)
