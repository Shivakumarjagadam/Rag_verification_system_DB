import streamlit as st
from backend.verifier import verify_claim

st.set_page_config(
    page_title="Veritas 2026",
    layout="wide"
)

st.markdown("""
<style>

body{
background: #0e1117;
color:white;
}

.verdict-box{
padding:40px;
border-radius:20px;
font-size:30px;
font-weight:bold;
text-align:center;
}

.real{
background:#0c3d2e;
color:#2aff9c;
}

.fake{
background:#3d0c0c;
color:#ff4a4a;
}

</style>
""", unsafe_allow_html=True)

st.title("Veritas 2026")
st.caption("Real-time fake news verification using RAG + LLM")

claim = st.text_area(
    "Enter a claim",
    height=150
)

if st.button("Verify News"):

    with st.spinner("Analyzing claim..."):
        result = verify_claim(claim)

    st.markdown("---")

    if result["source_type"] == "database":
        st.success("⚡ Result retrieved from ChromaDB cache")

    else:
        st.info("🌐 Result generated using Google Search + AI")

    verdict = result["verdict"]

    if verdict == "REAL":
        style="real"
    else:
        style="fake"

    st.markdown(
        f"<div class='verdict-box {style}'>{verdict}</div>",
        unsafe_allow_html=True
    )

    st.metric("Confidence", f"{int(result['confidence'])}%")

    st.write("### Explanation")

    st.write(result["explanation"])

    if result["source_type"] == "google":

        st.write("### Sources")

        for s in result["sources"]:
            st.write(f"- [{s['title']}]({s['url']})")

    st.caption(f"Checked at {result['timestamp']}")