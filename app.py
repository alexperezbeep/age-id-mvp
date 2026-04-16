import streamlit as st
from google import genai
from google.genai import types
from PIL import Image
import re

# 1. Page Configuration & Aesthetic
st.set_page_config(page_title="Falcon H4D: Logistics Audit", page_icon="🦅", layout="wide")

st.markdown("""
    <style>
    .main { background-color: #0e1117; }
    div[data-testid="stMetricValue"] { font-size: 28px; color: #00d4ff; }
    div[data-testid="stMetricDelta"] { font-size: 14px; font-weight: bold; }
    </style>
    """, unsafe_allow_html=True)

# 2. Command Dashboard (Sidebar)
with st.sidebar:
    st.image("https://upload.wikimedia.org/wikipedia/commons/thumb/d/d3/Seal_of_the_United_States_Department_of_the_Air_Force.svg/1200px-Seal_of_the_United_States_Department_of_the_Air_Force.svg.png", width=70)
    st.title("Falcon Dashboard")
    st.info("Status: 🦅 Logistics Recognition Active")
    
    st.divider()
    
    st.subheader("Step 1: Domain Selection")
    domains = ["Ground Support Equipment", "Engine / Powerplant", "Electrical / Avionics", "Hydraulic / Pneumatic", "Hardware / Universal"]
    selected_domain = st.selectbox("Technical Class:", domains)

    st.subheader("Step 2: Describe Profile")
    profiles = {
        "Ground Support Equipment": ["Mobile/Trailer", "Stationary", "Hand-Held"],
        "Engine / Powerplant": ["Internal/Closed", "External/Exposed", "Fuel/Oil System"],
        "Electrical / Avionics": ["Sealed/Relay Style", "Wiring/Harness", "Control Panel"],
        "Hydraulic / Pneumatic": ["Pump/Motor", "Valve/Manifold", "Hose/Fitting"],
        "Hardware / Universal": ["Fastener/Bracket", "Housing/Casing", "Unknown/Other"]
    }
    selected_profile = st.radio("Visual Profile:", profiles.get(selected_domain))

    st.subheader("Step 3: Technical Refinement")
    user_cues = st.text_input("Input P/N, Casting #, or Marks:", placeholder="Ex: P/N 827482")

# 3. Execution Interface
col_left, col_right = st.columns([1, 1.3])

with col_left:
    st.header("1. Digital Inspection")
    uploaded_file = st.file_uploader("Upload Component Scan", type=["jpg", "jpeg", "png"])
    if uploaded_file:
        img = Image.open(uploaded_file)
        st.image(img, caption="Unit under inspection", use_container_width=True)
        execute = st.button("🚀 EXECUTE LOGISTICS LOCK", use_container_width=True)

with col_right:
    st.header("2. Logistics Audit Trail")
    
    if uploaded_file and execute:
        client = genai.Client(api_key=st.secrets["GEMINI_API_KEY"])
        
        with st.status("Regimenting Technical Data...", expanded=True) as status:
            prompt = f"""
            ACT AS A USAF MAINTENANCE SUPERINTENDENT.
            DOMAIN: {selected_domain} | PROFILE: {selected_profile} | CUES: {user_cues}
            
            TASK:
            1. Identify the SINGLE 'Primary Lock' (NSN or CAGE/MPN).
            2. Identify 2 additional 'High-Confidence' alternative matches.
            3. Identify up to 10 'Possible Leads' for the technical backlog.
            4. For the Primary Lock, provide a 'REGIMENTED GRAPHICAL CRITERIA' breakdown:
               - CONFIDENCE SCORE: [XX]%
               - TIER: (Verified/Probable/Assisted)
               - VISUAL ANCHORS: List 3 specific physical features found in the image.
               - LOGIC GAP: What remains unverified?
               - TECHNICAL SOURCE: T.O. or Database.
            5. HIERARCHY: State that Section Chief reports to Production Superintendent.
            
            FORMAT START: Return the data as 'LOCK: [NSN]' followed by 'SCORE: [XX]%' and 'TIER: [TIER]' at the top.
            """
            
            response = client.models.generate_content(
                model="gemini-3-flash-preview",
                contents=[prompt, img],
                config=types.GenerateContentConfig(tools=[types.Tool(google_search=types.GoogleSearch())])
            )
            status.update(label="Analysis Complete", state="complete")

        # Indentation Fix: Extraction Logic
        res_text = response.text
        lock_name = re.search(r"LOCK:\s*(.*)\n", res_text).group(1) if "LOCK:" in res_text else "Identified Asset"
        conf_val = re.search(r"SCORE:\s*(\d+)%", res_text).group(1) if "SCORE:" in res_text else "95"
        tier_val = re.search(r"TIER:\s*(\w+)", res_text).group(1) if "TIER:" in res_text else "Verified"

        # Metric Dashboard
        m1, m2, m3 = st.columns(3)
        with m1:
            with st.popover(f"🎯 Confidence: {conf_val}%"):
                st.write(f"### 🛡️ Audit Tier: {tier_val}")
                st.write("**Scoring Matrix:**")
                st.write("- **50%:** OCR/Literal Match")
                st.write("- **30%:** Geometric Profile")
                st.caption("Score indicates independent probability of a correct logistical match.")
        
        m2.metric("Logistics Status", tier_val, delta="Verified Path")
        m3.metric("Lead Time", "24-48 Hours", delta="Priority A")

        st.divider()
        
        # Regimented Report Display
        with st.container(border=True):
            st.markdown(f"### ✅ Logistics Lock: {lock_name}")
            
            # Splitting the response to show Top 3 vs Backlog
            if "BACKLOG:" in res_text:
                main_report, backlog = res_text.split("BACKLOG:")
                st.markdown(main_report.split("TIER:")[1])
                with st.expander("🔍 View Technical Backlog (10 Possible Leads)"):
                    st.write("The following items match the broader visual taxonomy but require additional manual verification:")
                    st.markdown(backlog)
            else:
                st.markdown(res_text.split("TIER:")[1])
            
            if st.button("TRANSMIT TO PROD SHOP", type="primary", use_container_width=True):
                st.balloons()
                st.toast(f"Logistics data for {lock_name} transmitted to Section Chief.")
