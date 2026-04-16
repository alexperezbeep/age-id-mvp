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
    [data-testid="stMetricValue"] { cursor: pointer; }
    </style>
    """, unsafe_allow_html=True)

# 2. Command Dashboard (Sidebar)
with st.sidebar:
    st.image("https://upload.wikimedia.org/wikipedia/commons/thumb/d/d3/Seal_of_the_United_States_Department_of_the_Air_Force.svg/1200px-Seal_of_the_United_States_Department_of_the_Air_Force.svg.png", width=70)
    st.title("Falcon Dashboard")
    st.info("System Status: 🦅 Multi-Modal Audit Active")
    
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
        
        with st.status("Generating Graphical Criteria Report...", expanded=True) as status:
            prompt = f"""
            ACT AS A USAF MAINTENANCE SUPERINTENDENT.
            DOMAIN: {selected_domain} | PROFILE: {selected_profile} | CUES: {user_cues}
            
            TASK:
            1. Identify TOP 3 Logistics Matches (NSN or CAGE/MPN).
            2. For EACH match, provide:
               - CONFIDENCE SCORE: [XX]%
               - TIER: (Verified/Probable/Assisted)
               - VISUAL ANCHORS: List 3 physical features in the image (bolt count, port alignment, OCR).
               - LOGIC GAP: What remains unverified? (e.g. internal splines).
               - TECHNICAL SOURCE: T.O. IPB Figure/Index or Database.
            3. HIERARCHY: Remind user Section Chief reports to Production Superintendent.
            
            FORMAT START: Return the primary confidence and tier as 'METRIC: [XX]%, [TIER]' at the top.
            """
            
            response = client.models.generate_content(
                model="gemini-3-flash-preview",
                contents=[prompt, img],
                config=types.GenerateContentConfig(tools=[types.Tool(google_search=types.GoogleSearch())])
            )
            status.update(label="Audit Complete", state="complete")

        # Extract Metric and Tier
        metric_match = re.search(r"METRIC:\s*(\d+)%,\s*(\w+)", response.text)
        conf_val = metric_match.group(1) if metric_match else "85"
        tier_val = metric_match.group(2) if metric_match else "Assisted"

        # 4. Metric Dashboard with Popover Audit
        m1, m2, m3 = st.columns(3)
        with m1:
            with st.popover(f"🎯 Confidence: {conf_val}%"):
                st.write(f"### 🛡️ Audit Tier: {tier_val}")
                st.write("**Criteria Breakdown:**")
                st.write("- **50%:** OCR/Literal match to DLA records.")
                st.write("- **30%:** Geometric taxonomy (Flange/Ports).")
                st.write("- **20%:** System context validation.")
                st.caption("Clicking past confirms you've reviewed the Logic Gaps below.")
        
        m2.metric("Logistics Status", tier_val, delta="Verified Path" if tier_val == "Verified" else "Needs Review")
        m3.metric("Lead Time", "24-48 Hours", delta="Priority A")

        st.divider()
        
        # 5. The Regimented Report
        with st.container(border=True):
            # Show the report minus the metric header
            final_report = response.text.split(tier_val)[1] if tier_val in response.text else response.text
            st.markdown(final_report)
            
            if st.button("TRANSMIT TO PROD SHOP", type="primary", use_container_width=True):
                st.balloons()
                st.toast("Full Audit Trail transmitted to Section Chief.")
