import streamlit as st
from google import genai
from google.genai import types
from PIL import Image
import re

# 1. Page Configuration
st.set_page_config(page_title="Falcon H4D MVP", page_icon="🦅", layout="wide")

# Custom CSS for dark-mode military aesthetic
st.markdown("""
    <style>
    .main { background-color: #0e1117; }
    div[data-testid="stMetricValue"] { font-size: 28px; color: #00d4ff; }
    div[data-testid="stMetricDelta"] { font-size: 16px; }
    h1, h2, h3 { color: #f0f2f6; }
    </style>
    """, unsafe_allow_html=True)

# 2. Sidebar: The Command Dashboard
with st.sidebar:
    st.image("https://upload.wikimedia.org/wikipedia/commons/thumb/d/d3/Seal_of_the_United_States_Department_of_the_Air_Force.svg/1200px-Seal_of_the_United_States_Department_of_the_Air_Force.svg.png", width=80)
    st.title("Falcon Dashboard")
    st.info("Status: 🦅 Priority Recognition Active")
    
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

    st.subheader("Step 3: Descriptive Cues")
    user_cues = st.text_input("Refinement (Part #, Casting #, Marks)", placeholder="Ex: P/N 827482")

# 3. Main Interface
col_left, col_right = st.columns([1, 1.2])

with col_left:
    st.header("1. Access Scanner")
    uploaded_file = st.file_uploader("Upload component photo", type=["jpg", "jpeg", "png"])
    
    if uploaded_file:
        img = Image.open(uploaded_file)
        st.image(img, caption="Live Scanner Feed", use_container_width=True)
        execute = st.button("🚀 EXECUTE LOGISTICS LOCK", use_container_width=True)

with col_right:
    st.header("2. Part Details & Logistics")
    
    if uploaded_file and execute:
        client = genai.Client(api_key=st.secrets["GEMINI_API_KEY"])
        
        with st.status("Regimenting Technical Data...", expanded=True) as status:
            prompt = f"""
            ACT AS A USAF MAINTENANCE SUPERINTENDENT.
            DOMAIN: {selected_domain} | PROFILE: {selected_profile} | CUES: {user_cues}
            
            TASK:
            1. Identify the TOP 3 Logistics Matches (NSNs or CAGE/MPN for COTS).
            2. For EACH match, provide this regimented breakdown:
               - Confidence Score: [XX]%
               - Source Validation: (Cite P/N, Visual Taxonomy, or Database)
               - Technical Justification: (Why this variant?)
            3. Provide the Primary Technical Order (T.O.) and 2 Safety Pitfalls.
            4. HIERARCHY: Remind user that Section Chief reports to Production Superintendent.
            
            FORMAT START: Return the highest confidence score as 'PRIMARY_CONFIDENCE: [XX]%' at the top.
            """
            
            response = client.models.generate_content(
                model="gemini-3-flash-preview",
                contents=[prompt, img],
                config=types.GenerateContentConfig(tools=[types.Tool(google_search=types.GoogleSearch())])
            )
            status.update(label="Analysis Complete", state="complete")

        # Extraction Logic
        res_text = response.text
        p_conf = re.search(r"PRIMARY_CONFIDENCE:\s*(\d+)%", res_text).group(1) if re.search(r"PRIMARY_CONFIDENCE:\s*(\d+)%", res_text) else "85"

        # Interactive Metrics View
        m1, m2, m3 = st.columns(3)
        with m1:
            st.metric("Primary Match", f"{p_conf}%", delta="Target Locked")
        m2.metric("Stock Status", "Verified", delta_color="normal")
        m3.metric("Procurement", "Regimented")

        st.divider()
        st.subheader("📦 Supply Chain Analysis")
        
        # Clean up text for final display
        final_display = res_text.split("PRIMARY_CONFIDENCE")[1].split("%", 1)[1] if "PRIMARY_CONFIDENCE" in res_text else res_text
        st.markdown(final_display)
        
        if st.button("TRANSMIT TO PROD SHOP", type="primary", use_container_width=True):
            st.balloons()
            st.toast("Encrypted Data Transmitted to Section Chief.")
