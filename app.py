import streamlit as st
import json
import os
import math
if "result" not in st.session_state:
    st.session_state.result = None
from orchestrator import run_pipeline

st.set_page_config(page_title="ShoeScribe AI", layout="wide", page_icon="👟")

# ───────── CSS ─────────
def load_css():
    css_path = os.path.join(os.path.dirname(__file__), "style.css")
    with open(css_path, encoding="utf-8") as f:
        st.markdown(f"<style>{f.read()}</style>", unsafe_allow_html=True)

load_css()

# ───────── HELPERS ─────────
def safe_json(x):
    try:
        return json.loads(x) if isinstance(x, str) else x
    except Exception:
        return None

def pill(text, kind="feat"):
    return f"<span class='pill pill-{kind}'>{text}</span>"

def pills(items, type_):
    if not items:
        return ""
    color_map = {
        "feature": "#4f46e5",
        "pain":    "#ef4444",
        "benefit": "#10b981",
        "usp":     "#f59e0b"
    }
    color = color_map.get(type_, "#6b7280")
    return "".join([
        f'<span class="pill" style="border-color:{color}; color:{color};">{item}</span>'
        for item in items
    ])

def key_point(text):
    parts = text.split("—", 1)
    bold = parts[0].strip()
    rest = f" — {parts[1].strip()}" if len(parts) > 1 else ""
    return f"""
    <div class="key-point">
        <span class="kp-check">✓</span>
        <div class="kp-text"><strong>{bold}</strong>{rest}</div>
    </div>"""

# ───────── HERO ─────────
st.markdown("""
<div class="hero">
    <div class="hero-badge">⚡ AI-Powered</div>
    <h1>Shoe<span class="accent">Scribe</span> AI</h1>
    <p>Product descriptions that don't just describe — they sell.</p>
</div>
""", unsafe_allow_html=True)

# ───────── INPUT CARD ─────────
st.markdown("<div class='input-section'>", unsafe_allow_html=True)
col1, col2, col3 = st.columns([3, 3, 1])

with col1:
    name = st.text_input("Product Name", placeholder="e.g. Nike Air Max 270", label_visibility="visible")

with col2:
    category = st.text_input("Category", placeholder="e.g. running shoes", label_visibility="visible")

with col3:
    st.markdown("<div class='btn-spacer'></div>", unsafe_allow_html=True)
    run = st.button("⚡ Generate", use_container_width=True)

st.markdown("</div>", unsafe_allow_html=True)

# ───────── PIPELINE TRACKER ─────────
def pipeline_tracker(active=-1, done=None):
    done = done or set()
    stages = [
        ("research",   "🔍", "Research"),
        ("insights",   "💡", "Insights"),
        ("writing",    "✍️",  "Writing"),
        ("evaluation", "📊", "Evaluate"),
    ]
    items = ""
    for sid, icon, label in stages:
        cls = "stage"
        if sid in done:
            cls += " done"
            icon = "✓"
        elif stages.index((sid, icon, label)) == active:
            cls += " active"
        items += f"""
        <div class="{cls}">
            <div class="stage-dot">{icon}</div>
            <div class="stage-label">{label}</div>
        </div>"""
    return f"<div class='pipeline'>{items}</div>"

# ───────── PIPELINE ─────────
if run:
    if not name or not category:
        st.markdown("""
        <div class="toast-error">⚠️ Please fill in both Product Name and Category.</div>
        """, unsafe_allow_html=True)
        st.stop()

    tracker_placeholder = st.empty()
    status_placeholder  = st.empty()
    done_stages = set()

    # Stage 0 — Research
    tracker_placeholder.markdown(pipeline_tracker(active=0, done=done_stages), unsafe_allow_html=True)
    status_placeholder.markdown("""
    <div class="status-card">
        <div class="loading-dots"><span></span><span></span><span></span></div>
        <div class="loading-msg">Researching market data…</div>
        <div class="loading-sub">Stage 1 of 4</div>
    </div>""", unsafe_allow_html=True)

    # Stage 1 — Insights
    done_stages.add("research")
    tracker_placeholder.markdown(pipeline_tracker(active=1, done=done_stages), unsafe_allow_html=True)
    status_placeholder.markdown("""
    <div class="status-card">
        <div class="loading-dots"><span></span><span></span><span></span></div>
        <div class="loading-msg">Extracting key insights…</div>
        <div class="loading-sub">Stage 2 of 4</div>
    </div>""", unsafe_allow_html=True)

    st.session_state.result = run_pipeline(name, category)
    result = st.session_state.result

    done_stages.update({"insights", "writing", "evaluation"})
    tracker_placeholder.markdown(pipeline_tracker(active=-1, done=done_stages), unsafe_allow_html=True)
    status_placeholder.empty()
result = st.session_state.result

insights   = safe_json(result.get("insights")) if result else None
content    = safe_json(result.get("content")) if result else None
evaluation = safe_json(result.get("evaluation")) if result else None

if st.session_state.result:
    if st.button("🔄 Regenerate"):
        st.session_state.result = run_pipeline(name, category)
        st.rerun()

    # ───────── INSIGHTS ─────────
    if insights:
        st.markdown("""
        <div class="card">
            <div class="card-header">
                <div class="card-icon" style="background:#ede9fe">🔍</div>
                <div>
                    <div class="card-title">Market Insights</div>
                    <div class="card-subtitle">AI-researched competitive intelligence</div>
                </div>
            </div>
        </div>""", unsafe_allow_html=True)

        col1, col2 = st.columns(2)

        with col1:
            features = insights.get("features", [])
            if features:
                st.markdown(f"""
                <div class="insight-box">
                    <h4>Features</h4>
                    <div class="pills-wrap">{pills(features, "feature")}</div>
                </div>""", unsafe_allow_html=True)

            benefits = insights.get("benefits", [])
            if benefits:
                st.markdown(f"""
                <div class="insight-box">
                    <h4>Benefits</h4>
                    <div class="pills-wrap">{pills(benefits, "benefit")}</div>
                </div>""", unsafe_allow_html=True)

        with col2:
            pain_points = insights.get("pain_points", [])
            if pain_points:
                st.markdown(f"""
                <div class="insight-box">
                    <h4>Pain Points</h4>
                    <div class="pills-wrap">{pills(pain_points, "pain")}</div>
                </div>""", unsafe_allow_html=True)

            usp_ideas = insights.get("usp_ideas", [])
            if usp_ideas:
                st.markdown(f"""
                <div class="insight-box">
                    <h4>USP Ideas</h4>
                    <div class="pills-wrap">{pills(usp_ideas, "usp")}</div>
                </div>""", unsafe_allow_html=True)

    # ───────── PRODUCT DESCRIPTION ─────────
    if content:
        bullets_html = "".join([key_point(b) for b in content.get("usp_bullets", [])])

        st.markdown(f"""
        <div class="card">
            <div class="card-header">
                <div class="card-icon" style="background:#dcfce7">✍️</div>
                <div>
                    <div class="card-title">Product Description</div>
                    <div class="card-subtitle">Ready-to-publish copy</div>
                </div>
            </div>
            <div class="short-desc">{content.get("short_description", "")}</div>
            <div class="desc-grid">
                <div class="long-desc">{content.get("long_description", "")}</div>
                <div class="key-points">
                    <h4>Key Selling Points</h4>
                    {bullets_html}
                </div>
            </div>
        </div>""", unsafe_allow_html=True)

    # ───────── EVALUATION ─────────
    if evaluation:
        scores  = evaluation.get("scores", {})
        keys    = list(scores.keys())
        overall = (sum(scores[k]["score"] for k in keys) / len(keys)) if keys else 0
        overall_rounded = round(overall, 1)

        circ   = 2 * math.pi * 38
        offset = circ - (overall / 5) * circ

        # Card header
        st.markdown("""
        <div class="card">
            <div class="card-header">
                <div class="card-icon" style="background:#fef3c7">📊</div>
                <div>
                    <div class="card-title">Quality Evaluation</div>
                    <div class="card-subtitle">Multi-dimensional copy analysis</div>
                </div>
            </div>
        </div>""", unsafe_allow_html=True)

        col_metrics, col_ring = st.columns([2, 1])

        with col_metrics:
            for k in keys:
                s     = scores[k]
                pct   = (s["score"] / 5) * 100
                label = k.replace("_", " ").title()
                st.markdown(f"""
                <div class="eval-metric">
                    <div class="metric-header">
                        <span class="metric-name">{label}</span>
                        <span class="metric-score">{s["score"]}/5</span>
                    </div>
                    <div class="metric-bar">
                        <div class="metric-fill" style="width:{pct}%"></div>
                    </div>
                    <div class="metric-reason">{s.get("reason", "")}</div>
                </div>""", unsafe_allow_html=True)

        with col_ring:
            st.markdown(f"""
            <div class="score-meter">
                <div class="score-ring">
                    <svg width="96" height="96" viewBox="0 0 96 96">
                        <circle cx="48" cy="48" r="38"
                            fill="none" stroke="#ede9fe" stroke-width="6"/>
                        <circle cx="48" cy="48" r="38"
                            fill="none" stroke="#5e3bea" stroke-width="6"
                            stroke-linecap="round"
                            stroke-dasharray="{circ:.2f}"
                            stroke-dashoffset="{offset:.2f}"
                            transform="rotate(-90 48 48)"/>
                    </svg>
                    <div class="score-num">
                        <span class="score-val">{overall_rounded}</span>
                        <span class="score-max">/5</span>
                    </div>
                </div>
                <span class="score-label">Overall</span>
            </div>""", unsafe_allow_html=True)

        feedback = evaluation.get("overall_feedback", "")
        if feedback:
            st.markdown(f"""
            <div class="feedback-box">
                <div class="fb-label">💬 Feedback</div>
                {feedback}
            </div>""", unsafe_allow_html=True)

if not st.session_state.result:
    st.markdown("""
    <div class="empty-state">
        <span class="empty-icon">👟</span>
        <h3>Ready to write</h3>
        <p>Enter a product name and category above to generate AI-powered descriptions with market insights.</p>
    </div>
    """, unsafe_allow_html=True)