import streamlit as st # pyright: ignore[reportMissingImports]
import google.generativeai as genai # pyright: ignore[reportMissingImports]
import json, re

# Configure Gemini
genai.configure(api_key=st.secrets["GEMINI_API_KEY"])

st.set_page_config(page_title="UGC Generator", layout="wide")

# ---------- CUSTOM CARD STYLE ----------
st.markdown("""
<style>
.card {
    padding: 20px;
    border-radius: 15px;
    background-color: #111827;
    box-shadow: 0 4px 20px rgba(0,0,0,0.2);
    margin-bottom: 15px;
}
.title {
    font-size: 20px;
    font-weight: bold;
}
</style>
""", unsafe_allow_html=True)

# ---------- TITLE ----------
st.title("💄 AI UGC Ad Generator (Skincare)")
st.markdown("Create viral, high-converting ad scripts 🚀")
st.markdown("---")

# ---------- SIDEBAR ----------
st.sidebar.header("📌 Product Details")

product_name = st.sidebar.text_input("Product Name")
product_type = st.sidebar.text_input("Product Type")
audience = st.sidebar.text_input("Target Audience")
problem = st.sidebar.text_area("Customer Problem")
usp = st.sidebar.text_area("USP")
platform = st.sidebar.selectbox("Platform", ["Instagram Reels", "YouTube Shorts", "Facebook Ads"])
tone = st.sidebar.selectbox("Tone", ["Casual", "Emotional", "Luxury", "Funny"])

# ---------- VIRAL SCORE FUNCTION ----------
def calculate_score(hook):
    score = 0
    if "?" in hook:
        score += 2
    if any(word in hook.lower() for word in ["secret", "shocking", "never", "finally"]):
        score += 3
    if any(word in hook.lower() for word in ["you", "your"]):
        score += 2
    if len(hook.split()) <= 12:
        score += 3
    return min(score, 10)

# ---------- GENERATE ----------
if st.sidebar.button("✨ Generate UGC Ads"):

    if not product_name or not problem:
        st.warning("⚠️ Fill required fields")
    else:
        with st.spinner("Generating viral content... 🚀"):

            prompt = f"""
            You are a UGC ads expert.

            Create high-converting skincare ad content.

            Product: {product_name}
            Type: {product_type}
            Audience: {audience}
            Problem: {problem}
            USP: {usp}
            Platform: {platform}
            Tone: {tone}

            Return STRICT JSON:

            {{
              "hooks": ["", "", "", "", ""],
              "script": "",
              "cta": "",
              "timing": {{
                "hook": "",
                "problem": "",
                "solution": "",
                "cta": ""
              }}
            }}
            """

            model = genai.GenerativeModel("gemini-2.5-flash")
            response = model.generate_content(prompt)

            raw = response.text

            match = re.search(r"\{.*\}", raw, re.DOTALL)

            if match:
                try:
                    data = json.loads(match.group(0))
                except:
                    st.error("Parsing failed")
                    st.code(raw)
                    st.stop()
            else:
                st.error("No JSON found")
                st.code(raw)
                st.stop()

        st.success("✅ Content Generated!")

        # ---------- HOOKS WITH SCORE ----------
        st.markdown("## 🔥 Hooks + Viral Score")

        cols = st.columns(2)

        for i, hook in enumerate(data["hooks"]):
            score = calculate_score(hook)

            with cols[i % 2]:
                st.markdown(f"""
                <div class="card">
                <div class="title">Hook {i+1}</div>
                <p>{hook}</p>
                <b>🔥 Viral Score: {score}/10</b>
                </div>
                """, unsafe_allow_html=True)

        st.markdown("---")

        # ---------- SCRIPT ----------
        st.markdown("## 🎬 Main Script")
        st.markdown(f"""
        <div class="card">
        {data["script"]}
        </div>
        """, unsafe_allow_html=True)

        st.markdown("---")

        # ---------- CTA ----------
        st.markdown("## 📢 CTA")
        st.success(data["cta"])

        st.markdown("---")

        # ---------- TIMING ----------
        st.markdown("## ⏱️ Video Timing Breakdown")

        timing = data["timing"]

        st.markdown(f"""
        <div class="card">
        ⏱ Hook: {timing['hook']} <br><br>
        😟 Problem: {timing['problem']} <br><br>
        💡 Solution: {timing['solution']} <br><br>
        📢 CTA: {timing['cta']}
        </div>
        """, unsafe_allow_html=True)

        st.markdown("---")

        # ---------- DOWNLOAD ----------
        st.download_button(
            "📥 Download Ad Script",
            data=json.dumps(data, indent=2),
            file_name="ugc_ads.json"
        )