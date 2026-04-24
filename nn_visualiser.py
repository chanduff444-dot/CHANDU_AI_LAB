"""
nn_visualiser.py  —  Neural Network Visualiser page for Chandu AI Lab

Place this file wherever your other pages live (e.g. alongside game_lab.py).
It reads the trained DQN weights from data/models/snake_dqn.npz and draws
the network live with an SVG renderer.

No extra dependencies — pure numpy + streamlit.
"""

import os
import numpy as np
import streamlit as st


# ═══════════════════════════════════════════════════════════════════════════
# Weight loader
# ═══════════════════════════════════════════════════════════════════════════

def load_dqn_weights(path="data/models/snake_dqn.npz"):
    if not os.path.exists(path):
        return None
    d = np.load(path)
    return {
        "W1": d["W1"], "b1": d["b1"],
        "W2": d["W2"], "b2": d["b2"],
        "W3": d["W3"], "b3": d["b3"],
    }


def forward_pass(weights, x):
    """Run one forward pass, return activations per layer."""
    z1 = x @ weights["W1"] + weights["b1"]
    a1 = np.maximum(0, z1)
    z2 = a1 @ weights["W2"] + weights["b2"]
    a2 = np.maximum(0, z2)
    z3 = a2 @ weights["W3"] + weights["b3"]
    return [x, a1, a2, z3]


# ═══════════════════════════════════════════════════════════════════════════
# SVG renderer
# ═══════════════════════════════════════════════════════════════════════════

def _lerp_color(v, lo=-1.0, hi=1.0):
    if np.isnan(v) or np.isnan(lo) or np.isnan(hi):
        return "#222222"

    denom = (hi - lo)
    if denom == 0 or np.isnan(denom):
        return "#222222"

    t = (np.clip(v, lo, hi) - lo) / (denom + 1e-8)

    if np.isnan(t):
        return "#222222"

    if t < 0.5:
        r = int(220 * (1 - t * 2))
        g = int(30  * (1 - t * 2))
        b = int(30  * (1 - t * 2))
    else:
        s = (t - 0.5) * 2
        if np.isnan(s):
            return "#222222"
        r = int(20  + 20  * s)
        g = int(180 * s)
        b = int(220 * s)

    return f"#{r:02x}{g:02x}{b:02x}"


def _act_color(v, max_v=1.0):
    """Activation colour: dark=0, bright gold=high."""
    if np.isnan(v) or np.isnan(max_v):
        return "#111111"
    t = float(np.clip(abs(v) / (max_v + 1e-8), 0, 1))
    if np.isnan(t):
        return "#111111"
    r = int(30  + 215 * t)
    g = int(20  + 170 * t)
    b = int(10  +  10 * t)
    return f"#{r:02x}{g:02x}{b:02x}"


def render_network_svg(
    weights,
    activations,
    layer_labels,
    node_labels,
    width=900,
    height=520,
    max_edges_per_layer=300,
):
    """
    Build a full SVG string of the network.
    Shows:
      - Every node coloured by activation magnitude
      - A sampled subset of edges coloured by weight sign/magnitude
      - Layer names and node labels on the input layer
    """
    layers = [w.shape[0] for w in [
        weights["W1"], weights["W2"], weights["W3"]
    ]] + [weights["W3"].shape[1]]

    # How many nodes to actually draw per layer (cap for visual clarity)
    DISPLAY_CAP = [11, 16, 16, 3]
    draw_counts = [min(n, cap) for n, cap in zip(layers, DISPLAY_CAP)]

    PAD_X   = 70
    PAD_Y   = 50
    net_w   = width  - 2 * PAD_X
    net_h   = height - 2 * PAD_Y
    R       = 14     # node radius
    layer_x = [PAD_X + i * net_w // (len(layers) - 1) for i in range(len(layers))]

    def node_y(layer_idx, node_idx, n_nodes):
        spacing = net_h / (n_nodes + 1)
        return PAD_Y + spacing * (node_idx + 1)

    svg = [
        f'<svg xmlns="http://www.w3.org/2000/svg" '
        f'width="{width}" height="{height}" '
        f'style="background:#0a0a0a;border-radius:12px;'
        f'border:1px solid #1e1e1e;font-family:monospace;">'
    ]

    # ── Edges ──────────────────────────────────────────────────────────────
    weight_matrices = [weights["W1"], weights["W2"], weights["W3"]]

    for li, W in enumerate(weight_matrices):
        src_n   = draw_counts[li]
        dst_n   = draw_counts[li + 1]
        src_tot = layers[li]
        dst_tot = layers[li + 1]

        # Sample edges to avoid SVG explosion on large hidden layers
        pairs = [(i, j) for i in range(src_n) for j in range(dst_n)]
        if len(pairs) > max_edges_per_layer:
            rng   = np.random.default_rng(42)
            pairs = [pairs[k] for k in rng.choice(len(pairs),
                     max_edges_per_layer, replace=False)]

        w_abs_max = np.abs(W).max() + 1e-8

        for (si, di) in pairs:
            w_val  = W[si, di]
            alpha  = float(np.clip(abs(w_val) / w_abs_max, 0.05, 0.9))
            color  = _lerp_color(w_val, -w_abs_max, w_abs_max)
            x1     = layer_x[li]
            y1     = node_y(li,      si, src_n)
            x2     = layer_x[li + 1]
            y2     = node_y(li + 1,  di, dst_n)
            svg.append(
                f'<line x1="{x1:.0f}" y1="{y1:.0f}" '
                f'x2="{x2:.0f}" y2="{y2:.0f}" '
                f'stroke="{color}" stroke-width="1" '
                f'stroke-opacity="{alpha:.2f}"/>'
            )

    # ── Nodes ──────────────────────────────────────────────────────────────
    act_max = max(np.abs(a).max() for a in activations) + 1e-8

    for li in range(len(layers)):
        n     = draw_counts[li]
        act   = activations[li]
        lx    = layer_x[li]
        label = layer_labels[li]

        # Layer name
        svg.append(
            f'<text x="{lx}" y="{PAD_Y - 18}" '
            f'fill="#c8960c" font-size="11" text-anchor="middle" '
            f'font-weight="bold">{label}</text>'
        )
        # Node count subtitle
        svg.append(
            f'<text x="{lx}" y="{PAD_Y - 6}" '
            f'fill="#555" font-size="9" text-anchor="middle">'
            f'{layers[li]} nodes</text>'
        )

        for ni in range(n):
            cx    = lx
            cy    = node_y(li, ni, n)
            val   = float(act[ni]) if ni < len(act) else 0.0
            color = _act_color(val, act_max)

            # Glow ring for high activations
            glow_r = min(abs(val) / (act_max + 1e-8), 1.0)
            if glow_r > 0.4:
                svg.append(
                    f'<circle cx="{cx:.0f}" cy="{cy:.0f}" r="{R + 5}" '
                    f'fill="none" stroke="#c8960c" '
                    f'stroke-width="1" stroke-opacity="{glow_r * 0.5:.2f}"/>'
                )

            # Node circle
            svg.append(
                f'<circle cx="{cx:.0f}" cy="{cy:.0f}" r="{R}" '
                f'fill="{color}" stroke="#333" stroke-width="1"/>'
            )

            # Value text inside node
            txt_color = "#fff" if abs(val) / (act_max + 1e-8) > 0.3 else "#666"
            svg.append(
                f'<text x="{cx:.0f}" y="{cy + 4:.0f}" '
                f'fill="{txt_color}" font-size="7" text-anchor="middle">'
                f'{val:.2f}</text>'
            )

            # Input node labels (on the left)
            if li == 0 and node_labels and ni < len(node_labels):
                svg.append(
                    f'<text x="{cx - R - 5:.0f}" y="{cy + 4:.0f}" '
                    f'fill="#888" font-size="8" text-anchor="end">'
                    f'{node_labels[ni]}</text>'
                )

            # Output node labels (on the right)
            if li == len(layers) - 1:
                out_labels = ["Straight", "Turn R", "Turn L"]
                if ni < len(out_labels):
                    svg.append(
                        f'<text x="{cx + R + 5:.0f}" y="{cy + 4:.0f}" '
                        f'fill="#c8960c" font-size="9" text-anchor="start">'
                        f'{out_labels[ni]}</text>'
                    )

    # ── Legend ─────────────────────────────────────────────────────────────
    lx = width - 160
    ly = height - 70
    svg += [
        f'<text x="{lx}" y="{ly - 8}" fill="#555" font-size="9">EDGE WEIGHT</text>',
        f'<rect x="{lx}" y="{ly}" width="120" height="8" rx="4" '
        f'fill="url(#wgrad)"/>',
        f'<defs><linearGradient id="wgrad" x1="0" x2="1" y1="0" y2="0">'
        f'<stop offset="0%"   stop-color="#dc1e1e"/>'
        f'<stop offset="50%"  stop-color="#222"/>'
        f'<stop offset="100%" stop-color="#14b4dc"/>'
        f'</linearGradient></defs>',
        f'<text x="{lx}"       y="{ly + 20}" fill="#dc1e1e" font-size="8">negative</text>',
        f'<text x="{lx + 120}" y="{ly + 20}" fill="#14b4dc" font-size="8" '
        f'text-anchor="end">positive</text>',

        f'<text x="{lx}" y="{ly + 36}" fill="#555" font-size="9">NODE ACTIVATION</text>',
        f'<rect x="{lx}" y="{ly + 42}" width="120" height="8" rx="4" '
        f'fill="url(#agrad)"/>',
        f'<defs><linearGradient id="agrad" x1="0" x2="1" y1="0" y2="0">'
        f'<stop offset="0%"   stop-color="#1e1e1e"/>'
        f'<stop offset="100%" stop-color="#f5d060"/>'
        f'</linearGradient></defs>',
        f'<text x="{lx}"       y="{ly + 62}" fill="#555" font-size="8">low</text>',
        f'<text x="{lx + 120}" y="{ly + 62}" fill="#f5d060" font-size="8" '
        f'text-anchor="end">high</text>',
    ]

    svg.append("</svg>")
    return "\n".join(svg)


# ═══════════════════════════════════════════════════════════════════════════
# Stat helpers
# ═══════════════════════════════════════════════════════════════════════════

def weight_stats(W, name):
    return {
        "Layer":  name,
        "Shape":  f"{W.shape[0]} × {W.shape[1]}",
        "Mean":   f"{W.mean():.4f}",
        "Std":    f"{W.std():.4f}",
        "Min":    f"{W.min():.4f}",
        "Max":    f"{W.max():.4f}",
        "Dead %": f"{(np.abs(W) < 0.01).mean() * 100:.1f}%",
    }


# ═══════════════════════════════════════════════════════════════════════════
# Snake state presets for the probe panel
# ═══════════════════════════════════════════════════════════════════════════

PRESETS = {
    "Danger ahead — go right": [1,0,0,  0,1,0,0,  0,1,0,0],
    "Danger right — go left":  [0,1,0,  0,1,0,0,  0,1,0,0],
    "Food up-left":             [0,0,0,  0,1,0,0,  1,0,1,0],
    "Food down-right":          [0,0,0,  0,1,0,0,  0,1,0,1],
    "Clear path, food ahead":   [0,0,0,  0,1,0,0,  0,1,0,0],
    "All danger":               [1,1,1,  0,1,0,0,  0,1,0,0],
}

INPUT_LABELS = [
    "danger_fwd", "danger_right", "danger_left",
    "dir_left", "dir_right", "dir_up", "dir_down",
    "food_left", "food_right", "food_up", "food_down",
]


# ═══════════════════════════════════════════════════════════════════════════
# Main page
# ═══════════════════════════════════════════════════════════════════════════

def show_nn_visualiser_page(page_header):
    page_header(
        "🧠", "Neural Network Visualiser",
        "See inside your trained DQN — weights, activations, and decisions live"
    )

    weights = load_dqn_weights()

    if weights is None:
        st.warning(
            "⚠️ No trained DQN model found at `data/models/snake_dqn.npz`.  \n"
            "Go to **🎮 Game Lab** → select **DQN (Neural Net)** → click "
            "**▶ Train & Watch Live** to train one first."
        )
        return

    # ── Architecture summary ──────────────────────────────────
    arch = (
        f"**Input:** 11 signals  →  "
        f"**Hidden 1:** {weights['W1'].shape[1]} neurons  →  "
        f"**Hidden 2:** {weights['W2'].shape[1]} neurons  →  "
        f"**Output:** 3 actions"
    )
    st.markdown(arch)
    st.divider()

    # ── Tabs ──────────────────────────────────────────────────
    tab1, tab2, tab3 = st.tabs([
        "🔬 Probe — feed a state",
        "📊 Weight Inspector",
        "ℹ️ How it works",
    ])

    # ══════════════════════════════════════════════════════════
    # TAB 1 — Probe
    # ══════════════════════════════════════════════════════════
    with tab1:
        st.markdown("### Feed a game state — see what the agent decides")
        st.caption(
            "Choose a preset scenario or manually tune the 11 input signals. "
            "The network diagram updates instantly showing activations and the chosen action."
        )

        col_ctrl, col_net = st.columns([1, 2])

        with col_ctrl:
            preset = st.selectbox("Quick presets", ["— custom —"] + list(PRESETS.keys()))
            if preset != "— custom —":
                defaults = PRESETS[preset]
            else:
                defaults = [0] * 11

            st.markdown("#### 🎛️ Input signals")
            st.caption("Danger signals")
            d_fwd   = st.checkbox("Danger ahead",      value=bool(defaults[0]))
            d_right = st.checkbox("Danger right",      value=bool(defaults[1]))
            d_left  = st.checkbox("Danger left",       value=bool(defaults[2]))

            st.caption("Current direction (one-hot)")
            dir_l = st.checkbox("Moving left",         value=bool(defaults[3]))
            dir_r = st.checkbox("Moving right",        value=bool(defaults[4]))
            dir_u = st.checkbox("Moving up",           value=bool(defaults[5]))
            dir_d = st.checkbox("Moving down",         value=bool(defaults[6]))

            st.caption("Food location")
            f_left  = st.checkbox("Food is left",      value=bool(defaults[7]))
            f_right = st.checkbox("Food is right",     value=bool(defaults[8]))
            f_up    = st.checkbox("Food is up",        value=bool(defaults[9]))
            f_down  = st.checkbox("Food is down",      value=bool(defaults[10]))

        state = np.array([
            d_fwd, d_right, d_left,
            dir_l, dir_r, dir_u, dir_d,
            f_left, f_right, f_up, f_down,
        ], dtype=np.float32)

        activations = forward_pass(weights, state)

        with col_net:
            layer_labels = ["Input\n(11)", "Hidden 1", "Hidden 2", "Output\n(3)"]
            svg = render_network_svg(
                weights,
                activations,
                layer_labels,
                INPUT_LABELS,
                width=640,
                height=500,
            )
            st.markdown(svg, unsafe_allow_html=True)

        # ── Decision readout ──────────────────────────────────
        st.divider()
        q_vals   = activations[-1]
        action   = int(np.argmax(q_vals))
        actions  = ["⬆ Go Straight", "↪ Turn Right", "↩ Turn Left"]
        colors   = ["#1a73e8", "#43a047", "#f5d060"]

        st.markdown("### 🤖 Agent decision")
        dc1, dc2, dc3 = st.columns(3)
        for i, (col, act, qv) in enumerate(zip([dc1, dc2, dc3], actions, q_vals)):
            chosen = i == action
            col.markdown(
                f"<div style='background:{'#1a1a1a' if not chosen else '#1c2d1c'};"
                f"border:{'2px solid #43a047' if chosen else '1px solid #2a2a2a'};"
                f"border-radius:8px;padding:12px;text-align:center;'>"
                f"<div style='color:{'#43a047' if chosen else '#666'};font-size:11px;"
                f"font-weight:bold;margin-bottom:4px;'>{'✅ CHOSEN' if chosen else ''}</div>"
                f"<div style='color:#fff;font-size:15px;font-weight:bold;'>{act}</div>"
                f"<div style='color:#c8960c;font-size:18px;font-weight:bold;"
                f"margin-top:6px;'>{qv:.3f}</div>"
                f"<div style='color:#555;font-size:10px;'>Q-value</div>"
                f"</div>",
                unsafe_allow_html=True,
            )

        # ── Activation values ─────────────────────────────────
        with st.expander("🔢 Raw activation values"):
            for li, (act, lname) in enumerate(zip(
                activations,
                ["Input", "Hidden 1 (ReLU)", "Hidden 2 (ReLU)", "Output (Q-values)"]
            )):
                st.markdown(f"**{lname}** — {len(act)} values")
                vals = act[:16]   # show first 16
                bar_html = "<div style='display:flex;gap:3px;flex-wrap:wrap;'>"
                max_v = np.abs(act).max() + 1e-8
                for v in vals:
                    if np.isnan(v):
                        continue
                    t     = float(np.clip(abs(v) / max_v, 0, 1))
                    if np.isnan(t):
                        continue
                    h     = int(t * 40)
                    color = _act_color(v, max_v)
                    bar_html += (
                        f"<div style='width:18px;height:{max(h, 3)}px;"
                        f"background:{color};border-radius:2px;"
                        f"title=\"{v:.3f}\";'></div>"
                    )
                bar_html += "</div>"
                st.markdown(bar_html, unsafe_allow_html=True)
                if len(act) > 16:
                    st.caption(f"Showing first 16 of {len(act)} neurons")

    # ══════════════════════════════════════════════════════════
    # TAB 2 — Weight Inspector
    # ══════════════════════════════════════════════════════════
    with tab2:
        st.markdown("### 📊 Weight statistics per layer")
        st.caption(
            "Dead % = fraction of weights with |w| < 0.01 — "
            "high dead% means those neurons aren't learning."
        )

        import pandas as pd
        rows = [
            weight_stats(weights["W1"], "W1  (input → hidden1)"),
            weight_stats(weights["W2"], "W2  (hidden1 → hidden2)"),
            weight_stats(weights["W3"], "W3  (hidden2 → output)"),
        ]
        st.dataframe(pd.DataFrame(rows), use_container_width=True, hide_index=True)

        st.divider()
        st.markdown("### 🗺️ Weight heatmaps")

        wh1, wh2, wh3 = st.columns(3)

        def weight_heatmap_svg(W, title, w=200, h=160):
            rows_n, cols_n = W.shape
            # Sample to max 20×20 for display
            ri = np.linspace(0, rows_n - 1, min(rows_n, 20), dtype=int)
            ci = np.linspace(0, cols_n - 1, min(cols_n, 20), dtype=int)
            sub = W[np.ix_(ri, ci)]
            m   = np.abs(sub).max() + 1e-8
            nr, nc = sub.shape
            cw  = w / nc
            ch  = h / nr
            svg = [
                f'<svg width="{w + 10}" height="{h + 30}" '
                f'xmlns="http://www.w3.org/2000/svg" '
                f'style="background:#0a0a0a;border-radius:8px;">'
                f'<text x="{(w+10)//2}" y="14" fill="#c8960c" '
                f'font-size="10" text-anchor="middle" font-family="monospace">'
                f'{title}</text>'
            ]
            for ri2, row in enumerate(sub):
                for ci2, v in enumerate(row):
                    color = _lerp_color(v, -m, m)
                    x = ci2 * cw
                    y = ri2 * ch + 20
                    svg.append(
                        f'<rect x="{x:.1f}" y="{y:.1f}" '
                        f'width="{cw:.1f}" height="{ch:.1f}" '
                        f'fill="{color}"/>'
                    )
            svg.append("</svg>")
            return "\n".join(svg)

        wh1.markdown(
            weight_heatmap_svg(weights["W1"], "W1 (11 × hidden)"),
            unsafe_allow_html=True,
        )
        wh2.markdown(
            weight_heatmap_svg(weights["W2"], "W2 (hidden × hidden)"),
            unsafe_allow_html=True,
        )
        wh3.markdown(
            weight_heatmap_svg(weights["W3"], "W3 (hidden × 3)"),
            unsafe_allow_html=True,
        )

        st.divider()
        st.markdown("### 📈 Weight distributions")
        for name, W in [("W1", weights["W1"]),
                         ("W2", weights["W2"]),
                         ("W3", weights["W3"])]:
            flat = W.flatten()
            bins = np.linspace(flat.min(), flat.max(), 40)
            hist, edges = np.histogram(flat, bins=bins)
            df = pd.DataFrame({
                "Weight value": edges[:-1].round(3),
                "Count": hist,
            })
            st.caption(f"**{name}** weight distribution")
            st.bar_chart(df, x="Weight value", y="Count",
                         use_container_width=True, height=140)

    # ══════════════════════════════════════════════════════════
    # TAB 3 — How it works
    # ══════════════════════════════════════════════════════════
    with tab3:
        st.markdown("""
### How your DQN works

#### The 11 input signals
Your agent doesn't see the full grid. It only gets 11 binary signals:

| Signal | Meaning |
|---|---|
| `danger_fwd` | Will the snake die if it goes straight? |
| `danger_right` | Will it die turning right? |
| `danger_left` | Will it die turning left? |
| `dir_left/right/up/down` | Which direction is it currently moving? (one-hot) |
| `food_left/right/up/down` | Is food in that relative direction? |

#### The network architecture
```
Input (11)  →  Hidden 1 (256, ReLU)  →  Hidden 2 (256, ReLU)  →  Output (3)
```
- **ReLU** activation: sets negative values to 0 — shown as dark nodes
- **Output** = Q-values: how good is each action from this state?

#### Reading the visualiser
- **Node colour**: gold = highly active, dark = inactive/zero
- **Glow ring**: appears when a node activates strongly
- **Edge colour**: cyan = positive weight, red = negative weight
- **Edge opacity**: stronger weights are more visible

#### What to look for
- **Dead neurons** (always dark): the network has learned to ignore those
- **High Q-value gap**: confident decision — big difference between best and worst action
- **Danger signals lighting up**: watch how the hidden layers respond when danger flags are set
        """)