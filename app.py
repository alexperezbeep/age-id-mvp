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
    
    /* SYMMETRY FIX: Unified Logistics Card Style */
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

    /* ADVANCED WARZONE LOADER */
    #warzone-loader-container {
        position: fixed; top: 0; left: 0; width: 100%; height: 100%;
        background-color: rgba(14, 17, 23, 0.95); z-index: 9999;
        display: none; flex-direction: column; justify-content: center; align-items: center;
    }
    #falcon-path {
        width: 80%; height: 20px; background-color: #2d314c;
        border-radius: 10px; position: relative; overflow: hidden;
    }
    #falcon-progress {
        height: 100%; background-color: #00d4ff;
        width: 0%; border-radius: 10px; transition: width 0.1s linear;
    }
    #falcon-silhouette {
        position: absolute; top: -15px; left: 0%;
        font-size: 35px; color: #00d4ff;
        transition: left 0.1s linear;
    }
    #loading-text { color: #00d4ff; font-family: monospace; font-weight: bold; margin-top: 15px; }
    
    /* Simple inline JS to trigger the loader on button click */
    script { display: none; }
    </style>
    <script>
    function showWarzoneLoader() {
        document.getElementById('warzone-loader-container').style.display = 'flex';
        let progress = 0;
        const progressBar = document.getElementById('falcon-progress');
        const silhouette = document.getElementById('falcon-silhouette');
        
        const interval = setInterval(() => {
            progress += 1; // 1% per tick
            progressBar.style.width = progress + '%';
            silhouette.style.left = progress + '%';
            
            if (progress >= 100) {
                clearInterval(interval);
                // The form submission will reload the page and hide the loader
            }
        }, 30); // 3 seconds total duration (approx)
    }
    </script>
    """, unsafe_allow_html=True)

# --- 2. ADVANCED WARZONE LOADER HTML (Hidden until trigger) ---
# For the demo, we use emojis to represent the tactical elements of the map.
st.markdown("""
<div id="warzone-loader-container">
    <div id="loading-map" style="font-family: monospace; white-space: pre; color: #f0f2f6; opacity: 0.3; font-size: 1.1em; margin-bottom: 30px;">
    [TAC_MAP_92MXS]
    <br>🏔️🏔️      [DLA_DB]      🏝️
    <br>      🚁                  
    <br>   🟥 [H-1]          🟦 [HQ]
    <br>                      
    <br>      🏔️🏔️ [MINOT]         🏔️
    </div>
    <div id="falcon-path">
        <div id="falcon-progress"></div>
        <div id="falcon-silhouette">🦅</div>
    </div>
    <p id="loading-text">FALCON STRIKE: SCRUBBING GROUND SUPPORT DATA...</p>
</div>
""", unsafe_allow_html=True)

# 3. Sidebar (Command Dashboard)
with st.sidebar:
    st.image("https://upload.wikimedia.org/wikipedia/commons/thumb/d/d3/Seal_of_the_United_States_Department_of_the_Air_Force.svg/1200px-Seal_of_the_United_States_Department_of_the_Air_Force.svg.png", width=70)
    st.title("Falcon Dashboard")
    st.info("Status: 🦅 Logistics Recognition Active")
    st.divider()
    selected_domain = st.selectbox("Technical Class:", ["Ground Support Equipment", "Engine", "Electrical", "Hydraulic"])
    user_cues = st.text_input("Refinement (P/N, Casting #, or Marks):", placeholder="Ex: idk")

# 4. Execution Interface
col_left, col_right = st.columns([1, 1.4])

with col_left:
    st.header("1. Digital Inspection")
    uploaded_file = st.file_uploader("Upload Component Scan", type=["jpg", "jpeg", "png"])
    if uploaded_file:
        img = Image.open(uploaded_file)
        st.image(img, caption="Flight Line Unit", use_container_width=True)
        
        # Trigger loader via simple JS on click
        st.markdown('<button onclick="showWarzoneLoader()" style="width:100%; padding:10px; background-color:#1a1d2e; border: 2px solid #2d314c; color: #f0f2f6; border-radius:8px; cursor:pointer;">🚀 EXECUTE LOGISTICS LOCK</button>', unsafe_allow_html=True)
        
        # Streamlit doesn't handle JS triggers well with its own buttons. 
        # For the final code, this requires integrating a Streamlit component.
        # As a demo fallback, we use a hidden form to reload.
        with st.form("exec_form", clear_on_submit=True):
             execute = st.form_submit_submit_button("LOCK", help="Trigger API call and loader", use_container_width=True)

with col_right:
    st.header("2. Logistics Audit Trail")
    
    # We use a simulated execute here to always show results after upload for the demo.
    # Replace 'True' with 'uploaded_file and execute' in your live script.
    if uploaded_file: 
        # Add a small delay so the loader can fly before results render
        time.sleep(3.5)
        
        # simulated response (replace with Gemini API call)
        res_text = """
        NSN_1: 4520-00-541-1115 | KEY_1: HEATER, DUCT TYPE, PORTABLE (MODEL H-1)
        NSN_2: 4520-01-439-1682 | KEY_2: HEATER, DUCT TYPE, PORTABLE (MODEL H-120-1 / ASH)
        NSN_3: 4520-01-496-4100 | KEY_3: NEW GENERATION HEATER (NGH) - SYSTEM REPLACEMENT
        """
        
        st.subheader("🛡️ Verified Logistics Matches")
        
        # Extraction logic
        matches = re.findall(r"NSN_(\d+):\s*([\d-]+)\s*\|\s*KEY_\1:\s*(.*)", res_text)

        if not matches:
            st.warning("No precise NSN lock. Reviewing Backlog...")
        else:
            for i, nsn, key in matches:
                # SYMMETRY FIX: Unified Logistics Card Structure
                # Directly injecting HTML for precise layout control
                img_url = f"https://www.iso-group.com/Public/Images/NSN/{nsn.strip()}.jpg"
                
                header_style = "primary-lock" if i == "1" else "alternative-lock"
                badge = "🥇 PRIMARY LOCK" if i == "1" else f"🥈 ALTERNATIVE {i}"
                success_note = '<div style="background-color: #1e3a1e; border: 1px solid #3a7a3a; color: #c4fcc4; padding: 10px; border-radius: 5px; margin-top: 10px; font-size: 0.9em; font-weight: bold;">Logistics Match Confirmed via Visual Anchors.</div>' if i == '1' else ''

                st.markdown(f"""
                <div class="logistics-card">
                    <div class="card-header {header_style}">{badge}</div>
                    <div style="display: flex; gap: 20px; align-items: start; margin-top: 15px;">
                        <div style="flex: 1; max-width: 150px; text-align: center;">
                            <img src="{img_url}" alt="DLA Source IPB" style="width: 100%; border: 1px solid #2d314c; border-radius: 8px;">
                            <p style="font-family: monospace; font-size: 0.8em; color: #f0f2f6; margin-top: 5px;">IPB Diagram: {nsn}</p>
                        </div>
                        <div style="flex: 2;">
                            <code style="display: block; font-family: monospace; background-color: #0e1117; padding: 10px; border-radius: 5px; font-size: 1em; color: #f0f2f6; margin-bottom: 10px;">NSN: {nsn}</code>
                            <p style="margin: 0;"><strong>Nomenclature:</strong> {key}</p>
                            {success_note}
                        </div>
                    </div>
                </div>
                """, unsafe_allow_html=True)

        # 5. Backlog
        with st.expander("🔍 View Technical Backlog (10 Leads)"):
            st.write("Broader taxonomy matches below:")
            # Logic to print the backlog from AI response
            st.code("4520-00-511-2092 (Legacy H-1 Variant)")
            st.code("4520-01-329-3451 (H-45 Medium Space Heater)")
            # ... add other backlog entries here ...

        if st.button("TRANSMIT TO PROD SHOP", type="primary", use_container_width=True):
            st.balloons()
            st.toast("Full Audit transmitted to Production Superintendent.")
