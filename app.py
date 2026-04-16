import streamlit as st
from google import genai
from google.genai import types
from PIL import Image
import re
import time

# 1. Page Configuration & High-Density CSS
st.set_page_config(page_title="Falcon NSN Lock", page_icon="🦅", layout="wide")

st.markdown("""
    <style>
    .main { background-color: #0e1117; color: #f0f2f6; font-family: 'Inter', sans-serif; }
    
    /* CARD HIERARCHY */
    .decision-card {
        background-color: #1a1d2e; border-radius: 8px; 
        padding: 12px 18px; margin-bottom: 12px;
        border: 1px solid #2d314c;
    }
    .primary-card { border: 2px solid #00d4ff; box-shadow: 0 0 15px rgba(0, 212, 255, 0.2); }
    .alt-card { opacity: 0.85; border: 1px solid #3e4463; }
    
    /* NSN PROMINENCE */
    .nsn-display { 
        font-family: 'Roboto Mono', monospace; font-size: 1.6em; 
        font-weight: 800; color: #ffffff; letter-spacing: 1px;
    }
    .nomenclature { font-size: 0.95em; color: #bdc3c7; margin-bottom: 4px; }
    
    /* CONFIDENCE LABELS */
    .conf-high { color: #2ecc71; font-weight: bold; font-size: 1.2em; }
    .conf-med { color: #f1c40f; font-weight: bold; font-size: 1.2em; }
    .conf-low { color: #e74c3c; font-weight: bold; font-size: 1.2em; }

    /* LOADER BAR */
    @keyframes progress-animation { 0% { width: 0%; } 100% { width: 100%; } }
    .falcon-bar-container { width: 100%; height: 4px; background: #2d314c; position: fixed; top: 0; left: 0; z-index: 9999; }
    .falcon-bar-fill { height: 100%; background: #00d4ff; animation: progress-animation 3s linear infinite; }
    </style>
    """, unsafe_allow_html=True)

# 2. Sidebar: Tightened Input
with st.sidebar:
    st.image("https://upload.wikimedia.org/wikipedia/commons/thumb/d/d3/Seal_of_the_United_States_Department_of_the_Air_Force.svg/1200px-Seal_of_the_United_States_Department_of_the_Air_Force.svg.png", width=50)
    st.title("Falcon Dashboard")
    st.caption("v2.0 // Decision-Centric Mode")
    st.divider()
    
    equipment_class = st.selectbox(
        "Select Equipment/Part Class:", 
        ["Select...", "Generator", "Heater", "Compressor", "Towbar"],
        help="Start broad to narrow NSN family."
    )
    
    uploaded_file = st.file_uploader("Upload Scan", type=["jpg", "png"], label_visibility="collapsed")
    
    with st.expander("Manual Refinement (P/N)"):
        cues = st.text_input("Input P/N or Marks:", value="idk")

# 3. Decision Interface Layout
col_left, col_right = st.columns([1, 1.4])

with col_left:
    if uploaded_file:
        img = Image.open(uploaded_file)
        st.image(img, use_container_width=True)
        # Dynamic Class Detection Label
        st.markdown(f"**Detected Class:** `{equipment_class if equipment_class != 'Select...' else 'Analyzing...'}`")
        
        execute = st.button("🚀 Lock NSN & Proceed", use_container_width=True, type="primary")

with col_right:
    if uploaded_file and execute:
        # --- LOADING STATES ---
        loader = st.empty()
        states = ["Identifying class...", "Matching NSNs...", "Validating against inventory..."]
        for state in states:
            loader.markdown(f"""
                <div class="falcon-bar-container"><div class="falcon-bar-fill"></div></div>
                <p style="color:#00d4ff; font-family:monospace; text-align:center;">{state}</p>
            """, unsafe_allow_html=True)
            time.sleep(0.8)
        loader.empty()

        # Simulated API Extraction
        # In production, this pulls from your response.text regex
        results = [
            {"nsn": "4520-01-135-2770", "name": "HEATER, GROUND SUPPORT (H-1)", "conf": 94, "just": "Verified by vertical exhaust stowage & trailer chassis."},
            {"nsn": "4520-01-482-8571", "name": "NEW GENERATION HEATER (NGH-1)", "conf": 82, "just": "Alternative profile; lacks H-1 specific enclosure."},
            {"nsn": "4510-01-229-3451", "name": "HEATER, SPACE, MEDIUM", "conf": 55, "just": "Incorrect chassis layout for trailer mount."}
        ]

        # 4. TOP NSN MATCHES (RANKING STACK)
        st.subheader("Top NSN Matches")
        
        for i, res in enumerate(results):
            is_primary = (i == 0)
            c_class = "conf-high" if res['conf'] >= 85 else ("conf-med" if res['conf'] >= 60 else "conf-low")
            card_type = "primary-card" if is_primary else "alt-card"
            label = "RECOMMENDED" if is_primary else f"ALTERNATIVE {i+1}"
            
            with st.container():
                st.markdown(f"""
                <div class="decision-card {card_type}">
                    <div style="display: flex; justify-content: space-between; align-items: start;">
                        <span style="font-size: 0.7em; font-weight: bold; color: #888;">{label}</span>
                        <span class="{c_class}">{res['conf']}%</span>
                    </div>
                    <div class="nomenclature">{res['name']}</div>
                    <div style="display: flex; justify-content: space-between; align-items: center;">
                        <span class="nsn-display">{res['nsn']}</span>
                    </div>
                    <p style="font-size: 0.8em; color: #999; margin-top: 8px;"><em>{res['just']}</em></p>
                </div>
                """, unsafe_allow_html=True)
                
                # Actionable buttons per card
                c1, c2, c3 = st.columns([1, 1, 1])
                with c1: st.button(f"📋 Copy", key=f"copy_{i}")
                with c2: st.button(f"📤 JetDash", key=f"jet_{i}")
                with c3: 
                    if is_primary: st.button("✅ Verify Lock", type="primary", key=f"lock_{i}")

        # 5. Low Separation Warning
        if abs(results[0]['conf'] - results[1]['conf']) < 15:
            st.warning("⚠️ Low separation between top matches — verify visual markers manually.")

        # 6. Collapsed Analysis
        with st.expander("Diagnostic Markers & Technical Backlog"):
            st.write("**Visual Match Breakdown:**")
            st.write("- Exhaust Stack Configuration: Match")
            st.write("- Chassis Mounting: Match (Trailer)")
            st.divider()
            st.write("**Inventory Leads:** 4520-00-511-2092, 4520-01-329-3451...")

        st.button("TRANSMIT TO PROD SHOP", use_container_width=True)
