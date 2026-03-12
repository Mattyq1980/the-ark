"""
lcars_theme.py — LCARS-inspired theme for the FT&E Governor interface
─────────────────────────────────────────────────────────────────────
Star Trek control panel aesthetic.  Amber / gold on black.
Import and call apply_theme() after st.set_page_config().
"""

import streamlit as st

# ── Colour Palette ────────────────────────────────────────────────────────────
AMBER      = "#FF9900"
GOLD       = "#FFCC66"
PEACH      = "#FFAA66"
MAUVE      = "#CC6699"
LAVENDER   = "#9999FF"
TEAL       = "#33CCAA"
ICE        = "#99CCFF"
TAN        = "#CC9966"
TEXT       = "#FFCC99"
DIM        = "#665533"
BG         = "#000000"
PANEL      = "#080810"
BORDER     = "#332200"
OK         = "#33CC99"
WARN       = "#FFCC00"
ALERT      = "#FF6633"


def apply_theme():
    """Inject full LCARS CSS into the current Streamlit page."""
    st.markdown(_CSS, unsafe_allow_html=True)


def lcars_header(title: str, subtitle: str = ""):
    """Render an LCARS-style header bar with rounded elbow + pill."""
    sub_html = (
        f'<span class="lcars-sub">{subtitle}</span>' if subtitle else ""
    )
    st.markdown(f"""
    <div class="lcars-bar">
        <div class="lcars-elbow"></div>
        <div class="lcars-title-block">
            <span class="lcars-title">{title}</span>
            {sub_html}
        </div>
        <div class="lcars-pill"></div>
    </div>
    """, unsafe_allow_html=True)


def lcars_section(label: str):
    """Render an LCARS section divider with dot + line."""
    st.markdown(
        f'<div class="lcars-section">'
        f'<div class="lcars-section-dot"></div>'
        f'<span class="lcars-section-label">{label}</span>'
        f'<div class="lcars-section-line"></div>'
        f'</div>',
        unsafe_allow_html=True,
    )


# ═══════════════════════════════════════════════════════════════════════════════
#  CSS
# ═══════════════════════════════════════════════════════════════════════════════
_CSS = """<style>
/* ═══════════════════════════════════════════════════════════════
   LCARS THEME — FT&E Governor
   Star Trek-inspired control panel aesthetic
   ═══════════════════════════════════════════════════════════════ */

/* ── Fonts ── */
@import url('https://fonts.googleapis.com/css2?family=Antonio:wght@400;700&family=Share+Tech+Mono&display=swap');

/* ── Root backgrounds ── */
html, body { background: #000 !important; }
[data-testid="stAppViewContainer"],
[data-testid="stMain"],
.stMainBlockContainer,
.main, .main .block-container {
    background: #000000 !important;
}
[data-testid="stHeader"] {
    background: transparent !important;
}
[data-testid="stSidebar"],
[data-testid="stSidebar"] > div,
[data-testid="stSidebar"] [data-testid="stSidebarContent"] {
    background: #050508 !important;
    border-right: 2px solid #1a1100 !important;
}
/* Sidebar LCARS gradient bar */
[data-testid="stSidebar"] [data-testid="stSidebarContent"]::before {
    content: '';
    display: block;
    height: 5px;
    background: linear-gradient(90deg, #FF9900 0%, #CC6699 45%, #9999FF 100%);
    border-radius: 3px;
    margin: 0 0 16px 0;
}
footer, #MainMenu { display: none !important; }

/* ── Global typography ── */
html, body, .stMarkdown, .stMarkdown p, label, li, td, th,
[data-testid="stText"], .stTextInput label,
div[data-testid="stMarkdownContainer"] p,
div[data-testid="stMarkdownContainer"] li {
    color: #FFCC99 !important;
    font-family: 'Share Tech Mono', 'Consolas', 'Courier New', monospace !important;
}
h1, h2, h3 {
    font-family: 'Antonio', 'Arial Narrow', sans-serif !important;
    color: #FF9900 !important;
    letter-spacing: 0.12em !important;
    text-transform: uppercase !important;
    font-weight: 700 !important;
}
h1 { font-size: 2em !important; }
h4, h5, h6 {
    font-family: 'Antonio', sans-serif !important;
    color: #CC9966 !important;
    letter-spacing: 0.08em !important;
    text-transform: uppercase !important;
}
a { color: #9999FF !important; }
a:hover { color: #FFCC66 !important; }
hr, [data-testid="stDivider"] {
    border-color: #1a1100 !important;
}

/* ── Block container + responsive max-width for large screens ── */
.block-container {
    padding-top: 1rem !important;
    padding-bottom: 6rem !important;
    max-width: 1600px !important;
    margin-left: auto !important;
    margin-right: auto !important;
}
/* Ensure the fixed bottom bar has enough room and no clipping */
[data-testid="stBottom"] {
    bottom: 0 !important;
    padding-bottom: 8px !important;
    padding-top: 8px !important;
    z-index: 999 !important;
}
/* Keep columns from stretching absurdly on huge displays */
@media (min-width: 2000px) {
    .block-container {
        max-width: 1800px !important;
    }
}
@media (min-width: 2800px) {
    .block-container {
        max-width: 2200px !important;
    }
}
/* Prevent elements from collapsing on zoom-in */
@media (max-width: 700px) {
    .block-container {
        padding-left: 0.5rem !important;
        padding-right: 0.5rem !important;
    }
    .lcars-bar { height: 40px !important; }
    .lcars-elbow { width: 50px !important; min-width: 50px !important; }
    .lcars-title { font-size: 1em !important; }
    .lcars-pill { min-width: 20px !important; }
}

/* ── Buttons ── */
.stButton > button,
button[data-testid="stBaseButton-secondary"] {
    background: #0a0a14 !important;
    border: 1px solid #FF9900 !important;
    color: #FF9900 !important;
    border-radius: 20px !important;
    font-family: 'Antonio', sans-serif !important;
    letter-spacing: 0.1em !important;
    text-transform: uppercase !important;
    font-weight: 600 !important;
    transition: all 0.25s ease !important;
}
.stButton > button:hover,
button[data-testid="stBaseButton-secondary"]:hover {
    background: #1a1200 !important;
    border-color: #FFCC66 !important;
    color: #FFCC66 !important;
    box-shadow: 0 0 15px rgba(255,153,0,0.25) !important;
}
button[data-testid="stBaseButton-primary"],
.stButton > button[kind="primary"] {
    background: linear-gradient(135deg, #FF9900 0%, #CC7700 100%) !important;
    color: #000000 !important;
    border-color: #FF9900 !important;
    font-weight: 700 !important;
}
button[data-testid="stBaseButton-primary"]:hover {
    background: linear-gradient(135deg, #FFCC66 0%, #FF9900 100%) !important;
    box-shadow: 0 0 20px rgba(255,153,0,0.4) !important;
}

/* ── Text inputs / text areas ── */
.stTextInput > div > div,
.stTextArea > div > div,
[data-testid="stTextInput"] > div > div,
textarea, input[type="text"] {
    background: #080810 !important;
    border: 1px solid #332200 !important;
    border-radius: 8px !important;
    color: #FFCC99 !important;
    font-family: 'Share Tech Mono', monospace !important;
}
.stTextInput > div > div:focus-within,
.stTextArea > div > div:focus-within {
    border-color: #FF9900 !important;
    box-shadow: 0 0 10px rgba(255,153,0,0.15) !important;
}
textarea { color: #FFCC99 !important; }

/* ── Select boxes ── */
[data-testid="stSelectbox"] > div > div,
[data-baseweb="select"] > div {
    background: #080810 !important;
    border: 1px solid #332200 !important;
    color: #FFCC99 !important;
    border-radius: 8px !important;
}
[data-baseweb="select"] span {
    color: #FFCC99 !important;
}
/* Dropdown menu */
[data-baseweb="menu"], [data-baseweb="popover"] > div {
    background: #0a0a14 !important;
    border: 1px solid #332200 !important;
}
[data-baseweb="menu"] li {
    color: #FFCC99 !important;
    background: transparent !important;
}
[data-baseweb="menu"] li:hover {
    background: #1a1200 !important;
    color: #FF9900 !important;
}

/* ── Metrics ── */
[data-testid="stMetric"] {
    background: #080810 !important;
    border: 1px solid #1a1100 !important;
    border-radius: 12px !important;
    padding: 14px 16px !important;
    border-left: 3px solid #FF9900 !important;
}
[data-testid="stMetricValue"] {
    color: #FF9900 !important;
    font-family: 'Antonio', sans-serif !important;
    font-size: 1.8em !important;
    letter-spacing: 0.05em !important;
}
[data-testid="stMetricLabel"] {
    color: #CC9966 !important;
    font-family: 'Share Tech Mono', monospace !important;
    font-size: 0.72em !important;
    letter-spacing: 0.12em !important;
    text-transform: uppercase !important;
}
[data-testid="stMetricDelta"] {
    color: #33CCAA !important;
}

/* ── Chat messages ── */
.stChatMessage, [data-testid="stChatMessage"] {
    background: #080810 !important;
    border: 1px solid #1a1100 !important;
    border-radius: 12px !important;
    border-left: 3px solid #FF9900 !important;
}

/* ── Chat input + bottom bar ── */
[data-testid="stBottom"],
[data-testid="stBottom"] > div,
[data-testid="stBottomBlockContainer"],
[data-testid="stBottomBlockContainer"] > div,
.stBottom, .stBottom > div {
    background: #000000 !important;
    border-top: 1px solid #1a1100 !important;
}
[data-testid="stChatInput"],
[data-testid="stChatInput"] > div,
.stChatInput,
.stChatInput > div {
    background: #080810 !important;
    border: 1px solid #332200 !important;
    border-radius: 20px !important;
}
[data-testid="stChatInput"] textarea,
.stChatInput textarea {
    color: #FFCC99 !important;
    font-family: 'Share Tech Mono', monospace !important;
    background: transparent !important;
}
[data-testid="stChatInput"] button,
.stChatInput button {
    color: #FF9900 !important;
    background: transparent !important;
}
/* Kill any remaining white/light wrappers at the bottom */
[data-testid="stChatInputContainer"],
iframe + div, .stChatInputContainer,
div[class*="bottom-container"],
div[class*="Bottom"] {
    background: #000000 !important;
}

/* ── Expanders ── */
[data-testid="stExpander"] {
    background: #060610 !important;
    border: 1px solid #1a1100 !important;
    border-radius: 8px !important;
}
[data-testid="stExpander"] summary,
[data-testid="stExpander"] [data-testid="stExpanderToggleIcon"] {
    color: #CC9966 !important;
    font-family: 'Antonio', sans-serif !important;
    letter-spacing: 0.08em !important;
}
[data-testid="stExpander"] summary:hover {
    color: #FF9900 !important;
}

/* ── Tabs ── */
.stTabs [data-baseweb="tab-list"] {
    gap: 0px;
    border-bottom: 2px solid #1a1100 !important;
}
.stTabs [data-baseweb="tab"] {
    color: #CC9966 !important;
    font-family: 'Antonio', sans-serif !important;
    letter-spacing: 0.1em !important;
    text-transform: uppercase !important;
    background: transparent !important;
    border-radius: 12px 12px 0 0 !important;
    padding: 8px 20px !important;
}
.stTabs [aria-selected="true"] {
    color: #FF9900 !important;
    border-bottom: 3px solid #FF9900 !important;
    background: #0a0a14 !important;
}

/* ── Alerts ── */
[data-testid="stAlert"] {
    border-radius: 8px !important;
    font-family: 'Share Tech Mono', monospace !important;
}
div[data-baseweb="notification"][kind="positive"],
.element-container .stSuccess {
    background: rgba(51,204,153,0.08) !important;
    border-left: 3px solid #33CC99 !important;
    color: #33CC99 !important;
}
div[data-baseweb="notification"][kind="negative"],
.element-container .stError {
    background: rgba(255,102,51,0.08) !important;
    border-left: 3px solid #FF6633 !important;
    color: #FF6633 !important;
}
div[data-baseweb="notification"][kind="warning"],
.element-container .stWarning {
    background: rgba(255,204,0,0.08) !important;
    border-left: 3px solid #FFCC00 !important;
    color: #FFCC00 !important;
}
div[data-baseweb="notification"][kind="info"],
.element-container .stInfo {
    background: rgba(153,153,255,0.08) !important;
    border-left: 3px solid #9999FF !important;
    color: #9999FF !important;
}

/* ── Spinners ── */
.stSpinner > div > div {
    border-top-color: #FF9900 !important;
}

/* ── Captions ── */
[data-testid="stCaption"], .stCaption {
    color: #665533 !important;
    font-size: 0.78em !important;
    letter-spacing: 0.06em !important;
}

/* ── Toggle ── */
[data-testid="stToggle"] label span {
    color: #CC9966 !important;
}

/* ── Camera input ── */
[data-testid="stCameraInput"] {
    border: 1px solid #332200 !important;
    border-radius: 8px !important;
}
[data-testid="stCameraInput"] video {
    border-radius: 6px !important;
}

/* ── Audio player ── */
div[data-testid="stAudio"] { margin-top: 6px; }
audio { filter: sepia(30%) saturate(150%) !important; }

/* ── Iframe / components.html containers — no clipping ── */
iframe[title="streamlit_components_v1.html"],
div[data-testid="stCustomComponentV1"],
.element-container:has(iframe) {
    overflow: visible !important;
}

/* ── Scrollable containers ── */
[data-testid="stVerticalBlock"] > div[style*="overflow"] {
    border: 1px solid #1a1100 !important;
    border-radius: 8px !important;
    background: #040408 !important;
}

/* ── Sidebar select/input theming ── */
[data-testid="stSidebar"] .stSelectbox label,
[data-testid="stSidebar"] .stTextInput label {
    color: #CC9966 !important;
    font-size: 0.8em !important;
    letter-spacing: 0.1em !important;
    text-transform: uppercase !important;
}

/* ── Dataframes / Tables ── */
[data-testid="stTable"] th {
    background: #0a0a14 !important;
    color: #FF9900 !important;
    border-bottom: 2px solid #332200 !important;
}
[data-testid="stTable"] td {
    background: #050508 !important;
    color: #FFCC99 !important;
    border-bottom: 1px solid #1a1100 !important;
}

/* ══════════════════════════════════════════════════════════════
   LCARS STRUCTURAL COMPONENTS
   ══════════════════════════════════════════════════════════════ */

/* Header bar */
.lcars-bar {
    display: flex;
    align-items: stretch;
    gap: 0;
    margin-bottom: 16px;
    height: 52px;
}
.lcars-elbow {
    width: 90px;
    min-width: 90px;
    background: #FF9900;
    border-radius: 26px 0 0 26px;
}
.lcars-title-block {
    background: #000;
    padding: 0 24px;
    display: flex;
    flex-direction: column;
    justify-content: center;
    border-top: 4px solid #FF9900;
    border-bottom: 4px solid #FF9900;
    white-space: nowrap;
}
.lcars-title {
    font-family: 'Antonio', 'Arial Narrow', sans-serif;
    font-size: 1.5em;
    font-weight: 700;
    color: #FF9900;
    letter-spacing: 0.22em;
    text-transform: uppercase;
    line-height: 1.1;
}
.lcars-sub {
    font-family: 'Share Tech Mono', monospace;
    font-size: 0.55em;
    color: #CC9966;
    letter-spacing: 0.15em;
    text-transform: uppercase;
}
.lcars-pill {
    flex-grow: 1;
    background: linear-gradient(135deg, #CC6699 0%, #9966AA 100%);
    border-radius: 0 26px 26px 0;
    min-width: 40px;
}

/* Section dividers */
.lcars-section {
    display: flex;
    align-items: center;
    gap: 10px;
    margin: 14px 0 8px 0;
}
.lcars-section-dot {
    width: 10px;
    height: 10px;
    border-radius: 50%;
    background: #FF9900;
    flex-shrink: 0;
    box-shadow: 0 0 6px rgba(255,153,0,0.4);
}
.lcars-section-label {
    font-family: 'Antonio', sans-serif;
    font-size: 0.85em;
    color: #CC9966;
    letter-spacing: 0.18em;
    text-transform: uppercase;
    white-space: nowrap;
}
.lcars-section-line {
    flex-grow: 1;
    height: 2px;
    background: linear-gradient(90deg, #332200 0%, transparent 100%);
}

/* Status indicator */
.lcars-status {
    display: inline-flex;
    align-items: center;
    gap: 6px;
    font-family: 'Share Tech Mono', monospace;
    font-size: 0.75em;
    letter-spacing: 0.1em;
    text-transform: uppercase;
}
.lcars-status-dot {
    width: 8px;
    height: 8px;
    border-radius: 50%;
    display: inline-block;
}
.lcars-status-dot.green  { background: #33CC99; box-shadow: 0 0 6px #33CC99; }
.lcars-status-dot.amber  { background: #FF9900; box-shadow: 0 0 6px #FF9900; }
.lcars-status-dot.red    { background: #FF6633; box-shadow: 0 0 6px #FF6633; }

/* ══════════════════════════════════════════════════════════════
   BOTTOM BAR / CHAT INPUT — scorched earth (no white anywhere)
   ══════════════════════════════════════════════════════════════ */
[data-testid="stBottom"] *,
.stBottom * {
    background-color: #000000 !important;
}
/* Re-apply the input-area styling on top of the wildcard kill */
[data-testid="stBottom"] [data-testid="stChatInput"],
[data-testid="stBottom"] [data-testid="stChatInput"] > div {
    background: #080810 !important;
    border: 1px solid #332200 !important;
    border-radius: 20px !important;
}
[data-testid="stBottom"] textarea {
    background: transparent !important;
    color: #FFCC99 !important;
}
[data-testid="stBottom"] button {
    background: transparent !important;
    color: #FF9900 !important;
}

/* ══════════════════════════════════════════════════════════════
   BUTTON MIN-WIDTH — prevent text wrapping on small columns
   ══════════════════════════════════════════════════════════════ */
.stButton > button {
    min-width: 72px !important;
    white-space: nowrap !important;
    padding: 6px 18px !important;
}

/* ══════════════════════════════════════════════════════════════
   SCROLLBAR THEMING
   ══════════════════════════════════════════════════════════════ */
::-webkit-scrollbar { width: 6px; height: 6px; }
::-webkit-scrollbar-track { background: #050508; }
::-webkit-scrollbar-thumb { background: #332200; border-radius: 3px; }
::-webkit-scrollbar-thumb:hover { background: #FF9900; }

</style>"""
