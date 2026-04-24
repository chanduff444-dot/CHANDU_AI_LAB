import os
import time
import streamlit as st
import pandas as pd
from core.game_engine.trainer import train_snake_live, replay_trained_agent
from core.game_engine.renderer import render_snake_html

# ── Agent-vs-You imports ──────────────────────────────────────────────────
from vs_mode import HumanSnakeGame
from core.game_engine.envs.snake import SnakeGame
from core.game_engine.agents.q_learning import QLearningAgent
from core.game_engine.agents.dqn_agent import DQNAgent


# ═══════════════════════════════════════════════════════════════════════════
# Renderer helpers
# ═══════════════════════════════════════════════════════════════════════════

def render_vs_html(render_dict, label: str, color_head: str = "#1a73e8",
                   color_body: str = "#0d47a1", alive: bool = True) -> str:
    """
    Like render_snake_html but lets you override head/body colours
    and add a player label banner.
    """
    snake_set = set(map(tuple, render_dict["snake"]))
    head      = tuple(render_dict["head"]) if render_dict["head"] else None
    food      = tuple(render_dict["food"])
    width     = render_dict["width"]
    height    = render_dict["height"]
    score     = render_dict["score"]
    done      = render_dict["done"]

    CELL = 38

    rows_html = ""
    for y in range(height):
        cells = ""
        for x in range(width):
            pos = (x, y)
            if pos == head:
                bg, icon, size, col = color_head, "■", "18px", "#ffffff"
            elif pos in snake_set:
                bg, icon, size, col = color_body, "■", "14px", "#90caf9"
            elif pos == food:
                bg, icon, size, col = "#111111", "●", "16px", "#ef5350"
            else:
                bg, icon, size, col = "#111111", "",  "0",    "transparent"

            cells += (
                f'<td style="width:{CELL}px;height:{CELL}px;'
                f'background:{bg};text-align:center;vertical-align:middle;'
                f'font-size:{size};color:{col};border:1px solid #1a1a1a;">'
                f'{icon}</td>'
            )
        rows_html += f"<tr>{cells}</tr>"

    if done:
        status       = "💀 DEAD"
        status_color = "#ef5350"
    else:
        status       = f"Score: {score}"
        status_color = "#9aa0a6"

    label_color = "#1a73e8" if "Agent" in label else "#43a047"

    return (
        f'<div style="display:inline-block;background:#0d0d0d;'
        f'padding:12px;border-radius:10px;border:2px solid {label_color};'
        f'text-align:center;">'
        f'<div style="color:{label_color};font-weight:bold;'
        f'font-size:13px;margin-bottom:6px;font-family:sans-serif;">'
        f'{label}</div>'
        f'<div style="color:{status_color};font-size:11px;'
        f'margin-bottom:6px;font-family:sans-serif;letter-spacing:1px;">'
        f'{status}</div>'
        f'<table style="border-collapse:collapse;">{rows_html}</table>'
        f'</div>'
    )


def _make_agent(algo_key, grid_size, lr, gamma, epsilon_decay):
    """Return a trained agent (epsilon=0) or a fresh one if no model exists."""
    if algo_key == "dqn":
        agent = DQNAgent(
            lr=lr, gamma=gamma,
            epsilon=0.0, epsilon_min=0.0,
            epsilon_decay=epsilon_decay,
        )
        path = "data/models/snake_dqn.npz"
        if os.path.exists(path):
            agent.load(path)
    else:
        agent = QLearningAgent(
            lr=lr, gamma=gamma,
            epsilon=0.0, epsilon_min=0.0,
            epsilon_decay=epsilon_decay,
        )
        path = "data/models/snake_q_table.json"
        if os.path.exists(path):
            agent.load(path)
    agent.epsilon = 0.0   # pure exploitation in vs mode
    return agent


# ═══════════════════════════════════════════════════════════════════════════
# VS Mode session-state helpers
# ═══════════════════════════════════════════════════════════════════════════

def _vs_init(algo_key, grid_size, lr, gamma, epsilon_decay):
    """Initialise (or reset) the vs-mode session state."""
    agent      = _make_agent(algo_key, grid_size, lr, gamma, epsilon_decay)
    agent_env  = SnakeGame(width=grid_size, height=grid_size)
    human_env  = HumanSnakeGame(width=grid_size, height=grid_size)
    agent_state = agent_env.reset()

    st.session_state.vs_active      = True
    st.session_state.vs_agent        = agent
    st.session_state.vs_agent_env    = agent_env
    st.session_state.vs_human_env    = human_env
    st.session_state.vs_agent_state  = agent_state
    st.session_state.vs_agent_done   = False
    st.session_state.vs_human_done   = False
    st.session_state.vs_algo         = algo_key
    st.session_state.vs_grid         = grid_size


def _vs_tick():
    """Advance both snakes by one step."""
    # Agent step
    if not st.session_state.vs_agent_done:
        action      = st.session_state.vs_agent.select_action(
            st.session_state.vs_agent_state
        )
        next_state, _, done = st.session_state.vs_agent_env.step(action)
        st.session_state.vs_agent_state = next_state
        st.session_state.vs_agent_done  = done

    # Human step
    if not st.session_state.vs_human_done:
        alive = st.session_state.vs_human_env.step()
        if not alive:
            st.session_state.vs_human_done = True


# ═══════════════════════════════════════════════════════════════════════════
# Main page
# ═══════════════════════════════════════════════════════════════════════════

def show_game_lab_page(page_header):
    page_header(
        "🎮", "Game Lab",
        "Watch your agent learn Snake in real time"
    )

    # ── Sidebar ───────────────────────────────────────────────
    st.sidebar.markdown("---")
    st.sidebar.markdown("**🎮 Game Lab Controls**")

    algorithm = st.sidebar.radio(
        "Algorithm",
        ["Q-Learning", "DQN (Neural Net)"],
        help="Q-Learning: fast, simple. DQN: neural network, scales to larger grids."
    )
    algo_key = "dqn" if "DQN" in algorithm else "qlearning"

    episodes      = st.sidebar.slider("Episodes",         100, 2000,  500, 100)
    grid_size     = st.sidebar.slider("Grid Size",          6,   15,   10,   1)
    lr            = st.sidebar.slider("Learning Rate",   0.01,  0.5,  0.1)
    gamma         = st.sidebar.slider("Gamma",            0.5,  1.0, 0.95)
    epsilon_decay = st.sidebar.slider(
        "Epsilon Decay", 0.990, 0.9999, 0.995, format="%.4f"
    )

    speed_label = st.sidebar.select_slider(
        "Replay Speed",
        options=["Slow", "Normal", "Fast", "Turbo"],
        value="Normal",
    )
    delay_map    = {"Slow": 0.12, "Normal": 0.05, "Fast": 0.01, "Turbo": 0.0}
    render_map   = {"Slow": 1,    "Normal": 6,    "Fast": 14,   "Turbo": 25}
    frame_delay  = delay_map[speed_label]
    render_every = render_map[speed_label]

    # ── Info row ──────────────────────────────────────────────
    c1, c2, c3 = st.columns(3)
    c1.info("■ Blue head — agent")
    c2.info("■ Dark body — snake tail")
    c3.error("● Red dot — food")

    if algo_key == "dqn":
        st.info(
            "🧠 **DQN mode** — neural network agent. "
            "Needs ~200 episodes to warm up the replay buffer before it starts learning. "
            "Better than Q-Learning on grid sizes above 12."
        )

    st.divider()

    # ── Action buttons ────────────────────────────────────────
    b1, b2, b3 = st.columns(3)
    train_clicked = b1.button(
        "▶  Train & Watch Live",
        use_container_width=True,
        type="primary",
    )
    watch_clicked = b2.button(
        "👁  Watch Trained Agent",
        use_container_width=True,
    )
    vs_clicked = b3.button(
        "⚔️  Agent vs You",
        use_container_width=True,
        type="secondary",
    )

    # ═══════════════════════════════════════════════════════════
    # AGENT VS YOU
    # ═══════════════════════════════════════════════════════════

    if vs_clicked:
        _vs_init(algo_key, grid_size, lr, gamma, epsilon_decay)

    if st.session_state.get("vs_active"):
        st.markdown("## ⚔️ Agent vs You")

        algo_name = "DQN" if st.session_state.vs_algo == "dqn" else "Q-Learning"
        st.caption(
            f"**Algorithm:** {algo_name} | "
            f"**Grid:** {st.session_state.vs_grid}×{st.session_state.vs_grid} | "
            f"Agent plays with ε = 0 (pure exploitation)"
        )

        # ── Controls ──────────────────────────────────────────
        st.markdown("#### 🕹️ Your controls — click to steer")

        # Use 5 equal columns: [gap, W, gap, gap, gap]
        c1, c2, c3, c4, c5 = st.columns(5)
        with c2:
            if st.button("W  (Up)",   key="vs_up",    use_container_width=True):
                st.session_state.vs_human_env.set_direction(0)

        c1, c2, c3, c4, c5 = st.columns(5)
        with c1:
            if st.button("A  (Left)", key="vs_left",  use_container_width=True):
                st.session_state.vs_human_env.set_direction(2)
        with c2:
            if st.button("S  (Down)", key="vs_down",  use_container_width=True):
                st.session_state.vs_human_env.set_direction(1)
        with c3:
            if st.button("D  (Right)",key="vs_right", use_container_width=True):
                st.session_state.vs_human_env.set_direction(3)

        # ── Tick both snakes ──────────────────────────────────
        both_done = (
            st.session_state.vs_agent_done and
            st.session_state.vs_human_done
        )

        if not both_done:
            _vs_tick()

        # ── Render side-by-side ───────────────────────────────
        agent_rd = st.session_state.vs_agent_env.render_dict()
        human_rd = st.session_state.vs_human_env.render_dict()

        col_agent, col_vs, col_human = st.columns([5, 1, 5])

        with col_agent:
            st.markdown(
                render_vs_html(
                    agent_rd,
                    label      = f"🤖 Agent ({algo_name})",
                    color_head = "#1a73e8",
                    color_body = "#0d47a1",
                ),
                unsafe_allow_html=True,
            )

        with col_vs:
            st.markdown(
                "<div style='display:flex;align-items:center;"
                "justify-content:center;height:100%;font-size:28px;"
                "font-weight:bold;color:#f5d060;padding-top:120px;'>VS</div>",
                unsafe_allow_html=True,
            )

        with col_human:
            st.markdown(
                render_vs_html(
                    human_rd,
                    label      = "🧑 You",
                    color_head = "#43a047",
                    color_body = "#1b5e20",
                ),
                unsafe_allow_html=True,
            )

        # ── Score bar ─────────────────────────────────────────
        st.markdown("---")
        sc1, sc2, sc3 = st.columns([2, 1, 2])
        with sc1:
            st.metric("🤖 Agent Score", agent_rd["score"])
        with sc2:
            if agent_rd["score"] > human_rd["score"]:
                st.markdown(
                    "<p style='text-align:center;color:#1a73e8;"
                    "font-size:20px;font-weight:bold;'>🤖 Winning</p>",
                    unsafe_allow_html=True,
                )
            elif human_rd["score"] > agent_rd["score"]:
                st.markdown(
                    "<p style='text-align:center;color:#43a047;"
                    "font-size:20px;font-weight:bold;'>🧑 Winning</p>",
                    unsafe_allow_html=True,
                )
            else:
                st.markdown(
                    "<p style='text-align:center;color:#f5d060;"
                    "font-size:20px;'>🟡 Tied</p>",
                    unsafe_allow_html=True,
                )
        with sc3:
            st.metric("🧑 Your Score", human_rd["score"])

        # ── End-game result ───────────────────────────────────
        if both_done or (
            st.session_state.vs_agent_done and
            st.session_state.vs_human_done
        ):
            a_score = agent_rd["score"]
            h_score = human_rd["score"]
            if a_score > h_score:
                st.error("💀 **Agent wins!** Better luck next time.")
            elif h_score > a_score:
                st.success("🎉 **You win!** You beat the AI!")
            else:
                st.info("🤝 **It's a draw!**")

            if st.button("🔄 Play Again", type="primary"):
                _vs_init(algo_key, grid_size, lr, gamma, epsilon_decay)
                st.rerun()

        elif st.session_state.vs_agent_done and not st.session_state.vs_human_done:
            st.warning("🤖 Agent died! Keep going — you're still alive!")
        elif st.session_state.vs_human_done and not st.session_state.vs_agent_done:
            st.error("💀 You died! The agent is still going...")

        # ── Reset button ──────────────────────────────────────
        if st.button("🔄 Reset Match", key="vs_reset"):
            _vs_init(algo_key, grid_size, lr, gamma, epsilon_decay)
            st.rerun()

        # Auto-rerun to advance the game loop (only while playing)
        if not both_done:
            time.sleep(0.18)   # ~5-6 fps feels natural for human play
            st.rerun()

    # ═══════════════════════════════════════════════════════════
    # WATCH TRAINED AGENT
    # ═══════════════════════════════════════════════════════════

    if watch_clicked:
        # Exit vs mode if active
        st.session_state.vs_active = False

        model_path = (
            "data/models/snake_dqn.npz"
            if algo_key == "dqn"
            else "data/models/snake_q_table.json"
        )

        if not os.path.exists(model_path):
            st.error(
                f"No trained **{algorithm}** model found. "
                f"Click **Train & Watch Live** first to train one."
            )
        else:
            st.markdown("### 👁 Trained agent — pure exploitation (ε = 0)")

            wl, wr   = st.columns([1, 1])
            w_game   = wl.empty()
            w_info   = wr.empty()
            w_status = st.empty()

            for frame in replay_trained_agent(
                width=grid_size, height=grid_size,
                episodes=5, algorithm=algo_key,
            ):
                if "error" in frame:
                    st.error(frame["error"])
                    break

                w_game.markdown(
                    render_snake_html(frame),
                    unsafe_allow_html=True,
                )
                w_info.markdown(
                    f"**Episode:** {frame['episode'] + 1} / {frame['total_episodes']}  \n"
                    f"**Score:** {frame['score']}  \n"
                    f"**Steps:** {frame['steps']}"
                )
                w_status.caption(
                    f"Speed: {speed_label} — trained {algorithm} agent playing"
                )

                if frame_delay > 0:
                    time.sleep(frame_delay)

            st.success("✅ Replay complete!")

    # ═══════════════════════════════════════════════════════════
    # TRAIN & WATCH LIVE
    # ═══════════════════════════════════════════════════════════

    if train_clicked:
        # Exit vs mode if active
        st.session_state.vs_active = False

        left, right = st.columns([1, 1])

        with left:
            st.markdown("#### Live game")
            game_display = st.empty()

        with right:
            st.markdown("#### Stats")
            ep_display     = st.empty()
            score_display  = st.empty()
            eps_display    = st.empty()
            chart_display  = st.empty()

        frame_count = 0
        best_score  = 0

        for frame in train_snake_live(
            episodes      = episodes,
            width         = grid_size,
            height        = grid_size,
            lr            = lr,
            gamma         = gamma,
            epsilon_decay = epsilon_decay,
            algorithm     = algo_key,
        ):
            if frame.get("training_complete"):
                game_display.markdown(
                    render_snake_html(frame),
                    unsafe_allow_html=True,
                )
                st.success(
                    f"✅ Training complete! "
                    f"Best score: **{frame.get('best_score', 0):.0f}** | "
                    f"Algorithm: **{algorithm}** | "
                    f"Episodes: **{episodes}**  \n"
                    f"Model saved — click **👁 Watch Trained Agent** to replay."
                )
                break

            frame_count += 1
            best_score = max(best_score, frame["score"])

            if frame_count % render_every == 0:
                game_display.markdown(
                    render_snake_html(frame),
                    unsafe_allow_html=True,
                )
                ep_display.metric(
                    "Episode",
                    f"{frame['episode'] + 1} / {frame['total_episodes']}",
                )
                score_display.metric(
                    "Score this episode",
                    frame["score"],
                    delta=f"Best so far: {best_score}",
                )
                eps_display.metric(
                    "Epsilon (explore rate)",
                    frame["epsilon"],
                )

                rewards = frame["rewards_so_far"]
                if len(rewards) > 2:
                    df = pd.DataFrame({
                        "Episode": range(len(rewards)),
                        "Reward":  rewards,
                    })
                    chart_display.line_chart(
                        df, x="Episode", y="Reward",
                        use_container_width=True,
                    )

                if frame_delay > 0:
                    time.sleep(frame_delay)