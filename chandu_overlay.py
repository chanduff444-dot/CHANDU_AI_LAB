"""
chandu_overlay.py
──────────────────
Floating always-on-top overlay at bottom of Windows screen.
Run this separately: python chandu_overlay.py

- Type any task and press Enter or click Run
- Watch live step log as agent works on your real desktop
- Add/change task anytime — even while agent is running
- Stop anytime with the Stop button
"""

import tkinter as tk
from tkinter import scrolledtext
import threading
import sys
import os

# Make sure core is importable
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from core.screen_agent_engine import run_agent

# ── Colours ────────────────────────────────────────────────────
BG        = "#0d0d0d"
BG2       = "#141414"
BG3       = "#1a1a1a"
BORDER    = "#2a2a2a"
TEXT      = "#e0ddd5"
TEXT2     = "#888"
BLUE      = "#378add"
GREEN     = "#4a8c6f"
AMBER     = "#c8b560"
RED       = "#c05050"
FONT_MAIN = ("Segoe UI", 10)
FONT_MONO = ("Consolas", 9)
FONT_BOLD = ("Segoe UI", 10, "bold")

STATUS_COLORS = {
    "start":     BLUE,
    "seeing":    TEXT2,
    "thinking":  AMBER,
    "executing": TEXT,
    "done_step": GREEN,
    "complete":  GREEN,
    "error":     RED,
    "max_steps": AMBER,
}

STATUS_PREFIX = {
    "start":     "▶ ",
    "seeing":    "👁 ",
    "thinking":  "🧠 ",
    "executing": "⚙️  ",
    "done_step": "✅ ",
    "complete":  "🎯 ",
    "error":     "❌ ",
    "max_steps": "⚠️  ",
}


class ChanduOverlay:
    def __init__(self):
        self.root        = tk.Tk()
        self.agent_thread = None
        self.stop_flag   = threading.Event()
        self._build_ui()
        self._position_window()

    # ── Build UI ───────────────────────────────────────────────
    def _build_ui(self):
        root = self.root
        root.title("Chandu Agent")
        root.configure(bg=BG)
        root.resizable(True, False)
        root.attributes("-topmost", True)       # always on top
        root.attributes("-alpha", 0.96)         # slight transparency
        root.overrideredirect(False)

        # ── Title bar row ──────────────────────────────────────
        title_frame = tk.Frame(root, bg=BG, pady=4, padx=8)
        title_frame.pack(fill="x")

        tk.Label(
            title_frame, text="🤖 Chandu Agent",
            bg=BG, fg=BLUE, font=FONT_BOLD
        ).pack(side="left")

        self.status_label = tk.Label(
            title_frame, text="Ready",
            bg=BG, fg=TEXT2, font=FONT_MAIN
        )
        self.status_label.pack(side="left", padx=12)

        # minimize / close
        tk.Button(
            title_frame, text="─", bg=BG, fg=TEXT2,
            font=FONT_MAIN, bd=0, padx=6,
            command=self._minimize,
            activebackground=BG3, activeforeground=TEXT
        ).pack(side="right")

        tk.Button(
            title_frame, text="✕", bg=BG, fg=TEXT2,
            font=FONT_MAIN, bd=0, padx=6,
            command=root.destroy,
            activebackground=BG3, activeforeground=RED
        ).pack(side="right")

        # ── Log area ───────────────────────────────────────────
        log_frame = tk.Frame(root, bg=BG, padx=6)
        log_frame.pack(fill="both", expand=True)

        self.log = scrolledtext.ScrolledText(
            log_frame,
            height=8,
            bg=BG2, fg=TEXT,
            font=FONT_MONO,
            bd=0, relief="flat",
            wrap="word",
            state="disabled",
            insertbackground=TEXT,
        )
        self.log.pack(fill="both", expand=True)

        # colour tags
        for key, col in STATUS_COLORS.items():
            self.log.tag_config(key, foreground=col)

        # ── Divider ────────────────────────────────────────────
        tk.Frame(root, bg=BORDER, height=1).pack(fill="x")

        # ── Input row ──────────────────────────────────────────
        input_frame = tk.Frame(root, bg=BG, padx=6, pady=6)
        input_frame.pack(fill="x")

        self.task_var = tk.StringVar()
        self.task_entry = tk.Entry(
            input_frame,
            textvariable=self.task_var,
            bg=BG3, fg=TEXT,
            font=FONT_MAIN,
            bd=0, relief="flat",
            insertbackground=TEXT,
        )
        self.task_entry.pack(side="left", fill="x", expand=True,
                             ipady=6, padx=(0, 6))
        self.task_entry.bind("<Return>", lambda e: self._run_task())
        self.task_entry.focus()

        self.run_btn = tk.Button(
            input_frame, text="▶ Run",
            bg=BLUE, fg="#ffffff",
            font=FONT_BOLD, bd=0,
            padx=12, pady=4,
            command=self._run_task,
            activebackground="#2a6db5",
            activeforeground="#ffffff",
            cursor="hand2",
        )
        self.run_btn.pack(side="left")

        self.stop_btn = tk.Button(
            input_frame, text="■ Stop",
            bg=BG3, fg=RED,
            font=FONT_BOLD, bd=0,
            padx=10, pady=4,
            command=self._stop_task,
            activebackground=BG3,
            activeforeground=RED,
            cursor="hand2",
            state="disabled",
        )
        self.stop_btn.pack(side="left", padx=(6, 0))

        # ── Quick task chips ───────────────────────────────────
        chips_frame = tk.Frame(root, bg=BG, padx=6, pady=4)
        chips_frame.pack(fill="x")

        quick_tasks = [
            "What is on my screen?",
            "Open Notepad and write Hello World and save it",
            "Open YouTube",
            "Take a screenshot",
            "Open VS Code",
        ]
        for qt in quick_tasks:
            short = qt[:28] + "…" if len(qt) > 28 else qt
            tk.Button(
                chips_frame, text=short,
                bg=BG3, fg=TEXT2,
                font=("Segoe UI", 8), bd=0,
                padx=6, pady=2,
                command=lambda t=qt: self._set_task(t),
                activebackground=BG2,
                activeforeground=TEXT,
                cursor="hand2",
                relief="flat",
            ).pack(side="left", padx=(0, 4))

    # ── Window positioning ─────────────────────────────────────
    def _position_window(self):
        self.root.update_idletasks()
        screen_w = self.root.winfo_screenwidth()
        screen_h = self.root.winfo_screenheight()
        win_w    = 860
        win_h    = 300
        x = (screen_w - win_w) // 2
        y = screen_h - win_h - 48      # 48px above taskbar
        self.root.geometry(f"{win_w}x{win_h}+{x}+{y}")
        self.root.minsize(500, 200)

    # ── Log helpers ────────────────────────────────────────────
    def _log(self, message: str, tag: str = ""):
        prefix = STATUS_PREFIX.get(tag, "")
        self.log.configure(state="normal")
        self.log.insert("end", prefix + message + "\n", tag)
        self.log.see("end")
        self.log.configure(state="disabled")

    def _clear_log(self):
        self.log.configure(state="normal")
        self.log.delete("1.0", "end")
        self.log.configure(state="disabled")

    def _set_status(self, text: str, color: str = TEXT2):
        self.status_label.configure(text=text, fg=color)

    # ── Task control ───────────────────────────────────────────
    def _set_task(self, text: str):
        self.task_var.set(text)
        self.task_entry.focus()

    def _run_task(self):
        task = self.task_var.get().strip()
        if not task:
            return

        # If agent already running, queue new task (stop current first)
        if self.agent_thread and self.agent_thread.is_alive():
            self._stop_task()

        self.stop_flag.clear()
        self._clear_log()
        self._log(f"Task: {task}", "start")
        self._set_status("Running...", AMBER)
        self.run_btn.configure(state="disabled")
        self.stop_btn.configure(state="normal")

        self.agent_thread = threading.Thread(
            target=self._agent_loop, args=(task,), daemon=True
        )
        self.agent_thread.start()

    def _stop_task(self):
        self.stop_flag.set()
        self._log("Stopped by user.", "error")
        self._set_status("Stopped", RED)
        self.run_btn.configure(state="normal")
        self.stop_btn.configure(state="disabled")

    def _agent_loop(self, task: str):
        try:
            for step_data in run_agent(task):
                if self.stop_flag.is_set():
                    break

                status  = step_data.get("status", "")
                message = step_data.get("message", "")

                # Update UI from main thread
                self.root.after(0, self._log, message, status)

                if status in ("complete", "error", "max_steps"):
                    color = GREEN if status == "complete" else RED
                    self.root.after(0, self._set_status,
                                    "Done ✓" if status == "complete" else "Error", color)
                    break

        except Exception as e:
            self.root.after(0, self._log, f"Agent crashed: {e}", "error")
            self.root.after(0, self._set_status, "Error", RED)

        finally:
            self.root.after(0, self.run_btn.configure, {"state": "normal"})
            self.root.after(0, self.stop_btn.configure, {"state": "disabled"})

    # ── Minimize ───────────────────────────────────────────────
    def _minimize(self):
        self.root.iconify()

    # ── Start ──────────────────────────────────────────────────
    def run(self):
        self.root.mainloop()


# ── Entry point ────────────────────────────────────────────────
if __name__ == "__main__":
    print("Starting Chandu Agent overlay...")
    print("Tip: Keep this running alongside Streamlit.")
    ChanduOverlay().run()