"""
floating_assistant.py  —  Floating AI Assistant with Page Context
Chandu AI Lab

Drop in CHANDU_CORE. Call once in lab_app.py after page_name is set:

    from floating_assistant import inject_floating_assistant
    inject_floating_assistant(model="gemma3:latest", current_page=page_name)
"""

import streamlit as st
import streamlit.components.v1 as components

PAGE_CONTEXTS = {
    "Game Lab": {
        "icon": "🎮",
        "tip": "You are in Game Lab! I can help you tune DQN, explain reward shaping, or debug training issues.",
        "system": "You are Chandu AI in the Game Lab of Chandu AI Lab. Help with DQN hyperparameter tuning, reward shaping, replay buffer, epsilon decay, NaN weights. Be specific and practical.",
        "chips": [
            ("Tune DQN", "My DQN is not learning well. What hyperparameters should I adjust first?"),
            ("Loss not dropping", "My training loss is not decreasing. What is wrong?"),
            ("Reward shaping", "How should I design the reward function for Snake?"),
            ("NaN weights", "My model weights are NaN after training. How do I fix this?"),
            ("Speed up training", "How can I make my DQN train faster?"),
            ("Epsilon decay", "What is the best epsilon decay strategy for DQN?"),
        ],
    },
    "Neural Network Visualiser": {
        "icon": "🧠",
        "tip": "You are in the Neural Network Visualiser! Ask me to explain any layer, activation, or node colors.",
        "system": "You are Chandu AI in the Neural Network Visualiser of Chandu AI Lab. Help with layers, activation values, node colors, Q-values, dead neurons, backpropagation.",
        "chips": [
            ("Node colors", "What do the node colors in the visualiser mean?"),
            ("Q-values", "How are Q-values computed in the output layer?"),
            ("Dead neurons", "Some of my nodes are always dark. What does that mean?"),
            ("Edge weights", "How do I read the edge weights in the visualisation?"),
            ("Activation fns", "What is the difference between relu and sigmoid activation?"),
            ("Backprop", "Explain how backpropagation flows through this network"),
        ],
    },
    "GitHub": {
        "icon": "🐙",
        "tip": "You are in the GitHub tool! Ask me about git commands, commit messages, or branching.",
        "system": "You are Chandu AI in the GitHub tool of Chandu AI Lab. Help with git commands, commit messages, branching, merge vs rebase, .gitignore, README writing.",
        "chips": [
            ("Commit message", "What is a good commit message format? Show me examples."),
            ("Branching", "What branching strategy should I use for a solo project?"),
            ("Merge vs Rebase", "Should I use merge or rebase? What is the difference?"),
            (".gitignore", "What should I put in my .gitignore for a Python ML project?"),
            ("Undo commit", "How do I undo my last commit without losing changes?"),
            ("Good README", "How should I write a good README for my AI project?"),
        ],
    },
    "Tool System": {
        "icon": "🛠️",
        "tip": "You are in the Tool System! Ask me to write scripts, explain commands, or suggest automations.",
        "system": "You are Chandu AI in the Tool System of Chandu AI Lab. Help with Python automation scripts, terminal commands, file management, os module, shutil, Windows automation.",
        "chips": [
            ("Organise files", "Write a Python script to organise my Downloads folder by file type"),
            ("Find duplicates", "Write a script to find duplicate files on my PC"),
            ("Disk usage", "Write a script to show which folders use the most disk space"),
            ("Automate task", "I want to automate renaming files in a folder. How?"),
            ("Terminal command", "What command shows all running processes in Windows?"),
            ("Backup script", "Write a Python script to backup my CHANDU_CORE folder"),
        ],
    },
    "AI File Assistant": {
        "icon": "🤖",
        "tip": "You are in the AI File Assistant! Select a file and I will help you summarize, fix bugs, explain, or refactor it.",
        "system": "You are Chandu AI in the AI File Assistant of Chandu AI Lab. Help with choosing the right action for file types, code review, refactoring, Python best practices, debugging.",
        "chips": [
            ("Which action?", "Which AI action should I use for a Python file with errors?"),
            ("CSV analysis", "What can AI tell me about a CSV dataset file?"),
            ("Security tips", "What are common Python security issues I should check for?"),
            ("Refactor tips", "What makes Python code cleaner? Give me key refactoring rules."),
            ("Batch analysis", "When should I use Batch Analysis instead of Single File?"),
            ("Prompt tips", "How do I write a good custom prompt for my Python file?"),
        ],
    },
    "System Dashboard": {
        "icon": "🖥️",
        "tip": "You are on the System Dashboard! Ask me about CPU or RAM usage, or how to optimize performance.",
        "system": "You are Chandu AI in the System Dashboard of Chandu AI Lab. Help with CPU/RAM metrics, process monitoring, Ollama resource usage, Python ML training optimization.",
        "chips": [
            ("High CPU", "My CPU is at 90 percent during training. Is that normal?"),
            ("RAM usage", "How much RAM does DQN training typically use?"),
            ("Speed up", "How can I reduce CPU and RAM usage during model training?"),
            ("Ollama RAM", "How much RAM does Ollama use with gemma3?"),
            ("Monitor", "What system metrics should I watch during ML training?"),
            ("Free memory", "How do I free up RAM on Windows without restarting?"),
        ],
    },
    "__default__": {
        "icon": "🤖",
        "tip": "Hi Chandrajit! Ask me anything about your AI Lab, code, or machine learning.",
        "system": "You are Chandu AI, a helpful assistant in Chandu AI Lab built by Chandrajit. Help with machine learning, Python, reinforcement learning, neural networks, debugging, and AI concepts. Be concise and practical.",
        "chips": [
            ("Next feature", "What should I build next in my AI lab?"),
            ("Explain RL", "Explain how reinforcement learning works simply"),
            ("Debug NaN", "How do I debug NaN loss in neural network training?"),
            ("Python tips", "Give me 5 Python tips to write better ML code"),
            ("ML ideas", "What ML experiments should I try with my current setup?"),
            ("Learn next", "What AI or ML topic should I learn next?"),
        ],
    },
}


def _get_context(page_name):
    if page_name in PAGE_CONTEXTS:
        return PAGE_CONTEXTS[page_name]
    for key in PAGE_CONTEXTS:
        if key != "__default__" and key.lower() in page_name.lower():
            return PAGE_CONTEXTS[key]
    return PAGE_CONTEXTS["__default__"]


def inject_floating_assistant(
    model="gemma3:latest",
    ollama_url="http://localhost:11434",
    current_page="",
    accent="#c8960c",
):
    ctx        = _get_context(current_page)
    p_icon     = ctx["icon"]
    p_tip      = ctx["tip"].replace("'", "\\'")
    system_str = ctx["system"].replace("'", "\\'")
    page_label = (current_page or "Chandu AI Lab").replace("'", "\\'")

    chips_parts = []
    for label, prompt in ctx["chips"]:
        chips_parts.append("['" + label.replace("'", "\\'") + "','" + prompt.replace("'", "\\'") + "']")
    chips_js = "[" + ",".join(chips_parts) + "]"

    # ── Step 1: inject HTML + CSS via st.markdown ──────────────
    st.markdown("""
<style>
#chandu-badge {
  position: fixed; bottom: 94px; right: 28px;
  background: #141414; border: 1px solid #2a2a2a; border-radius: 20px;
  padding: 3px 10px; font-size: 10px; color: #666; white-space: nowrap;
  z-index: 99997; font-family: 'Segoe UI', sans-serif; pointer-events: none;
}
#chandu-fab {
  position: fixed; bottom: 28px; right: 28px;
  width: 58px; height: 58px; border-radius: 50%;
  background: linear-gradient(135deg, """ + accent + """, #b07d0a);
  border: none; cursor: pointer;
  box-shadow: 0 4px 20px rgba(200,150,12,.45);
  z-index: 99999; display: flex; align-items: center;
  justify-content: center; font-size: 26px;
  transition: transform .2s, box-shadow .2s;
  animation: cfab 3s ease-in-out infinite;
}
#chandu-fab:hover { transform: scale(1.1); box-shadow: 0 6px 30px rgba(200,150,12,.7); }
@keyframes cfab {
  0%,100% { box-shadow: 0 4px 20px rgba(200,150,12,.45); }
  50%      { box-shadow: 0 4px 36px rgba(200,150,12,.8); }
}
#chandu-panel {
  position: fixed; bottom: 100px; right: 28px;
  width: 370px; max-height: 560px;
  background: #0f0f0f; border: 1px solid #232323; border-radius: 18px;
  box-shadow: 0 12px 50px rgba(0,0,0,.8);
  z-index: 99998; display: none; flex-direction: column; overflow: hidden;
  font-family: 'Segoe UI', sans-serif;
}
.cpanel-open { animation: cpanelin .28s cubic-bezier(.34,1.4,.64,1) forwards; }
@keyframes cpanelin {
  from { transform: translateY(24px) scale(.94); opacity: 0; }
  to   { transform: translateY(0) scale(1); opacity: 1; }
}
#chandu-hdr {
  display: flex; align-items: center; gap: 10px;
  padding: 13px 15px; background: #141414;
  border-bottom: 1px solid #1e1e1e; flex-shrink: 0;
}
#chandu-hicon {
  width: 36px; height: 36px; border-radius: 50%;
  background: linear-gradient(135deg, """ + accent + """, #b07d0a);
  display: flex; align-items: center; justify-content: center;
  font-size: 18px; flex-shrink: 0;
}
#chandu-htitle { font-size: 13px; font-weight: 700; color: #e8eaed; }
#chandu-hsub   { font-size: 10px; color: #444; }
#chandu-dot {
  width: 8px; height: 8px; border-radius: 50%;
  background: #43a047; box-shadow: 0 0 6px #43a047; flex-shrink: 0;
}
#chandu-x {
  background: none; border: none; color: #444;
  font-size: 18px; cursor: pointer; padding: 0; line-height: 1;
}
#chandu-x:hover { color: #e8eaed; }
#chandu-ctxbar {
  display: flex; align-items: center; gap: 8px;
  padding: 7px 14px; background: #0a0a0a;
  border-bottom: 1px solid #181818; flex-shrink: 0;
}
#chandu-ctxlabel {
  font-size: 10px; color: """ + accent + """; font-weight: 700;
  text-transform: uppercase; letter-spacing: .5px;
}
#chandu-ctxdesc { font-size: 10px; color: #333; margin-left: auto; }
#chandu-chips {
  display: flex; gap: 5px; padding: 8px 12px 0;
  flex-wrap: wrap; flex-shrink: 0;
}
.cchip {
  background: #161616; border: 1px solid #242424; border-radius: 20px;
  padding: 4px 9px; font-size: 10px; color: #777;
  cursor: pointer; transition: all .15s; white-space: nowrap;
}
.cchip:hover {
  background: #1e1e1e; color: #e8eaed;
  border-color: """ + accent + """; transform: translateY(-1px);
}
#chandu-msgs {
  flex: 1; overflow-y: auto; padding: 10px 12px;
  display: flex; flex-direction: column; gap: 8px; scroll-behavior: smooth;
}
#chandu-msgs::-webkit-scrollbar { width: 3px; }
#chandu-msgs::-webkit-scrollbar-thumb { background: #232323; border-radius: 4px; }
.cmsg-user {
  align-self: flex-end; max-width: 86%;
  background: linear-gradient(135deg,""" + accent + """2a,""" + accent + """15);
  border: 1px solid """ + accent + """38; color: #e8eaed;
  border-radius: 12px 12px 2px 12px; padding: 8px 11px;
  font-size: 12px; line-height: 1.5;
}
.cmsg-ai {
  align-self: flex-start; max-width: 92%;
  background: #161616; border: 1px solid #202020; color: #d0d2d8;
  border-radius: 2px 12px 12px 12px; padding: 8px 11px;
  font-size: 12px; line-height: 1.65; white-space: pre-wrap;
}
.cmsg-tip {
  align-self: flex-start; max-width: 92%;
  background: """ + accent + """0f; border: 1px solid """ + accent + """25; color: #999;
  border-radius: 2px 12px 12px 12px; padding: 8px 11px;
  font-size: 11px; line-height: 1.55;
}
.cmsg-sys {
  align-self: center; color: #333; font-size: 10px;
  font-style: italic; text-align: center;
}
.ctyping {
  align-self: flex-start; background: #161616; border: 1px solid #202020;
  border-radius: 2px 12px 12px 12px;
  padding: 10px 14px; display: flex; gap: 4px; align-items: center;
}
.cdot {
  width: 6px; height: 6px; border-radius: 50%;
  background: """ + accent + """; animation: cbounce 1.2s infinite;
}
.cdot:nth-child(2) { animation-delay: .2s; }
.cdot:nth-child(3) { animation-delay: .4s; }
@keyframes cbounce {
  0%,60%,100% { transform: translateY(0); opacity: .3; }
  30%          { transform: translateY(-5px); opacity: 1; }
}
#chandu-ibar {
  display: flex; gap: 7px; padding: 10px 12px;
  border-top: 1px solid #181818; flex-shrink: 0; background: #0a0a0a;
}
#chandu-inp {
  flex: 1; background: #141414; border: 1px solid #242424;
  border-radius: 10px; padding: 7px 11px; color: #e8eaed;
  font-size: 12px; resize: none; outline: none; font-family: inherit;
  line-height: 1.4; max-height: 80px; overflow-y: auto;
  transition: border-color .15s;
}
#chandu-inp:focus { border-color: """ + accent + """; }
#chandu-inp::placeholder { color: #303030; }
#chandu-send {
  width: 34px; height: 34px; border-radius: 9px;
  background: linear-gradient(135deg, """ + accent + """, #b07d0a);
  border: none; cursor: pointer; color: #000; font-size: 15px;
  display: flex; align-items: center; justify-content: center;
  align-self: flex-end; flex-shrink: 0; font-weight: 700;
}
#chandu-send:hover   { transform: scale(1.08); }
#chandu-send:disabled { opacity: .35; cursor: not-allowed; transform: none; }
#chandu-clr {
  background: none; border: none; color: #2a2a2a; font-size: 11px;
  cursor: pointer; padding: 0 3px; align-self: flex-end;
}
#chandu-clr:hover { color: #555; }
</style>

<div id="chandu-badge">""" + p_icon + " " + page_label + """</div>

<button id="chandu-fab">""" + p_icon + """</button>

<div id="chandu-panel">
  <div id="chandu-hdr">
    <div id="chandu-hicon">""" + p_icon + """</div>
    <div style="flex:1">
      <div id="chandu-htitle">Chandu AI</div>
      <div id="chandu-hsub">""" + page_label + " &middot; " + model + """</div>
    </div>
    <div id="chandu-dot"></div>
    <button id="chandu-x">&#x2715;</button>
  </div>
  <div id="chandu-ctxbar">
    <span>""" + p_icon + """</span>
    <span id="chandu-ctxlabel">""" + page_label + """</span>
    <span id="chandu-ctxdesc">context active</span>
  </div>
  <div id="chandu-chips"></div>
  <div id="chandu-msgs"></div>
  <div id="chandu-ibar">
    <button id="chandu-clr">&#x1F5D1;</button>
    <textarea id="chandu-inp" rows="1" placeholder="Ask about """ + page_label + """... (Enter to send)"></textarea>
    <button id="chandu-send">&#x27A4;</button>
  </div>
</div>
""", unsafe_allow_html=True)

    # ── Step 2: inject JS via components.html using window.parent ──
    # This bypasses Streamlit's script-tag stripping entirely.
    js_code = (
        "<script>"
        "(function() {"
        "  var doc    = window.parent.document;"
        "  var OLLAMA = '" + ollama_url + "';"
        "  var MODEL  = '" + model + "';"
        "  var PAGE   = '" + page_label + "';"
        "  var SYS    = '" + system_str + "';"
        "  var TIP    = '" + p_tip + "';"
        "  var CHIPS  = " + chips_js + ";"
        "  var isOpen = false, busy = false, hist = [], tipDone = false;"
        ""
        "  function init() {"
        "    var chipsEl = doc.getElementById('chandu-chips');"
        "    if (chipsEl) {"
        "      CHIPS.forEach(function(c) {"
        "        var el = doc.createElement('span');"
        "        el.className = 'cchip';"
        "        el.textContent = c[0];"
        "        el.addEventListener('click', function() { quickSend(c[1]); });"
        "        chipsEl.appendChild(el);"
        "      });"
        "    }"
        "    var fab  = doc.getElementById('chandu-fab');"
        "    var xbtn = doc.getElementById('chandu-x');"
        "    var clr  = doc.getElementById('chandu-clr');"
        "    var send = doc.getElementById('chandu-send');"
        "    var inp  = doc.getElementById('chandu-inp');"
        "    if (fab)  fab.addEventListener('click', toggle);"
        "    if (xbtn) xbtn.addEventListener('click', toggle);"
        "    if (clr)  clr.addEventListener('click', clearChat);"
        "    if (send) send.addEventListener('click', sendMsg);"
        "    if (inp) {"
        "      inp.addEventListener('keydown', function(e) {"
        "        if (e.key === 'Enter' && !e.shiftKey) { e.preventDefault(); sendMsg(); }"
        "      });"
        "      inp.addEventListener('input', function() {"
        "        this.style.height = 'auto';"
        "        this.style.height = Math.min(this.scrollHeight, 80) + 'px';"
        "      });"
        "    }"
        "    checkStatus();"
        "  }"
        ""
        "  function toggle() {"
        "    isOpen = !isOpen;"
        "    var panel = doc.getElementById('chandu-panel');"
        "    var badge = doc.getElementById('chandu-badge');"
        "    if (!panel) return;"
        "    if (isOpen) {"
        "      panel.style.display = 'flex';"
        "      panel.classList.add('cpanel-open');"
        "      if (badge) badge.style.display = 'none';"
        "      if (!tipDone) { tipDone = true; setTimeout(function() { addMsg('tip', '💡 ' + TIP); }, 200); }"
        "      setTimeout(function() { var i = doc.getElementById('chandu-inp'); if (i) i.focus(); }, 150);"
        "    } else {"
        "      panel.style.display = 'none';"
        "      panel.classList.remove('cpanel-open');"
        "      if (badge) badge.style.display = 'block';"
        "    }"
        "  }"
        ""
        "  function quickSend(text) {"
        "    var inp = doc.getElementById('chandu-inp');"
        "    if (inp) inp.value = text;"
        "    sendMsg();"
        "  }"
        ""
        "  function clearChat() {"
        "    hist = []; tipDone = false;"
        "    var msgs = doc.getElementById('chandu-msgs');"
        "    if (msgs) msgs.innerHTML = '';"
        "    addMsg('sys', 'Cleared · ' + PAGE + ' context still active');"
        "  }"
        ""
        "  function addMsg(role, text) {"
        "    var msgs = doc.getElementById('chandu-msgs');"
        "    if (!msgs) return;"
        "    var d = doc.createElement('div');"
        "    d.className = role === 'user' ? 'cmsg-user' : role === 'ai' ? 'cmsg-ai' : role === 'tip' ? 'cmsg-tip' : 'cmsg-sys';"
        "    d.textContent = text;"
        "    msgs.appendChild(d);"
        "    msgs.scrollTop = msgs.scrollHeight;"
        "  }"
        ""
        "  function showTyping() {"
        "    var msgs = doc.getElementById('chandu-msgs');"
        "    if (!msgs) return;"
        "    var d = doc.createElement('div');"
        "    d.className = 'ctyping'; d.id = 'ctyping';"
        "    d.innerHTML = '<div class=\"cdot\"></div><div class=\"cdot\"></div><div class=\"cdot\"></div>';"
        "    msgs.appendChild(d);"
        "    msgs.scrollTop = msgs.scrollHeight;"
        "  }"
        ""
        "  function hideTyping() {"
        "    var e = doc.getElementById('ctyping');"
        "    if (e) e.remove();"
        "  }"
        ""
        "  function sendMsg() {"
        "    var inp = doc.getElementById('chandu-inp');"
        "    if (!inp) return;"
        "    var text = inp.value.trim();"
        "    if (!text || busy) return;"
        "    inp.value = ''; inp.style.height = 'auto';"
        "    busy = true;"
        "    var sendBtn = doc.getElementById('chandu-send');"
        "    if (sendBtn) sendBtn.disabled = true;"
        "    addMsg('user', text);"
        "    hist.push({ role: 'user', content: text });"
        "    showTyping();"
        "    var messages = [{ role: 'system', content: SYS }].concat(hist.slice(-10));"
        "    fetch(OLLAMA + '/api/chat', {"
        "      method: 'POST',"
        "      headers: { 'Content-Type': 'application/json' },"
        "      body: JSON.stringify({ model: MODEL, messages: messages, stream: false })"
        "    })"
        "    .then(function(r) {"
        "      hideTyping();"
        "      if (!r.ok) { addMsg('ai', 'Error ' + r.status + '. Run: ollama serve'); return null; }"
        "      return r.json();"
        "    })"
        "    .then(function(data) {"
        "      if (!data) return;"
        "      var reply = (data.message && data.message.content) ? data.message.content : (data.response || 'No response.');"
        "      hist.push({ role: 'assistant', content: reply });"
        "      addMsg('ai', reply);"
        "    })"
        "    .catch(function(err) {"
        "      hideTyping();"
        "      addMsg('ai', 'Cannot reach Ollama. Run: ollama serve');"
        "    })"
        "    .finally(function() {"
        "      busy = false;"
        "      var sb = doc.getElementById('chandu-send');"
        "      if (sb) sb.disabled = false;"
        "      var i = doc.getElementById('chandu-inp');"
        "      if (i) i.focus();"
        "    });"
        "  }"
        ""
        "  function checkStatus() {"
        "    fetch(OLLAMA + '/api/tags')"
        "    .then(function(r) { if (!r.ok) throw new Error(); })"
        "    .catch(function() {"
        "      var dot = doc.getElementById('chandu-dot');"
        "      if (dot) { dot.style.background = '#e53935'; dot.style.boxShadow = '0 0 6px #e53935'; }"
        "      var sub = doc.getElementById('chandu-hsub');"
        "      if (sub) sub.textContent = 'Ollama offline - run: ollama serve';"
        "    });"
        "  }"
        ""
        "  setTimeout(init, 500);"
        "})();"
        "</script>"
    )

    components.html(js_code, height=0)