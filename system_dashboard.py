"""
system_dashboard.py  —  System Dashboard page for Chandu AI Lab

Drop this file in your CHANDU_CORE folder alongside game_lab_page.py etc.

Requirements:
    pip install psutil

Usage in lab_app.py:
    from system_dashboard import show_system_dashboard_page

    elif page_name == "System Dashboard":
        show_system_dashboard_page(page_header)

Add to sidebar navigation:
    "🖥️ System Dashboard",
"""

import time
import datetime
import os
import json

import streamlit as st
import psutil
import numpy as np


# ═══════════════════════════════════════════════════════════════════════════
# Helpers
# ═══════════════════════════════════════════════════════════════════════════

def _bytes_to_gb(b: int) -> float:
    return round(b / (1024 ** 3), 2)


def _get_system_stats() -> dict:
    cpu      = psutil.cpu_percent(interval=0.3)
    mem      = psutil.virtual_memory()
    disk     = psutil.disk_usage("/")
    boot_ts  = psutil.boot_time()
    uptime_s = time.time() - boot_ts
    uptime   = str(datetime.timedelta(seconds=int(uptime_s)))

    return {
        "cpu_pct":      cpu,
        "ram_used_gb":  _bytes_to_gb(mem.used),
        "ram_total_gb": _bytes_to_gb(mem.total),
        "ram_pct":      mem.percent,
        "disk_used_gb": _bytes_to_gb(disk.used),
        "disk_total_gb":_bytes_to_gb(disk.total),
        "disk_pct":     disk.percent,
        "uptime":       uptime,
        "cpu_count":    psutil.cpu_count(logical=True),
    }


def _color_for_pct(pct: float) -> str:
    if pct < 50:
        return "#43a047"   # green
    elif pct < 80:
        return "#f9a825"   # yellow
    return "#e53935"       # red


def _gauge_svg(pct: float, label: str, color: str, size: int = 130) -> str:
    """Minimal SVG arc gauge."""
    r      = 44
    cx, cy = size // 2, size // 2 + 10
    stroke = 10
    # Arc math (semicircle from -180° to 0°)
    angle  = -180 + (pct / 100) * 180
    rad    = angle * (3.14159 / 180)
    ex     = cx + r * (-1 * (1 - (pct / 100)))   # simplified
    # SVG path for a semicircle
    start_x = cx - r
    start_y = cy
    end_x   = cx + r * (pct / 100 * 2 - 1)
    end_y   = cy - r * (1 - abs(pct / 100 * 2 - 1)) * 0.5

    # Use stroke-dasharray trick on a circle
    circ   = 2 * 3.14159 * r
    dash   = circ * (pct / 100) * 0.5
    gap    = circ - dash

    return f"""
<svg width="{size}" height="{size - 10}" xmlns="http://www.w3.org/2000/svg">
  <!-- background track -->
  <circle cx="{cx}" cy="{cy}" r="{r}"
    fill="none" stroke="#1e1e1e" stroke-width="{stroke}"
    stroke-dasharray="{circ * 0.5:.1f} {circ:.1f}"
    stroke-dashoffset="{circ * 0.25:.1f}"
    stroke-linecap="round"/>
  <!-- value arc -->
  <circle cx="{cx}" cy="{cy}" r="{r}"
    fill="none" stroke="{color}" stroke-width="{stroke}"
    stroke-dasharray="{dash:.1f} {gap + circ * 0.5:.1f}"
    stroke-dashoffset="{circ * 0.25:.1f}"
    stroke-linecap="round"/>
  <!-- percentage text -->
  <text x="{cx}" y="{cy + 6}" fill="#e8eaed"
    font-size="16" font-weight="bold"
    text-anchor="middle" font-family="monospace">{pct:.0f}%</text>
  <!-- label -->
  <text x="{cx}" y="{cy + 24}" fill="#9aa0a6"
    font-size="10" text-anchor="middle" font-family="monospace">{label}</text>
</svg>"""


def _mini_bar(pct: float, color: str, width: int = 200) -> str:
    filled = int(width * pct / 100)
    return f"""
<div style="background:#1a1a1a;border-radius:4px;height:8px;width:{width}px;overflow:hidden;margin-top:4px;">
  <div style="background:{color};height:8px;width:{filled}px;border-radius:4px;
    transition:width 0.5s ease;"></div>
</div>"""


def _load_task_log(path: str = "data/task_log.json") -> list:
    if not os.path.exists(path):
        return []
    try:
        with open(path) as f:
            return json.load(f)
    except Exception:
        return []


def _save_task_log(tasks: list, path: str = "data/task_log.json"):
    os.makedirs("data", exist_ok=True)
    with open(path, "w") as f:
        json.dump(tasks, f, indent=2)


def _model_usage_stats(log_path: str = "data/logs.json") -> dict:
    """Read existing interaction logs and count model usage."""
    if not os.path.exists(log_path):
        return {}
    try:
        with open(log_path) as f:
            logs = json.load(f)
        counts = {}
        for entry in logs:
            m = entry.get("model", "unknown")
            counts[m] = counts.get(m, 0) + 1
        return counts
    except Exception:
        return {}


# ═══════════════════════════════════════════════════════════════════════════
# Main page
# ═══════════════════════════════════════════════════════════════════════════

def show_system_dashboard_page(page_header):
    page_header(
        "🖥️", "System Dashboard",
        "Live system metrics, model usage, and task logs — your AI OS control panel"
    )

    # ── Auto-refresh toggle ───────────────────────────────────
    col_ref, col_int, _ = st.columns([1, 1, 4])
    auto_refresh = col_ref.checkbox("🔄 Auto-refresh", value=False)
    interval     = col_int.selectbox("Interval", [5, 10, 30, 60], index=1,
                                     label_visibility="collapsed")

    if auto_refresh:
        time.sleep(interval)
        st.rerun()

    st.divider()

    # ══════════════════════════════════════════════════════════
    # SECTION 1 — Live Hardware Metrics
    # ══════════════════════════════════════════════════════════
    st.markdown("### ⚡ Live Hardware")

    stats = _get_system_stats()

    g1, g2, g3, g4 = st.columns(4)

    # CPU gauge
    cpu_color = _color_for_pct(stats["cpu_pct"])
    g1.markdown(
        _gauge_svg(stats["cpu_pct"], "CPU", cpu_color),
        unsafe_allow_html=True,
    )
    g1.caption(f"🧮 {stats['cpu_count']} logical cores")

    # RAM gauge
    ram_color = _color_for_pct(stats["ram_pct"])
    g2.markdown(
        _gauge_svg(stats["ram_pct"], "RAM", ram_color),
        unsafe_allow_html=True,
    )
    g2.caption(f"💾 {stats['ram_used_gb']} / {stats['ram_total_gb']} GB")

    # Disk gauge
    disk_color = _color_for_pct(stats["disk_pct"])
    g3.markdown(
        _gauge_svg(stats["disk_pct"], "Disk", disk_color),
        unsafe_allow_html=True,
    )
    g3.caption(f"💿 {stats['disk_used_gb']} / {stats['disk_total_gb']} GB")

    # Uptime card
    g4.markdown(
        f"""<div style="background:#111;border:1px solid #222;border-radius:12px;
        padding:18px;text-align:center;margin-top:4px;">
        <div style="color:#9aa0a6;font-size:10px;margin-bottom:6px;font-family:monospace;">UPTIME</div>
        <div style="color:#c8960c;font-size:18px;font-weight:bold;font-family:monospace;">
        {stats['uptime']}</div>
        <div style="color:#555;font-size:9px;margin-top:8px;">since last boot</div>
        </div>""",
        unsafe_allow_html=True,
    )

    st.divider()

    # ── Progress bars (detailed) ──────────────────────────────
    b1, b2, b3 = st.columns(3)

    for col, label, pct, detail, color in [
        (b1, "CPU Usage",  stats["cpu_pct"],  f"{stats['cpu_pct']:.1f}%",           cpu_color),
        (b2, "RAM Usage",  stats["ram_pct"],  f"{stats['ram_used_gb']} GB used",    ram_color),
        (b3, "Disk Usage", stats["disk_pct"], f"{stats['disk_used_gb']} GB used",   disk_color),
    ]:
        col.markdown(
            f"<div style='font-size:12px;color:#9aa0a6;font-family:monospace;'>"
            f"{label} — <span style='color:{color};font-weight:bold;'>{detail}</span></div>"
            + _mini_bar(pct, color, width=220),
            unsafe_allow_html=True,
        )

    st.divider()

    # ══════════════════════════════════════════════════════════
    # SECTION 2 — Model Usage Stats
    # ══════════════════════════════════════════════════════════
    st.markdown("### 🤖 Model Usage")

    usage = _model_usage_stats()

    if usage:
        total_calls = sum(usage.values())
        mu_cols     = st.columns(min(len(usage), 4))

        for i, (model, count) in enumerate(
            sorted(usage.items(), key=lambda x: -x[1])
        ):
            pct = count / total_calls * 100
            mu_cols[i % 4].markdown(
                f"""<div style="background:#111;border:1px solid #222;
                border-radius:10px;padding:14px;margin-bottom:8px;">
                <div style="color:#c8960c;font-size:11px;font-weight:bold;
                font-family:monospace;margin-bottom:6px;">{model}</div>
                <div style="color:#e8eaed;font-size:22px;font-weight:bold;">{count}</div>
                <div style="color:#555;font-size:10px;">calls · {pct:.1f}%</div>
                {_mini_bar(pct, '#1a73e8', 160)}
                </div>""",
                unsafe_allow_html=True,
            )
    else:
        st.info("No model usage data yet — start using the Brain page.")

    st.divider()

    # ══════════════════════════════════════════════════════════
    # SECTION 3 — Active Agents / Processes
    # ══════════════════════════════════════════════════════════
    st.markdown("### 🤖 Active Agents")

    # Check for Ollama / Python processes
    agents = []
    for proc in psutil.process_iter(["pid", "name", "cpu_percent", "memory_percent"]):
        try:
            name = proc.info["name"].lower()
            if any(k in name for k in ["ollama", "python", "streamlit"]):
                agents.append({
                    "Process": proc.info["name"],
                    "PID":     proc.info["pid"],
                    "CPU %":   f"{proc.info['cpu_percent']:.1f}",
                    "RAM %":   f"{proc.info['memory_percent']:.1f}",
                    "Status":  "🟢 Running",
                })
        except (psutil.NoSuchProcess, psutil.AccessDenied):
            pass

    if agents:
        import pandas as pd
        st.dataframe(
            pd.DataFrame(agents),
            use_container_width=True,
            hide_index=True,
        )
    else:
        st.info("No tracked agents running.")

    st.divider()

    # ══════════════════════════════════════════════════════════
    # SECTION 4 — Task Log
    # ══════════════════════════════════════════════════════════
    st.markdown("### 🧾 Task Log")

    tasks = _load_task_log()

    # Add new task
    with st.expander("➕ Add Task / Note"):
        tc1, tc2 = st.columns([3, 1])
        new_task = tc1.text_input("Task description", label_visibility="collapsed",
                                   placeholder="e.g. Retrain DQN with lr=0.001")
        tag      = tc2.selectbox("Tag", ["🧪 Experiment", "🐛 Bug", "💡 Idea",
                                          "✅ Done", "🔥 Priority"],
                                  label_visibility="collapsed")
        if st.button("Log Task"):
            if new_task.strip():
                tasks.append({
                    "timestamp": datetime.datetime.now().strftime("%Y-%m-%d %H:%M"),
                    "task":      new_task.strip(),
                    "tag":       tag,
                    "status":    "open",
                })
                _save_task_log(tasks)
                st.success("Task logged!")
                st.rerun()

    if tasks:
        for i, t in enumerate(reversed(tasks[-20:])):   # show last 20
            status_color = "#43a047" if t.get("status") == "done" else "#c8960c"
            st.markdown(
                f"""<div style="background:#0f0f0f;border-left:3px solid {status_color};
                border-radius:0 8px 8px 0;padding:10px 14px;margin-bottom:6px;
                display:flex;justify-content:space-between;align-items:center;">
                <div>
                  <span style="color:#9aa0a6;font-size:10px;font-family:monospace;">
                  {t['timestamp']}</span>
                  <span style="margin-left:10px;font-size:11px;background:#1a1a1a;
                  padding:2px 8px;border-radius:10px;color:#c8960c;">{t['tag']}</span>
                  <div style="color:#e8eaed;font-size:13px;margin-top:4px;">{t['task']}</div>
                </div>
                </div>""",
                unsafe_allow_html=True,
            )

        if st.button("🗑️ Clear All Tasks"):
            _save_task_log([])
            st.rerun()
    else:
        st.info("No tasks logged yet.")

    st.divider()

    # ══════════════════════════════════════════════════════════
    # SECTION 5 — System Status Summary
    # ══════════════════════════════════════════════════════════
    st.markdown("### 🟢 System Status")

    issues = []
    if stats["cpu_pct"] > 85:
        issues.append("⚠️ CPU usage is very high")
    if stats["ram_pct"] > 85:
        issues.append("⚠️ RAM usage is very high")
    if stats["disk_pct"] > 90:
        issues.append("⚠️ Disk almost full")

    if issues:
        for issue in issues:
            st.warning(issue)
    else:
        st.success("✅ All systems normal — CPU, RAM, and Disk are healthy.")

    st.caption(f"Last updated: {datetime.datetime.now().strftime('%H:%M:%S')}")