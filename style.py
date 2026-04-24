import streamlit as st


def apply_theme():
    st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Google+Sans:wght@400;500;700&family=Google+Sans+Display:wght@400;700&family=Roboto+Mono:wght@400;500&display=swap');
    @import url('https://fonts.googleapis.com/css2?family=DM+Sans:opsz,wght@9..40,300;9..40,400;9..40,500;9..40,600&family=DM+Mono:wght@400;500&display=swap');

    :root {
        --bg:            #0d0d0d;
        --surface:       #1a1a1a;
        --surface2:      #111111;
        --surface3:      #222222;
        --border:        #2a2a2a;
        --border-light:  #222222;

        --blue:          #1a73e8;
        --blue-light:    #e8f0fe;
        --blue-dark:     #1557b0;
        --teal:          #00897b;
        --teal-light:    #e0f2f1;
        --green:         #1e8e3e;
        --green-light:   #e6f4ea;
        --red:           #d93025;
        --red-light:     #fce8e6;
        --amber:         #f29900;
        --amber-light:   #fef7e0;
        --purple:        #7c4dff;
        --purple-light:  #ede7f6;

        --text:          #e8eaed;
        --text-2:        #9aa0a6;
        --text-3:        #5f6368;
        --text-on-blue:  #ffffff;

        --radius-sm:     6px;
        --radius-md:     10px;
        --radius-lg:     16px;
        --radius-xl:     24px;

        --shadow-sm:     0 1px 2px rgba(0,0,0,0.4), 0 1px 3px rgba(0,0,0,0.3);
        --shadow-md:     0 2px 6px rgba(0,0,0,0.5), 0 2px 8px rgba(0,0,0,0.4);
        --shadow-lg:     0 4px 16px rgba(0,0,0,0.6), 0 2px 6px rgba(0,0,0,0.5);

        --font:          'DM Sans', 'Google Sans', sans-serif;
        --font-display:  'DM Sans', 'Google Sans Display', sans-serif;
        --font-mono:     'DM Mono', 'Roboto Mono', monospace;
    }

    html, body, [class*="css"] {
        font-family: var(--font) !important;
        background-color: var(--bg) !important;
        color: var(--text) !important;
    }

    #MainMenu, footer, header { visibility: hidden; }
    .stDeployButton { display: none !important; }

    .stApp {
        background: var(--bg) !important;
    }

    /* ── Typography ───────────────────────────────────────── */
    h1 {
        font-family: var(--font-display) !important;
        font-size: 1.75rem !important;
        font-weight: 600 !important;
        color: var(--text) !important;
        letter-spacing: -0.3px !important;
        -webkit-text-fill-color: unset !important;
        background: none !important;
        border-bottom: 2px solid var(--blue) !important;
        padding-bottom: 0.5rem !important;
        margin-bottom: 1.5rem !important;
    }

    h2 {
        font-family: var(--font-display) !important;
        font-size: 1.15rem !important;
        font-weight: 600 !important;
        color: var(--text) !important;
        letter-spacing: -0.2px !important;
        text-transform: none !important;
    }

    h3 {
        font-family: var(--font) !important;
        font-size: 0.9rem !important;
        font-weight: 600 !important;
        color: var(--text-2) !important;
        text-transform: uppercase !important;
        letter-spacing: 0.8px !important;
    }

    p, li, span {
        color: var(--text-2) !important;
        font-size: 0.875rem !important;
        line-height: 1.6 !important;
    }

    /* ── Sidebar ──────────────────────────────────────────── */
    [data-testid="stSidebar"] {
        background: var(--surface) !important;
        border-right: 1px solid var(--border) !important;
        box-shadow: var(--shadow-sm) !important;
    }

    [data-testid="stSidebar"] .stMarkdown p,
    [data-testid="stSidebar"] label,
    [data-testid="stSidebar"] .stCaption {
        font-size: 0.8rem !important;
        color: var(--text-2) !important;
    }

    [data-testid="stSidebar"] h2 {
        font-size: 0.72rem !important;
        font-weight: 600 !important;
        color: var(--text-3) !important;
        text-transform: uppercase !important;
        letter-spacing: 1.2px !important;
    }

    [data-testid="stSidebar"] hr {
        border-color: var(--border-light) !important;
    }

    /* ── Inputs ───────────────────────────────────────────── */
    .stSelectbox > div > div,
    .stTextInput > div > div > input,
    .stNumberInput > div > div > input,
    .stTextArea > div > textarea {
        background: var(--surface) !important;
        border: 1.5px solid var(--border) !important;
        border-radius: var(--radius-md) !important;
        color: var(--text) !important;
        font-family: var(--font) !important;
        font-size: 0.875rem !important;
        box-shadow: var(--shadow-sm) !important;
        transition: border-color 0.15s, box-shadow 0.15s !important;
    }

    .stSelectbox > div > div:focus-within,
    .stTextInput > div > div > input:focus,
    .stNumberInput > div > div > input:focus,
    .stTextArea > div > textarea:focus {
        border-color: var(--blue) !important;
        box-shadow: 0 0 0 3px rgba(26,115,232,0.15) !important;
        outline: none !important;
    }

    /* ── Buttons ──────────────────────────────────────────── */
    .stButton > button {
        background: var(--blue) !important;
        border: none !important;
        color: white !important;
        border-radius: var(--radius-md) !important;
        font-family: var(--font) !important;
        font-size: 0.875rem !important;
        font-weight: 500 !important;
        letter-spacing: 0.2px !important;
        padding: 0.5rem 1.4rem !important;
        box-shadow: var(--shadow-sm) !important;
        transition: all 0.15s ease !important;
    }

    .stButton > button:hover {
        background: var(--blue-dark) !important;
        box-shadow: var(--shadow-md) !important;
        transform: translateY(-1px) !important;
    }

    .stButton > button:active {
        transform: translateY(0) !important;
        box-shadow: var(--shadow-sm) !important;
    }

    .stDownloadButton > button {
        background: var(--surface) !important;
        border: 1.5px solid var(--border) !important;
        color: var(--blue) !important;
        font-weight: 500 !important;
        font-family: var(--font) !important;
        border-radius: var(--radius-md) !important;
    }

    .stDownloadButton > button:hover {
        background: var(--blue-light) !important;
        border-color: var(--blue) !important;
    }

    /* ── Metrics ──────────────────────────────────────────── */
    [data-testid="stMetric"] {
        background: var(--surface) !important;
        border: 1px solid var(--border) !important;
        border-radius: var(--radius-lg) !important;
        padding: 1rem 1.25rem !important;
        box-shadow: var(--shadow-sm) !important;
        transition: box-shadow 0.2s, transform 0.2s !important;
    }

    [data-testid="stMetric"]:hover {
        box-shadow: var(--shadow-md) !important;
        transform: translateY(-2px) !important;
    }

    [data-testid="stMetricLabel"] {
        font-size: 0.72rem !important;
        font-weight: 600 !important;
        color: var(--text-3) !important;
        text-transform: uppercase !important;
        letter-spacing: 0.8px !important;
    }

    [data-testid="stMetricValue"] {
        font-family: var(--font-display) !important;
        font-size: 2rem !important;
        font-weight: 700 !important;
        color: var(--blue) !important;
        -webkit-text-fill-color: unset !important;
        background: none !important;
    }

    [data-testid="stMetricDelta"] {
        font-size: 0.78rem !important;
    }

    /* ── Code Blocks ──────────────────────────────────────── */
    .stCodeBlock, pre, code {
        background: var(--surface2) !important;
        border: 1px solid var(--border) !important;
        border-radius: var(--radius-md) !important;
        font-family: var(--font-mono) !important;
        font-size: 0.8rem !important;
        color: var(--text) !important;
    }

    /* ── Chat Messages ────────────────────────────────────── */
    [data-testid="stChatMessage"] {
        background: var(--surface) !important;
        border: 1px solid var(--border-light) !important;
        border-radius: var(--radius-lg) !important;
        margin-bottom: 0.75rem !important;
        padding: 1rem 1.25rem !important;
        box-shadow: var(--shadow-sm) !important;
    }

    [data-testid="stChatMessage"][data-role="user"] {
        border-left: 3px solid var(--blue) !important;
        background: var(--blue-light) !important;
    }

    [data-testid="stChatMessage"][data-role="assistant"] {
        border-left: 3px solid var(--teal) !important;
    }

    /* ── Chat Input ───────────────────────────────────────── */
    [data-testid="stChatInput"] textarea {
        background: var(--surface) !important;
        border: 1.5px solid var(--border) !important;
        border-radius: var(--radius-xl) !important;
        color: var(--text) !important;
        font-family: var(--font) !important;
        font-size: 0.9rem !important;
        box-shadow: var(--shadow-md) !important;
    }

    [data-testid="stChatInput"] textarea:focus {
        border-color: var(--blue) !important;
        box-shadow: 0 0 0 3px rgba(26,115,232,0.12), var(--shadow-md) !important;
    }

    /* ── Alerts ───────────────────────────────────────────── */
    .stSuccess {
        background: var(--green-light) !important;
        border: 1px solid rgba(30,142,62,0.3) !important;
        border-radius: var(--radius-md) !important;
        color: var(--green) !important;
    }

    .stWarning {
        background: var(--amber-light) !important;
        border: 1px solid rgba(242,153,0,0.3) !important;
        border-radius: var(--radius-md) !important;
        color: #b06000 !important;
    }

    .stError {
        background: var(--red-light) !important;
        border: 1px solid rgba(217,48,37,0.3) !important;
        border-radius: var(--radius-md) !important;
        color: var(--red) !important;
    }

    .stInfo {
        background: var(--blue-light) !important;
        border: 1px solid rgba(26,115,232,0.25) !important;
        border-radius: var(--radius-md) !important;
        color: var(--blue-dark) !important;
    }

    /* ── Dataframe ────────────────────────────────────────── */
    .stDataFrame {
        border: 1px solid var(--border) !important;
        border-radius: var(--radius-md) !important;
        box-shadow: var(--shadow-sm) !important;
        overflow: hidden !important;
    }

    /* ── Progress Bar ─────────────────────────────────────── */
    .stProgress > div > div {
        background: linear-gradient(90deg, var(--blue), var(--teal)) !important;
        border-radius: 99px !important;
    }

    .stProgress > div {
        background: var(--surface3) !important;
        border-radius: 99px !important;
    }

    /* ── Slider ───────────────────────────────────────────── */
    .stSlider > div > div > div {
        background: var(--blue) !important;
    }

    /* ── Checkbox ─────────────────────────────────────────── */
    .stCheckbox > label > span {
        color: var(--text-2) !important;
        font-size: 0.875rem !important;
    }

    /* ── Divider ──────────────────────────────────────────── */
    hr {
        border-color: var(--border-light) !important;
        margin: 1.5rem 0 !important;
    }

    /* ── File Uploader ────────────────────────────────────── */
    [data-testid="stFileUploader"] {
        background: var(--surface) !important;
        border: 2px dashed var(--border) !important;
        border-radius: var(--radius-lg) !important;
        padding: 1.5rem !important;
        transition: border-color 0.2s, background 0.2s !important;
    }

    [data-testid="stFileUploader"]:hover {
        border-color: var(--blue) !important;
        background: var(--blue-light) !important;
    }

    /* ── Spinner ──────────────────────────────────────────── */
    .stSpinner > div {
        border-top-color: var(--blue) !important;
    }

    /* ── Tabs ─────────────────────────────────────────────── */
    .stTabs [data-baseweb="tab-list"] {
        background: transparent !important;
        border-bottom: 2px solid var(--border-light) !important;
        gap: 0 !important;
    }

    .stTabs [data-baseweb="tab"] {
        color: var(--text-2) !important;
        font-family: var(--font) !important;
        font-size: 0.875rem !important;
        font-weight: 500 !important;
        padding: 0.6rem 1.25rem !important;
        border-radius: var(--radius-sm) var(--radius-sm) 0 0 !important;
    }

    .stTabs [aria-selected="true"] {
        color: var(--blue) !important;
        border-bottom: 2px solid var(--blue) !important;
        background: var(--blue-light) !important;
    }

    /* ── Scrollbar ────────────────────────────────────────── */
    ::-webkit-scrollbar { width: 6px; height: 6px; }
    ::-webkit-scrollbar-track { background: var(--bg); }
    ::-webkit-scrollbar-thumb {
        background: var(--border);
        border-radius: 99px;
    }
    ::-webkit-scrollbar-thumb:hover { background: var(--blue); }

    /* ── Expander ─────────────────────────────────────────── */
    .stExpander {
        border: 1px solid var(--border) !important;
        border-radius: var(--radius-md) !important;
        background: var(--surface) !important;
        box-shadow: var(--shadow-sm) !important;
    }

    .stExpander summary {
        font-size: 0.875rem !important;
        font-weight: 500 !important;
        color: var(--text) !important;
        padding: 0.75rem 1rem !important;
    }

    /* ── Selectbox dropdown ───────────────────────────────── */
    [data-baseweb="popover"] {
        background: var(--surface) !important;
        border: 1px solid var(--border) !important;
        border-radius: var(--radius-md) !important;
        box-shadow: var(--shadow-lg) !important;
    }

    </style>
    """, unsafe_allow_html=True)


def hero_banner(
    title: str = "CHANDU",
    subtitle: str = "AI LAB",
    top_label: str = "Personal AI Operating System",
    bottom_label: str = "Intelligence · Redefined",
):
    st.markdown(f"""
    <div style="
        width: 100%;
        background: #080808;
        border-radius: 20px;
        padding: 3rem 2rem;
        text-align: center;
        position: relative;
        overflow: hidden;
        margin-bottom: 2rem;
        border: 1px solid #2a2008;
    ">
        <!-- ambient glow -->
        <div style="
            position: absolute;
            top: 50%; left: 50%;
            transform: translate(-50%, -50%);
            width: 70%; height: 60%;
            background: radial-gradient(ellipse, rgba(200,134,10,0.12) 0%, transparent 70%);
            pointer-events: none;
        "></div>

        <!-- top label -->
        <div style="
            font-family: 'DM Sans', sans-serif;
            font-size: 0.72rem;
            font-weight: 500;
            letter-spacing: 5px;
            color: #c8860a;
            opacity: 0.8;
            text-transform: uppercase;
            margin-bottom: 0.6rem;
        ">{top_label}</div>

        <!-- top divider -->
        <div style="
            width: 60%; margin: 0 auto 1.2rem auto;
            height: 1px;
            background: linear-gradient(90deg, transparent, #c8860a, transparent);
            opacity: 0.5;
        "></div>

        <!-- main title -->
        <div style="
            font-family: 'DM Sans', 'Google Sans Display', Arial Black, sans-serif;
            font-size: clamp(3rem, 10vw, 6rem);
            font-weight: 800;
            letter-spacing: 4px;
            line-height: 1.05;
            white-space: normal;
            word-break: keep-all;
            background: linear-gradient(180deg,
                #fff8c0 0%,
                #f5c518 28%,
                #c8860a 62%,
                #7a4e00 100%);
            -webkit-background-clip: text;
            -webkit-text-fill-color: transparent;
            background-clip: text;
            filter: drop-shadow(0 0 18px rgba(200,134,10,0.45));
            margin-bottom: 0.2rem;
        ">{title}</div>

        <!-- subtitle -->
        <div style="
            font-family: 'DM Sans', sans-serif;
            font-size: clamp(1.2rem, 4vw, 2.2rem);
            font-weight: 300;
            letter-spacing: 14px;
            white-space: normal;
            background: linear-gradient(180deg,
                #ffe89a 0%,
                #c8860a 55%,
                #7a4e00 100%);
            -webkit-background-clip: text;
            -webkit-text-fill-color: transparent;
            background-clip: text;
            filter: drop-shadow(0 0 10px rgba(200,134,10,0.3));
            margin-bottom: 1.2rem;
        ">{subtitle}</div>

        <!-- bottom divider -->
        <div style="
            width: 60%; margin: 0 auto 0.9rem auto;
            height: 1px;
            background: linear-gradient(90deg, transparent, #c8860a, transparent);
            opacity: 0.5;
        "></div>

        <!-- bottom tagline -->
        <div style="
            font-family: 'DM Sans', sans-serif;
            font-size: 0.72rem;
            font-weight: 400;
            letter-spacing: 4px;
            color: #c8860a;
            opacity: 0.7;
            text-transform: uppercase;
        ">{bottom_label}</div>
    </div>
    """, unsafe_allow_html=True)


def page_header(icon: str, title: str, subtitle: str = ""):
    st.markdown(f"""
    <div style="
        display: flex;
        align-items: center;
        gap: 1rem;
        padding: 1.5rem 0 1rem 0;
        margin-bottom: 1.5rem;
        border-bottom: 1px solid #2a2a2a;
    ">
        <div style="
            width: 44px; height: 44px;
            background: #1e2a3a;
            border-radius: 12px;
            display: flex; align-items: center; justify-content: center;
            font-size: 1.3rem;
            flex-shrink: 0;
        ">{icon}</div>
        <div>
            <div style="
                font-family: 'DM Sans', sans-serif;
                font-size: 1.35rem;
                font-weight: 600;
                color: #e8eaed;
                line-height: 1.25;
                letter-spacing: -0.3px;
            ">{title}</div>
            {"" if not subtitle else f'<div style="font-size:0.8rem; color:#5f6368; margin-top:3px; font-weight:400;">{subtitle}</div>'}
        </div>
    </div>
    """, unsafe_allow_html=True)


def stat_card(label: str, value: str, color: str = "#1a73e8"):
    bg_map = {
        "#1a73e8": "#e8f0fe",
        "var(--accent2)": "#ede7f6",
        "var(--accent3)": "#e0f2f1",
        "var(--warn)":    "#fef7e0",
    }
    bg = bg_map.get(color, "#e8f0fe")
    st.markdown(f"""
    <div style="
        background: #1a1a1a;
        border: 1px solid #2a2a2a;
        border-radius: 16px;
        padding: 1.25rem 1.25rem;
        text-align: left;
        box-shadow: 0 1px 2px rgba(60,64,67,0.08), 0 1px 3px rgba(60,64,67,0.12);
        transition: box-shadow 0.2s, transform 0.2s;
        position: relative;
        overflow: hidden;
    ">
        <div style="
            position: absolute; top: 0; right: 0;
            width: 80px; height: 80px;
            background: {bg};
            border-radius: 0 16px 0 80px;
            opacity: 0.6;
        "></div>
        <div style="
            font-size: 0.68rem;
            font-weight: 600;
            color: #5f6368;
            text-transform: uppercase;
            letter-spacing: 1px;
            margin-bottom: 0.5rem;
        ">{label}</div>
        <div style="
            font-family: 'DM Sans', sans-serif;
            font-size: 2rem;
            font-weight: 700;
            color: {color};
            line-height: 1;
        ">{value}</div>
    </div>
    """, unsafe_allow_html=True)


def tag(text: str, color: str = "#1a73e8"):
    bg_map = {
        "#1a73e8": "#e8f0fe",
        "#00897b": "#e0f2f1",
        "#d93025": "#fce8e6",
        "#f29900": "#fef7e0",
    }
    bg = bg_map.get(color, "#e8f0fe")
    st.markdown(f"""
    <span style="
        display: inline-block;
        background: {bg};
        color: {color};
        font-size: 0.72rem;
        font-family: 'DM Sans', sans-serif;
        font-weight: 600;
        padding: 3px 10px;
        border-radius: 99px;
        letter-spacing: 0.3px;
    ">{text}</span>
    """, unsafe_allow_html=True)