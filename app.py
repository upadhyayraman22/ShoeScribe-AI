import streamlit as st
import json
import os
import math

from orchestrator import run_pipeline

if "result" not in st.session_state:
    st.session_state.result = None

st.set_page_config(page_title="ShoeScribe AI", layout="wide", page_icon="👟")
if "name" not in st.session_state:
    st.session_state.name = ""
if "category" not in st.session_state:
    st.session_state.category = ""

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

# ───────── INPUT ─────────
col1, col2, col3 = st.columns([3, 3, 1])

with col1:
    name = st.text_input("Product Name", value=st.session_state.name)

with col2:
    category = st.text_input("Category", value=st.session_state.category)

with col3:
    st.markdown("<div style='margin-top:25px'></div>", unsafe_allow_html=True)
    run = st.button("⚡ Generate", use_container_width=True)

# ───────── RUN PIPELINE ─────────
if run:
    if not name or not category:
        st.warning("⚠️ Please fill all fields")
        st.stop()
        
    st.session_state.name = name
    st.session_state.category = category
    st.session_state.result = run_pipeline(name, category)

# ───────── LOAD RESULT SAFELY ─────────
result = st.session_state.result

initial_content = safe_json(result.get("initial_content")) if result else None
improved_content = safe_json(result.get("improved_content")) if result else None
initial_score = result.get("initial_score", 0) if result else 0
final_score = result.get("final_score", 0) if result else 0

insights = safe_json(result.get("insights")) if result else None
evaluation = safe_json(result.get("evaluation")) if result else None

# ───────── MAIN UI ─────────
if result:

    if st.button("🔄 Regenerate"):
        st.session_state.result = run_pipeline(
            st.session_state.name,
            st.session_state.category
        )
        st.rerun()

    # ───────── INSIGHTS ─────────
    if insights:
        st.markdown("## 🔍 Market Insights")

        col1, col2 = st.columns(2)

        with col1:
            if insights.get("features"):
                st.markdown("**Features**")
                st.markdown(pills(insights["features"], "feature"), unsafe_allow_html=True)

            if insights.get("benefits"):
                st.markdown("**Benefits**")
                st.markdown(pills(insights["benefits"], "benefit"), unsafe_allow_html=True)

        with col2:
            if insights.get("pain_points"):
                st.markdown("**Pain Points**")
                st.markdown(pills(insights["pain_points"], "pain"), unsafe_allow_html=True)

            if insights.get("usp_ideas"):
                st.markdown("**USP Ideas**")
                st.markdown(pills(insights["usp_ideas"], "usp"), unsafe_allow_html=True)

    # ───────── TOGGLE ─────────
    show_comparison = st.toggle("🔍 Show improvement comparison")

    # ───────── PRODUCT DESCRIPTION ─────────
    if improved_content:

        if show_comparison and initial_content:
            col1, col2 = st.columns(2)

            with col1:
                st.markdown("### 🟥 Initial Output")
                st.markdown(f"**Score:** {round(initial_score,2)}")
                st.write(initial_content.get("long_description", ""))

            with col2:
                st.markdown("### 🟩 Improved Output")
                st.markdown(f"**Score:** {round(final_score,2)}")
                st.write(improved_content.get("long_description", ""))

        else:
            bullets_html = "".join([key_point(b) for b in improved_content.get("usp_bullets", [])])

            st.markdown(f"""
            <div class="card">
                <h3>Product Description</h3>
                <p>{improved_content.get("short_description", "")}</p>
                <div>{improved_content.get("long_description", "")}</div>
                <h4>Key Points</h4>
                {bullets_html}
                <div style="margin-top:10px; font-weight:600;">
                    Final Score: {round(final_score,2)}/5
                </div>
            </div>
            """, unsafe_allow_html=True)

    # ───────── EVALUATION ─────────
    if evaluation:
        st.markdown("## 📊 Evaluation")

        scores = evaluation.get("scores", {})

        for k, s in scores.items():
            reason = s.get("reason", "")
            st.markdown(f"**{k.upper()} — {s['score']}/5**")
            if reason:
                st.markdown(f"💡 {reason}")

        feedback = evaluation.get("overall_feedback", "")
        if feedback:
            st.markdown("### 💬 Feedback")
            st.write(feedback)

# ───────── EMPTY STATE ─────────
if not result:
    st.info("Enter product details and click Generate 🚀")