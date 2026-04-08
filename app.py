import streamlit as st
import time
from backend.verifier import verify_claim

# ---------------- PAGE CONFIG ----------------
st.set_page_config(
    page_title="Real -Time Fact-checking Using Retrieval-Augmented Generation and Large Language Models",
    page_icon="🔍",
    layout="centered" 
)

# ---------------- SESSION STATE ----------------
if "theme" not in st.session_state:
    st.session_state.theme = "dark"

# ---------------- THEME COLORS ----------------
if st.session_state.theme == "dark":
    bg_color = "#0e1117"
    card_color = "rgba(255, 255, 255, 0.05)"
    text_color = "#FFFFFF"
    heading_color = "#FFFFFF"  # White for dark mode
    border_color = "rgba(255, 255, 255, 0.1)"
    btn_color = "linear-gradient(45deg, #00c6ff, #0072ff)"
else:
    bg_color = "#f5f7fb"
    card_color = "#ffffff"
    text_color = "#333333"
    heading_color = "#000000"  # Black for light mode as requested
    border_color = "#dddddd"
    btn_color = "linear-gradient(45deg, #0072ff, #00c6ff)"

# ---------------- CSS ----------------
st.markdown(f"""
<style>
[data-testid="stAppViewContainer"] {{
    background-color: {bg_color};
    color: {text_color};
    transition: 0.3s;
}}

.main-title {{
    text-align: center;
    font-size: 48px;
    font-weight: 800;
    color: {heading_color};
    margin-bottom: 5px;
    animation: fadeInDown 0.8s ease-out;
}}

.subtitle {{
    text-align: center;
    font-size: 18px;
    color: gray;
    margin-bottom: 40px;
}}

.card {{
    background: {card_color};
    padding: 30px;
    border-radius: 20px;
    border: 1px solid {border_color};
    box-shadow: 0 10px 25px rgba(0,0,0,0.1);
    margin-bottom: 25px;
    animation: fadeInUp 0.6s ease-out;
}}

/* Button Styling */
div.stButton > button {{
    background: {btn_color} !important;
    color: white !important;
    border-radius: 12px !important;
    border: none !important;
    width: 100% !important;
    font-weight: bold !important;
    padding: 10px !important;
    transition: 0.3s;
}}

div.stButton > button:hover {{
    transform: scale(1.02);
    box-shadow: 0 5px 15px rgba(0,114,255,0.3);
}}

/* Result Verdicts */
.verdict {{
    padding: 20px;
    border-radius: 15px;
    font-size: 28px;
    font-weight: bold;
    text-align: center;
}}
.real {{ background: rgba(16, 185, 129, 0.15); color: #10b981; border: 1px solid #10b981; }}
.fake {{ background: rgba(239, 68, 68, 0.15); color: #ef4444; border: 1px solid #ef4444; }}

@keyframes fadeInDown {{ from {{ opacity: 0; transform: translateY(-20px); }} to {{ opacity: 1; transform: translateY(0); }} }}
@keyframes fadeInUp {{ from {{ opacity: 0; transform: translateY(20px); }} to {{ opacity: 1; transform: translateY(0); }} }}

</style>
""", unsafe_allow_html=True)

# ---------------- HEADER & TOGGLE ----------------
col1, col2 = st.columns([10, 1])
with col2:
    if st.button("🌙" if st.session_state.theme == "dark" else "☀️"):
        st.session_state.theme = "light" if st.session_state.theme == "dark" else "dark"
        st.rerun()

st.markdown("<div class='main-title'>Fact Checker</div>", unsafe_allow_html=True)
st.markdown("<div class='subtitle'>Real-time Fact Checking by RAG and LLM</div>", unsafe_allow_html=True)

# ---------------- INPUT ----------------
st.markdown("<div class='card'>", unsafe_allow_html=True)
# The label_visibility="collapsed" fixes the empty gap you showed in the pic
claim = st.text_area("input", placeholder="Paste a claim or news headline here...", height=120, label_visibility="collapsed")
verify_btn = st.button("🚀 Verify Claim")
st.markdown("</div>", unsafe_allow_html=True)

# ---------------- RESULTS ----------------
if verify_btn:
    if claim.strip() == "":
        st.warning("Please enter a claim first!")
    else:
        with st.spinner("Analyzing accuracy..."):
            result = verify_claim(claim)
        
        # Verdict Card
        v_class = "real" if result["verdict"] == "REAL" else "fake"
        st.markdown(f"""
        <div class='card'>
            <div class='verdict {v_class}'>{result['verdict']}</div>
            <br>
            <p style='text-align:center;'><b>Confidence:</b> {int(result['confidence'])}%</p>
        </div>
        """, unsafe_allow_html=True)

        # Explanation Card
        st.markdown("<div class='card'>", unsafe_allow_html=True)
        st.markdown("### 🧠 Analysis Explanation")
        st.write(result["explanation"])
        
        # Source tag
        if result["source_type"] == "database":
            st.success("Verified via Local ChromaDB")
        else:
            st.info("Verified via Global Web Search")
        st.markdown("</div>", unsafe_allow_html=True)

        # Sources Card
        if result.get("sources"):
            st.markdown("<div class='card'>", unsafe_allow_html=True)
            st.markdown("### 🔗 Referenced Sources")
            for s in result["sources"]:
                st.markdown(f"- [{s['title']}]({s['url']})")
            st.markdown("</div>", unsafe_allow_html=True)

        st.caption(f"Checked at {result['timestamp']}")