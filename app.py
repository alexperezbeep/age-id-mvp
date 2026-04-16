import streamlit as st
from google import genai
from google.genai import types
from PIL import Image
import re
import time

# 1. Page Configuration & Custom CSS for Advanced Loader and Symmetric Layout
st.set_page_config(page_title="Falcon H4D: Visual Audit", page_icon="🦅", layout="wide")

st.markdown("""
    <style>
    .main { background-color: #0e1117; color: #f0f2f6; }
    
    /* SYMMETRY: Unified Logistics Card Style */
    .logistics-card {
        background-color: #1a1d2e; border: 2px solid #2d314c;
        border-radius: 12px; padding: 20px;
        margin-bottom: 20px; box-shadow: 0 4px 6px rgba(0,0,0,0.3);
        transition: transform 0.2s ease, border-color 0.2s ease;
    }
    .logistics-card:hover { transform: translateY(-3px); border-color: #00d4ff; }
    .card-header { font-family: monospace; font-weight: bold; font-size: 1.1em; color: #f0f2f6; }
    .primary-lock { color: #00d4ff; border-left: 5px solid #00d4ff; padding-left: 15px; }
    .alternative-lock { color: #f0f2f6; border-left: 5px solid #2d314c; padding-left: 15px; }

    /* WARZONE LOADER ANIMATION */
    @keyframes fly { from { left: -10%; } to { left: 100%; } }
    .warzone-container {
        position: relative; width: 100%; height: 60px;
        background: #0e1117; border: 1px solid #2d314c;
        border-radius: 8px; overflow: hidden; margin: 20px 0;
    }
    .warzone-bg {
        position: absolute; width: 100%; height: 100%;
        opacity: 0.1; font-family: monospace; font-size: 10px;
        white-space: pre; color: #00d4ff;
    }
    .falcon-flyer {
        position: absolute; top: 15px; left: -10%;
        font-size: 24px; animation: fly 3s linear infinite;
    }
    .progress-bar-fill {
        height: 100%; background: rgba(0, 212, 255, 0.2);
        width: 0%; transition: width 0.1s linear;
    }
    </style>
    """, unsafe_allow_html=True)

# 2. Sidebar (Command Dashboard)
with st.sidebar:
    st.image("https://upload.wikimedia.org/wikipedia/commons/thumb/d/d3/Seal_of_the_United_States_Department_of_the_Air_Force.svg/1200px-Seal_of_the_United_States_Department_of_the_Air_Force.svg.png", width=70)
    st.title("Falcon Dashboard")
    selected_domain = st.selectbox("Technical Class:", ["Ground Support Equipment", "Engine", "Electrical", "Hydraulic"])
    user_cues = st.text_input("Refinement (P/N, Casting #, or Marks):", placeholder="Ex: idk")

# 3. Execution Interface
col_left, col_right = st.columns([1, 1.4])

with col_left:
    st.header("1. Digital Inspection")
    uploaded_file = st.file_uploader("Upload Component Scan", type=["jpg", "jpeg", "png"])
    if uploaded_file:
        img = Image.open(uploaded_file)
        st.image(img, caption="Flight Line Unit", use_container_width=True)
        
        with st.form("exec_form"):
             # FIXED: Corrected function name here
             execute = st.form_submit_button("🚀 EXECUTE LOGISTICS LOCK", use_container_width=True)

with col_right:
    st.header("2. Logistics Audit Trail")
    
    if uploaded_file and execute:
        # --- WARZONE LOADER RENDER ---
        loader_placeholder = st.empty()
        for percent in range(0, 101, 5):
            loader_placeholder.markdown(f"""
            <div class="warzone-container">
                <div class="warzone-bg">MTN_TERRAIN_01 // OBSTACLE_REMOVED // DLA_LINK_ESTABLISHED</div>
                <div class="progress-bar-fill" style="width: {percent}%;"></div>
                <div class="falcon-flyer" style="left: {percent-5}%;">🦅</div>
            </div>
            <p style="text-align:center; color:#00d4ff; font-family:monospace;">STRIKE STATUS: {percent}% COMPLETE</p>
            """, unsafe_allow_html=True)
            time.sleep(0.1)
        loader_placeholder.empty()

        # API Call
        client = genai.Client(api_key=st.secrets["GEMINI_API_KEY"])
        prompt = "Identify Primary NSN + 2 High-Confidence Alternatives. FORMAT: NSN_1: [NSN] | KEY_1: [Nomenclature] etc. Include a '---REPORT---' section."
        
        response = client.models.generate_content(
            model="gemini-3-flash-preview",
            contents=[prompt, img],
            config=types.GenerateContentConfig(tools=[types.Tool(google_search=types.GoogleSearch())])
        )
        res_text = response.text

        # 4. Symmetric Logistics Cards
        st.subheader("🛡️ Verified Logistics Matches")
        matches = re.findall(r"NSN_(\d+):\s*([\d-]+)\s*\|\s*KEY_\1:\s*(.*)", res_text)

        if matches:
            for i, nsn, key in matches:
                img_url = f"https://www.iso-group.com/Public/Images/NSN/{nsn.strip()}.jpg"
                header_style = "primary-lock" if i == "1" else "alternative-lock"
                badge = "🥇 PRIMARY LOCK" if i == "1" else f"🥈 ALTERNATIVE {i}"
                
                st.markdown(f"""
                <div class="logistics-card">
                    <div class="card-header {header_style}">{badge}</div>
                    <div style="display: flex; gap: 20px; align-items: start; margin-top: 15px;">
                        <div style="flex: 1; max-width: 150px; text-align: center;">
                            <img src="{img_url}" style="width: 100%; border: 1px solid #2d314c; border-radius: 8px;">
                            <p style="font-family: monospace; font-size: 0.7em; color: #888; margin-top: 5px;">IPB: {nsn}</p>
                        </div>
                        <div style="flex: 2;">
                            <code style="display: block; background: #0e1117; padding: 8px; border-radius: 4px; margin-bottom: 8px;">NSN: {nsn}</code>
                            <p style="margin: 0; font-size: 0.95em;"><strong>Nomenclature:</strong> {key}</p>
                        </div>
                    </div>
                </div>
                """, unsafe_allow_html=True)
        
        with st.expander("🔍 View Technical Backlog (10 Leads)"):
            st.markdown(res_text.split("---REPORT---")[-1] if "---REPORT---" in res_text else "Audit Complete.")

        if st.button("TRANSMIT TO PROD SHOP", type="primary", use_container_width=True):
            st.balloons()
