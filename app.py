import streamlit as st
import time
from agents import build_reader_agent, build_search_agent, writer_chain, critic_chain

# ── Page config ──────────────────────────────────────────────────────────────
st.set_page_config(
    page_title="ResearchMind · AI Research Agent",
    page_icon="🔬",
    layout="wide",
    initial_sidebar_state="collapsed",
)

# ── Custom CSS ────────────────────────────────────────────────────────────────
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Syne:wght@400;600;700;800&family=DM+Mono:wght@300;400;500&family=DM+Sans:ital,wght@0,300;0,400;0,500;1,300&display=swap');

/* ═══════════════════════════════════════════════════════════
   COLOR THEME OPTIONS - Choose One Below
   ═══════════════════════════════════════════════════════════ */

/* THEME 1: MODERN BLUE (Recommended) */
:root {
    --primary-color: #00d4ff;      /* Cyan */
    --primary-dark: #0099cc;
    --secondary-color: #6366f1;    /* Indigo */
    --accent-color: #10b981;       /* Emerald Green */
    --background: #0a0e27;         /* Deep Navy */
    --background-alt: #131829;
    --text-primary: #f0f9ff;       /* Almost White */
    --text-secondary: #94a3b8;     /* Slate */
    --border-color: rgba(0, 212, 255, 0.15);
    --success-color: #10b981;
    --warning-color: #f59e0b;
}

/* THEME 2: PURPLE GRADIENT (Uncomment to use)
:root {
    --primary-color: #a78bfa;      /* Purple */
    --primary-dark: #8b5cf6;
    --secondary-color: #ec4899;    /* Pink */
    --accent-color: #14b8a6;       /* Teal */
    --background: #1a1625;
    --background-alt: #2a1f3d;
    --text-primary: #f3f0ff;
    --text-secondary: #c4b5fd;
    --border-color: rgba(167, 139, 250, 0.12);
    --success-color: #14b8a6;
    --warning-color: #f97316;
}
*/

/* THEME 3: TECH NEON (Uncomment to use)
:root {
    --primary-color: #00ff88;      /* Neon Green */
    --primary-dark: #00cc6a;
    --secondary-color: #0088ff;    /* Electric Blue */
    --accent-color: #ff006e;       /* Hot Pink */
    --background: #0a0e1a;
    --background-alt: #0f1629;
    --text-primary: #e0f7ff;
    --text-secondary: #7a8fa3;
    --border-color: rgba(0, 255, 136, 0.1);
    --success-color: #00ff88;
    --warning-color: #ff006e;
}
*/

html, body, [class*="css"] {
    font-family: 'DM Sans', sans-serif;
    color: var(--text-primary);
}

.stApp {
    background: var(--background);
    background-image:
        radial-gradient(ellipse 80% 50% at 20% -10%, rgba(0, 212, 255, 0.08) 0%, transparent 50%),
        radial-gradient(ellipse 60% 45% at 80% 110%, rgba(99, 102, 241, 0.07) 0%, transparent 55%),
        radial-gradient(ellipse 50% 35% at 50% 50%, rgba(255, 255, 255, 0.01) 0%, transparent 70%);
    background-attachment: fixed;
}

#MainMenu, footer, header { visibility: hidden; }
.block-container { padding: 2rem 3rem 5rem; max-width: 1200px; }

/* ────────────────────────────────────
   HERO SECTION
   ──────────────────────────────────── */
.hero {
    text-align: center;
    padding: 4rem 0 2.5rem;
}
.hero-eyebrow {
    font-family: 'DM Mono', monospace;
    font-size: 0.62rem;
    font-weight: 600;
    letter-spacing: 0.35em;
    text-transform: uppercase;
    color: var(--primary-color);
    margin-bottom: 1rem;
    opacity: 0.9;
}
.hero h1 {
    font-family: 'Syne', sans-serif;
    font-size: clamp(2.8rem, 6vw, 4.6rem);
    font-weight: 800;
    line-height: 1.05;
    letter-spacing: -0.03em;
    color: var(--text-primary);
    margin: 0 0 1rem;
    background: linear-gradient(135deg, var(--text-primary), var(--primary-color));
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
    background-clip: text;
}
.hero h1 em {
    font-style: normal;
    color: var(--primary-color);
    -webkit-text-fill-color: var(--primary-color);
}
.hero-sub {
    font-size: 1.05rem;
    font-weight: 300;
    color: var(--text-secondary);
    max-width: 520px;
    margin: 0 auto;
    line-height: 1.8;
}

/* ────────────────────────────────────
   DIVIDER
   ──────────────────────────────────── */
.divider {
    height: 1px;
    background: linear-gradient(90deg, transparent, var(--border-color), transparent);
    margin: 2.5rem 0;
}

/* ────────────────────────────────────
   INPUT PANEL
   ──────────────────────────────────── */
.input-panel {
    background: rgba(255,255,255,0.03);
    border: 1px solid var(--border-color);
    border-radius: 18px;
    padding: 2rem 2.2rem;
    margin-bottom: 1.5rem;
    backdrop-filter: blur(10px);
    transition: border-color 0.3s, background 0.3s;
}
.input-panel:hover {
    background: rgba(255,255,255,0.05);
    border-color: rgba(0, 212, 255, 0.25);
}

/* ────────────────────────────────────
   STREAMLIT INPUT OVERRIDES
   ──────────────────────────────────── */
.stTextInput > div > div > input {
    background: rgba(255,255,255,0.04) !important;
    border: 1.5px solid var(--border-color) !important;
    border-radius: 12px !important;
    color: var(--text-primary) !important;
    font-family: 'DM Sans', sans-serif !important;
    font-size: 0.97rem !important;
    padding: 0.8rem 1.2rem !important;
    transition: border-color 0.25s, box-shadow 0.25s, background 0.25s !important;
    caret-color: var(--primary-color) !important;
}
.stTextInput > div > div > input:focus {
    border-color: var(--primary-color) !important;
    box-shadow: 0 0 0 4px rgba(0, 212, 255, 0.12) !important;
    background: rgba(255,255,255,0.06) !important;
}
.stTextInput > div > div > input::placeholder {
    color: rgba(148, 163, 184, 0.5) !important;
}
.stTextInput > label {
    font-family: 'DM Mono', monospace !important;
    font-size: 0.63rem !important;
    letter-spacing: 0.25em !important;
    text-transform: uppercase !important;
    color: var(--primary-color) !important;
    font-weight: 600 !important;
    margin-bottom: 0.4rem !important;
}

/* ────────────────────────────────────
   RUN BUTTON
   ──────────────────────────────────── */
.stButton > button {
    background: linear-gradient(135deg, var(--primary-color) 0%, var(--secondary-color) 100%) !important;
    color: var(--background) !important;
    font-family: 'Syne', sans-serif !important;
    font-weight: 700 !important;
    font-size: 0.95rem !important;
    letter-spacing: 0.08em !important;
    border: none !important;
    border-radius: 12px !important;
    padding: 0.8rem 2.2rem !important;
    cursor: pointer !important;
    transition: transform 0.2s, box-shadow 0.2s, opacity 0.2s !important;
    box-shadow: 0 8px 25px rgba(0, 212, 255, 0.25) !important;
    width: 100%;
}
.stButton > button:hover {
    transform: translateY(-3px) !important;
    box-shadow: 0 12px 40px rgba(0, 212, 255, 0.35) !important;
    opacity: 0.96 !important;
}
.stButton > button:active {
    transform: translateY(-1px) !important;
    box-shadow: 0 4px 15px rgba(0, 212, 255, 0.25) !important;
}

/* ────────────────────────────────────
   DOWNLOAD BUTTON
   ──────────────────────────────────── */
.stDownloadButton > button {
    background: rgba(0, 212, 255, 0.08) !important;
    border: 1.5px solid var(--primary-color) !important;
    border-radius: 10px !important;
    color: var(--primary-color) !important;
    font-family: 'DM Mono', monospace !important;
    font-size: 0.7rem !important;
    letter-spacing: 0.15em !important;
    padding: 0.6rem 1.4rem !important;
    width: auto !important;
    transition: background 0.2s, border-color 0.2s, box-shadow 0.2s !important;
    box-shadow: none !important;
}
.stDownloadButton > button:hover {
    background: rgba(0, 212, 255, 0.15) !important;
    border-color: var(--primary-color) !important;
    box-shadow: 0 4px 15px rgba(0, 212, 255, 0.15) !important;
}

/* ────────────────────────────────────
   PIPELINE STEP CARDS
   ──────────────────────────────────── */
.step-card {
    background: rgba(255,255,255,0.02);
    border: 1.5px solid rgba(255,255,255,0.08);
    border-radius: 14px;
    padding: 1.2rem 1.5rem 1.2rem 1.8rem;
    margin-bottom: 0.8rem;
    position: relative;
    overflow: hidden;
    transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
}
.step-card:hover {
    background: rgba(255,255,255,0.03);
    border-color: rgba(255,255,255,0.12);
}
.step-card.active {
    border-color: var(--primary-color);
    background: rgba(0, 212, 255, 0.05);
}
.step-card.done {
    border-color: var(--success-color);
    background: rgba(16, 185, 129, 0.04);
}
.step-card::before {
    content: '';
    position: absolute;
    left: 0; top: 0; bottom: 0;
    width: 4px;
    border-radius: 14px 0 0 14px;
    background: rgba(255,255,255,0.05);
    transition: background 0.3s;
}
.step-card.active::before { background: var(--primary-color); }
.step-card.done::before { background: var(--success-color); }

.step-header {
    display: flex;
    align-items: center;
    gap: 0.8rem;
}
.step-num {
    font-family: 'DM Mono', monospace;
    font-size: 0.62rem;
    font-weight: 600;
    letter-spacing: 0.2em;
    color: var(--primary-color);
    opacity: 0.7;
}
.step-title {
    font-family: 'Syne', sans-serif;
    font-size: 0.9rem;
    font-weight: 700;
    color: var(--text-primary);
    flex: 1;
}
.step-status {
    font-family: 'DM Mono', monospace;
    font-size: 0.62rem;
    letter-spacing: 0.15em;
}
.status-waiting { color: rgba(148, 163, 184, 0.6); }
.status-running { color: var(--primary-color); }
.status-done { color: var(--success-color); }

.step-desc {
    font-size: 0.77rem;
    color: var(--text-secondary);
    margin-top: 0.3rem;
    opacity: 0.8;
}

/* ────────────────────────────────────
   SECTION HEADING
   ──────────────────────────────────── */
.section-heading {
    font-family: 'Syne', sans-serif;
    font-size: 1.25rem;
    font-weight: 700;
    color: var(--text-primary);
    margin: 1.2rem 0 1.2rem;
    letter-spacing: -0.02em;
}

/* ────────────────────────────────────
   EXAMPLE CHIPS
   ──────────────────────────────────── */
.chips-row {
    display: flex;
    gap: 0.6rem;
    flex-wrap: wrap;
    margin-top: 1.2rem;
    align-items: center;
}
.chip-try {
    font-family: 'DM Mono', monospace;
    font-size: 0.64rem;
    color: var(--text-secondary);
    letter-spacing: 0.16em;
    text-transform: uppercase;
}
.chip {
    background: rgba(0, 212, 255, 0.08);
    border: 1px solid var(--border-color);
    border-radius: 8px;
    padding: 0.3rem 0.8rem;
    font-size: 0.75rem;
    color: var(--text-secondary);
    font-family: 'DM Mono', monospace;
    cursor: pointer;
    transition: all 0.25s;
}
.chip:hover {
    background: rgba(0, 212, 255, 0.15);
    border-color: var(--primary-color);
    color: var(--primary-color);
}

/* ────────────────────────────────────
   RESULT EXPANDER
   ──────────────────────────────────── */
details {
    background: rgba(255,255,255,0.02);
    border: 1px solid var(--border-color);
    border-radius: 14px;
    margin-bottom: 0.8rem;
    overflow: hidden;
    transition: border-color 0.3s, background 0.3s;
}
details:hover {
    background: rgba(255,255,255,0.03);
    border-color: rgba(0, 212, 255, 0.2);
}
details summary {
    font-family: 'DM Mono', monospace !important;
    font-size: 0.7rem !important;
    letter-spacing: 0.15em !important;
    color: var(--text-secondary) !important;
    padding: 0.95rem 1.3rem !important;
    cursor: pointer !important;
    list-style: none;
    transition: color 0.25s;
}
details summary:hover { color: var(--primary-color) !important; }
details[open] summary { border-bottom: 1px solid var(--border-color); }

/* ────────────────────────────────────
   RESULT PANELS
   ──────────────────────────────────── */
.result-panel {
    background: transparent;
    padding: 1.2rem 1.3rem;
}
.result-panel-title {
    font-family: 'DM Mono', monospace;
    font-size: 0.66rem;
    font-weight: 600;
    letter-spacing: 0.25em;
    text-transform: uppercase;
    color: var(--primary-color);
    margin-bottom: 0.95rem;
}
.result-content {
    font-size: 0.82rem;
    line-height: 1.85;
    color: var(--text-secondary);
    white-space: pre-wrap;
    font-family: 'DM Mono', monospace;
    max-height: 240px;
    overflow-y: auto;
}
.result-content::-webkit-scrollbar { width: 5px; }
.result-content::-webkit-scrollbar-track { background: transparent; }
.result-content::-webkit-scrollbar-thumb { background: rgba(0, 212, 255, 0.2); border-radius: 5px; }

/* ────────────────────────────────────
   REPORT & FEEDBACK PANELS
   ──────────────────────────────────── */
.report-panel {
    background: rgba(0, 212, 255, 0.04);
    border: 1.5px solid var(--primary-color);
    border-radius: 16px;
    padding: 2rem 2.3rem;
    margin-top: 0.6rem;
    margin-bottom: 1.2rem;
    backdrop-filter: blur(8px);
}
.feedback-panel {
    background: rgba(16, 185, 129, 0.04);
    border: 1.5px solid var(--success-color);
    border-radius: 16px;
    padding: 2rem 2.3rem;
    margin-top: 0.6rem;
    backdrop-filter: blur(8px);
}
.panel-label {
    font-family: 'DM Mono', monospace;
    font-size: 0.66rem;
    letter-spacing: 0.25em;
    text-transform: uppercase;
    margin-bottom: 1.3rem;
    padding-bottom: 0.8rem;
    font-weight: 600;
}
.panel-label.orange {
    color: var(--primary-color);
    border-bottom: 2px solid rgba(0, 212, 255, 0.2);
}
.panel-label.green {
    color: var(--success-color);
    border-bottom: 2px solid rgba(16, 185, 129, 0.2);
}

/* ────────────────────────────────────
   MARKDOWN IN PANELS
   ──────────────────────────────────── */
.report-panel p, .feedback-panel p {
    font-size: 0.95rem;
    line-height: 1.88;
    color: var(--text-secondary);
}
.report-panel h1, .report-panel h2, .report-panel h3,
.feedback-panel h1, .feedback-panel h2, .feedback-panel h3 {
    font-family: 'Syne', sans-serif;
    color: var(--text-primary);
    margin: 1.3rem 0 0.6rem;
    letter-spacing: -0.02em;
}
.report-panel h2 { font-size: 1.2rem; }
.report-panel h3 { font-size: 1rem; }

/* ────────────────────────────────────
   SPINNER
   ──────────────────────────────────── */
.stSpinner > div { 
    color: var(--primary-color) !important;
    border-color: rgba(0, 212, 255, 0.2) !important;
}

/* ────────────────────────────────────
   ALERTS & WARNINGS
   ──────────────────────────────────── */
.stAlert {
    background: rgba(0, 212, 255, 0.08) !important;
    border: 1.5px solid var(--primary-color) !important;
    border-radius: 12px !important;
    color: var(--text-secondary) !important;
    font-family: 'DM Mono', monospace !important;
    font-size: 0.8rem !important;
}

/* ────────────────────────────────────
   FOOTER & NOTICE
   ──────────────────────────────────── */
.notice {
    font-family: 'DM Mono', monospace;
    font-size: 0.64rem;
    color: rgba(148, 163, 184, 0.5);
    text-align: center;
    margin-top: 4rem;
    letter-spacing: 0.12em;
}

/* ────────────────────────────────────
   SCROLLBAR STYLING
   ──────────────────────────────────── */
::-webkit-scrollbar {
    width: 8px;
    height: 8px;
}
::-webkit-scrollbar-track {
    background: transparent;
}
::-webkit-scrollbar-thumb {
    background: rgba(0, 212, 255, 0.2);
    border-radius: 8px;
}
::-webkit-scrollbar-thumb:hover {
    background: rgba(0, 212, 255, 0.35);
}
</style>
""", unsafe_allow_html=True)


# ── Helper: render a step card ────────────────────────────────────────────────
def step_card(num: str, title: str, state: str, desc: str = ""):
    status_map = {
        "waiting": ("WAITING",  "status-waiting"),
        "running": ("● RUNNING", "status-running"),
        "done":    ("✓ DONE",    "status-done"),
    }
    label, cls = status_map.get(state, ("", ""))
    card_cls = {"running": "active", "done": "done"}.get(state, "")
    st.markdown(f"""
    <div class="step-card {card_cls}">
        <div class="step-header">
            <span class="step-num">{num}</span>
            <span class="step-title">{title}</span>
            <span class="step-status {cls}">{label}</span>
        </div>
        {"<div class='step-desc'>"+desc+"</div>" if desc else ""}
    </div>
    """, unsafe_allow_html=True)


# ── Session state init ────────────────────────────────────────────────────────
for key in ("results", "running", "done"):
    if key not in st.session_state:
        st.session_state[key] = {} if key == "results" else False


# ── Hero ──────────────────────────────────────────────────────────────────────
st.markdown("""
<div class="hero">
    <div class="hero-eyebrow">Multi-Agent AI System</div>
    <h1>Research<em>Mind</em></h1>
    <p class="hero-sub">
        Four specialized AI agents collaborate — searching, scraping, writing,
        and critiquing — to deliver a polished research report on any topic.
    </p>
</div>
<div class="divider"></div>
""", unsafe_allow_html=True)


# ── Layout: input left, pipeline right ───────────────────────────────────────
col_input, col_spacer, col_pipeline = st.columns([5, 0.4, 4])

with col_input:
    st.markdown('<div class="input-panel">', unsafe_allow_html=True)
    topic = st.text_input(
        "Research Topic",
        placeholder="e.g. Quantum computing breakthroughs in 2025",
        key="topic_input",
        label_visibility="visible",
    )
    run_btn = st.button("⚡  Run Research Pipeline", use_container_width=True)
    st.markdown('</div>', unsafe_allow_html=True)

    # Example chips
    st.markdown("""
    <div class="chips-row">
        <span class="chip-try">Try →</span>
        <span class="chip">LLM agents 2025</span>
        <span class="chip">CRISPR gene editing</span>
        <span class="chip">Fusion energy progress</span>
    </div>
    """, unsafe_allow_html=True)

with col_pipeline:
    st.markdown('<div class="section-heading">Pipeline</div>', unsafe_allow_html=True)

    r = st.session_state.results

    def s(step):
        steps = ["search", "reader", "writer", "critic"]
        if not r and not st.session_state.running:
            return "waiting"
        if step in r:
            return "done"
        if st.session_state.running:
            for k in steps:
                if k not in r:
                    return "running" if k == step else "waiting"
        return "waiting"

    step_card("01", "Search Agent",  s("search"), "Gathers recent web information")
    step_card("02", "Reader Agent",  s("reader"), "Scrapes & extracts deep content")
    step_card("03", "Writer Chain",  s("writer"), "Drafts the full research report")
    step_card("04", "Critic Chain",  s("critic"), "Reviews & scores the report")


# ── Run pipeline ──────────────────────────────────────────────────────────────
if run_btn:
    if not topic.strip():
        st.warning("Please enter a research topic first.")
    else:
        st.session_state.results = {}
        st.session_state.running = True
        st.session_state.done = False
        st.rerun()

if st.session_state.running and not st.session_state.done:
    results = {}
    topic_val = st.session_state.topic_input

    # Step 1: Search
    with st.spinner("Search Agent is working…"):
        search_agent = build_search_agent()
        sr = search_agent.invoke({
            "messages": [("user", f"Find recent, reliable and detailed information about: {topic_val}")]
        })
        results["search"] = sr["messages"][-1].content
        st.session_state.results = dict(results)

    # Step 2: Reader
    with st.spinner("Reader Agent is scraping top resources…"):
        reader_agent = build_reader_agent()
        rr = reader_agent.invoke({
            "messages": [("user",
                f"Based on the following search results about '{topic_val}', "
                f"pick the most relevant URL and scrape it for deeper content.\n\n"
                f"Search Results:\n{results['search'][:800]}"
            )]
        })
        results["reader"] = rr["messages"][-1].content
        st.session_state.results = dict(results)

    # Step 3: Writer
    with st.spinner("Writer is drafting the report…"):
        research_combined = (
            f"SEARCH RESULTS:\n{results['search']}\n\n"
            f"DETAILED SCRAPED CONTENT:\n{results['reader']}"
        )
        results["writer"] = writer_chain.invoke({
            "topic": topic_val,
            "research": research_combined
        })
        st.session_state.results = dict(results)

    # Step 4: Critic
    with st.spinner("Critic is reviewing the report…"):
        results["critic"] = critic_chain.invoke({
            "report": results["writer"]
        })
        st.session_state.results = dict(results)

    st.session_state.running = False
    st.session_state.done = True
    st.rerun()


# ── Results display ───────────────────────────────────────────────────────────
r = st.session_state.results

if r:
    st.markdown('<div class="divider"></div>', unsafe_allow_html=True)
    st.markdown('<div class="section-heading">Results</div>', unsafe_allow_html=True)

    if "search" in r:
        with st.expander("🔍 Search Results (raw)", expanded=False):
            st.markdown(
                f'<div class="result-panel">'
                f'<div class="result-panel-title">Search Agent Output</div>'
                f'<div class="result-content">{r["search"]}</div>'
                f'</div>',
                unsafe_allow_html=True
            )

    if "reader" in r:
        with st.expander("📄 Scraped Content (raw)", expanded=False):
            st.markdown(
                f'<div class="result-panel">'
                f'<div class="result-panel-title">Reader Agent Output</div>'
                f'<div class="result-content">{r["reader"]}</div>'
                f'</div>',
                unsafe_allow_html=True
            )

    if "writer" in r:
        st.markdown("""
        <div class="report-panel">
            <div class="panel-label orange">📝 Final Research Report</div>
        """, unsafe_allow_html=True)
        st.markdown(r["writer"])
        st.markdown("</div>", unsafe_allow_html=True)

        st.download_button(
            label="⬇  Download Report (.md)",
            data=r["writer"],
            file_name=f"research_report_{int(time.time())}.md",
            mime="text/markdown",
        )

    if "critic" in r:
        st.markdown("""
        <div class="feedback-panel">
            <div class="panel-label green">🧐 Critic Feedback</div>
        """, unsafe_allow_html=True)
        st.markdown(r["critic"])
        st.markdown("</div>", unsafe_allow_html=True)


# ── Footer ────────────────────────────────────────────────────────────────────
st.markdown("""
<div class="notice">
    ResearchMind · Powered by LangChain multi-agent pipeline · Built with Streamlit
</div>
""", unsafe_allow_html=True)