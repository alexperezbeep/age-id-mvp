import streamlit as st
from google import genai
from google.genai import types
from PIL import Image
import re
import time

# 1. Page Configuration & Advanced CSS
st.set_page_config(page_title="Falcon H4D: NSN Audit", page_icon="🦅", layout="wide")

st.markdown("""
    <style>
    .main { background-color: #0e1117; color: #f0f2f6; }
    
    /* SYMMETRIC LOGISTICS CARDS */
    .logistics-card {
        background-color: #1a1d2e; border: 2px solid #2d314c;
        border-radius: 12px; padding: 20px; margin-bottom: 20px;
        box-shadow: 0 4px 6px rgba(0,0,0,0.3);
    }
    .primary-lock { color: #00d4ff; border-left: 5px solid #00d4ff; padding-left: 15px; }
    .alternative-lock { color: #f0f2f6; border-left: 5px solid #444; padding-left: 15px; }

    /* WARZONE LOADER */
    @keyframes fly { from { left: -10%; } to { left: 105%; } }
    .warzone-container {
        position: relative; width: 100%; height: 80px;
        background: #0e1117; border: 1px solid #2d314c;
        border-radius: 8px; overflow: hidden; margin: 20px 0;
    }
    .warzone-bg {
        position: absolute; width: 100%; height: 100%;
        opacity: 0.15; font-family: monospace; font-size: 10px;
        white-space: pre; color: #00d4ff; line-height: 1.2;
    }
    .falcon-flyer {
        position: absolute; top: 20px; font-size: 30px;
        animation: fly 3s linear infinite;
    }
    .progress-fill {
        height: 100%; background: rgba(0, 212, 255, 0.2);
        transition: width 0.1s linear;
    }
    </style>
    """, unsafe_allow_html=True)

# 2. Sidebar: Command Inputs
with st.sidebar:
    st.image("https://upload.wikimedia.org/wikipedia/commons/thumb/d/d3/Seal_of_the_United_States_Department_of_the_Air_Force.svg/1200px-Seal_of_the_United_States_Department_of_the_Air_Force.svg.png", width=70)
    st.title("Falcon Dashboard")
    st.info("Status: 🦅 NSN Resolution Active")
    st.divider()
    domain = st.selectbox("Technical Class:", ["Ground Support Equipment", "Engine", "Electrical", "Hydraulic"])
    cues = st.text_input("Input P/N, Casting #, or Marks:", placeholder="Ex: idk")

# 3. Main Interface
col_left, col_right = st.columns([1, 1.4])

with col_left:
    st.header("1. Digital Inspection")
    uploaded_file = st.file_uploader("Upload Component Scan", type=["jpg", "jpeg", "png"])
    if uploaded_file:
        img = Image.open(uploaded_file)
        st.image(img, caption="Flight Line Unit", use_container_width=True)
        
        with st.form("exec_form"):
             execute = st.form_submit_button("🚀 EXECUTE LOGISTICS LOCK", use_container_width=True)

with col_right:
    st.header("2. Logistics Audit Trail")
    
    if uploaded_file and execute:
        # --- WARZONE LOADER RENDER (0-100%) ---
        loader_placeholder = st.empty()
        for p in range(0, 101, 2):
            loader_placeholder.markdown(f"""
            <div class="warzone-container">
                <div class="warzone-bg">TAC_MAP_92MXS // OBSTACLE_REMOVED // DLA_LINK_ESTABLISHED // SCRUBBING_FEDLOG</div>
                <div class="progress-fill" style="width: {p}%;"></div>
                <div class="falcon-flyer" style="left: {p-10}%;">🦅</div>
            </div>
            <p style="text-align:center; color:#00d4ff; font-family:monospace; font-weight:bold;">STRIKE STATUS: {p}% COMPLETE</p>
            """, unsafe_allow_html=True)
            time.sleep(0.05)
        loader_placeholder.empty()

        # 4. NSN-CENTRIC AI LOGIC
        client = genai.Client(api_key=st.secrets["GEMINI_API_KEY"])
        prompt = f"""
        ACT AS A USAF MAINTENANCE SUPERINTENDENT. 
        OBJECTIVE: Accurate NSN identification from image.
        1. Identify Class (e.g. Heater, Generator).
        2. Identify Top 3 NSN Matches with Confidence % and diagnostic justification.
        3. Detailed markers for Best Match.
        4. List 10 'Possible Leads' for backlog.

        FORMAT FOR PARSING:
        CLASS: [Class Name]
        NSN_1: [NSN] | NAME_1: [Nomenclature] | CONF_1: [XX%] | JUST_1: [Reason]
        NSN_2: [NSN] | NAME_2: [Nomenclature] | CONF_2: [XX%] | JUST_2: [Reason]
        NSN_3: [NSN] | NAME_3: [Nomenclature] | CONF_3: [XX%] | JUST_3: [Reason]
        ---REPORT---
        [Detailed Diagnostics]
        """
        
        response = client.models.generate_content(
            model="gemini-3-flash-preview",
            contents=[prompt, img],
            config=types.GenerateContentConfig(tools=[types.Tool(google_search=types.GoogleSearch())])
        )
        res_text = response.text

        # 5. Symmetric UI Rendering
        st.subheader("🛡️ Top NSN Matches")
        
        # Parse logic
        matches = re.findall(r"NSN_(\d+):\s*([\d-]+)\s*\|\s*NAME_\1:\s*(.*?)\s*\|\s*CONF_\1:\s*(.*?)\s*\|\s*JUST_\1:\s*(.*)", res_text)

        if matches:
            for i, nsn, name, conf, just in matches:
                # Direct IPB Link
                img_url = f"https://www.iso-group.com/Public/Images/NSN/{nsn.strip()}.jpg"
                is_primary = (i == "1")
                card_style = "primary-lock" if is_primary else "alternative-lock"
                
                st.markdown(f"""
                <div class="logistics-card">
                    <div class="card-header {card_style}">{'🥇 PRIMARY LOCK' if is_primary else f'🥈 ALTERNATIVE {i}'} ({conf})</div>
                    <div style="display: flex; gap: 20px; align-items: start; margin-top: 15px;">
                        <div style="flex: 1; max-width: 140px; text-align: center;">
                            <img src="{img_url}" style="width: 100%; border: 1px solid #2d314c; border-radius: 8px;">
                            <p style="font-family: monospace; font-size: 0.7em; color: #888; margin-top: 5px;">IPB: {nsn}</p>
                        </div>
                        <div style="flex: 2;">
                            <code style="display: block; background: #0e1117; padding: 8px; border-radius: 4px; color: #00d4ff; margin-bottom: 8px;">NSN: {nsn}</code>
                            <p style="margin: 0; font-size: 0.9em;"><strong>{name}</strong></p>
                            <p style="margin-top: 8px; font-size: 0.85em; color: #ccc;"><em>{just}</em></p>
                        </div>
                    </div>
                </div>
                """, unsafe_allow_html=True)
        
        # 6. Detailed Diagnostics & Backlog
        with st.expander("🔍 Diagnostic Markers & Technical Backlog"):
            st.markdown(res_text.split("---REPORT---")[-1] if "---REPORT---" in res_text else "Audit Complete.")

        if st.button("TRANSMIT TO PROD SHOP", type="primary", use_container_width=True):
            st.balloons()
            st.toast("NSN-Centric Audit Transmitted.")
