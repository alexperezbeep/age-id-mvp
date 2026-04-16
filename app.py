import streamlit as st
from google import genai
from google.genai import types
from PIL import Image

# 1. Page Configuration & Falcon Branding
st.set_page_config(page_title="Falcon H4D MVP", page_icon="🦅", layout="wide")

# Custom CSS to mimic the Slide's dark/modern UI
st.markdown("""
    <style>
    .main { background-color: #0e1117; }
    div[data-testid="stMetricValue"] { font-size: 24px; color: #00d4ff; }
    </style>
    """, unsafe_allow_html=True)

# 2. Sidebar: The "Dashboard" Inputs
with st.sidebar:
    st.image("https://upload.wikimedia.org/wikipedia/commons/thumb/d/d3/Seal_of_the_United_States_Department_of_the_Air_Force.svg/1200px-Seal_of_the_United_States_Department_of_the_Air_Force.svg.png", width=100)
    st.title("Falcon Dashboard")
    st.info("Mission Status: 🦅 Priority Active")
    
    st.divider()
    
    st.subheader("Step 1: Technical Domain")
    domains = [
        "Ground Support Equipment (Full Unit)",
        "Engine / Powerplant Component", 
        "Electrical / Avionics Component",
        "Hydraulic / Pneumatic Component",
        "Hardware / Structural / Universal"
    ]
    selected_domain = st.selectbox("Select Domain:", domains)

    st.subheader("Step 2: Describe Physical Profile")
    profiles = {
        "Ground Support Equipment (Full Unit)": ["Mobile/Trailer", "Stationary/Large", "Hand-Held"],
        "Engine / Powerplant Component": ["Internal/Closed", "External/Exposed", "Fuel/Oil System"],
        "Electrical / Avionics Component": ["Sealed/Relay Style", "Wiring/Harness", "Control Panel"],
        "Hydraulic / Pneumatic Component": ["Pump/Motor", "Valve/Manifold", "Hose/Fitting"],
        "Hardware / Structural / Universal": ["Fastener/Bracket", "Housing/Casing", "Unknown/Other"]
    }
    current_options = profiles.get(selected_domain, ["Standard Configuration"])
    selected_profile = st.radio("Visual Profile:", current_options)

    st.subheader("Step 3: Descriptive Cues")
    user_cues = st.text_input("Refinement (e.g. Casting #23505677)", placeholder="Enter visible part numbers...")

# 3. Main Interface: The Scanner
col_left, col_right = st.columns([1, 1.2])

with col_left:
    st.header("1. Access Scanner")
    uploaded_file = st.file_uploader("Drop photo here for visual recognition", type=["jpg", "jpeg", "png"])
    
    if uploaded_file:
        img = Image.open(uploaded_file)
        st.image(img, caption="Live Scanner Feed", use_container_width=True)
        execute = st.button("🚀 EXECUTE LOGISTICS LOCK", use_container_width=True)

# 4. Results: The Part Details & Supply Cart
with col_right:
    st.header("2. Part Details & Logistics")
    
    if uploaded_file and execute:
        api_key = st.secrets["GEMINI_API_KEY"]
        client = genai.Client(api_key=api_key)
        
        with st.status("Analyzing Visual Taxonomy...", expanded=True) as status:
            prompt = f"""
            ACT AS A USAF MAINTENANCE SUPERINTENDENT.
            DOMAIN: {selected_domain} | PROFILE: {selected_profile}
            USER CUES: {user_cues}
            
            TASK:
            1. Identify TOP 3 NSN matches. Prioritize matches for '{user_cues}'.
            2. Provide the Primary Technical Order (T.O.).
            3. SAFETY: List 2 pitfalls.
            4. HIERARCHY: Remind that Section Chief is below Production Superintendent.
            """
            
            response = client.models.generate_content(
                model="gemini-3-flash-preview",
                contents=[prompt, img],
                config=types.GenerateContentConfig(tools=[types.Tool(google_search=types.GoogleSearch())])
            )
            status.update(label="Analysis Complete", state="complete")

        # Visual Dashboard Metrics (Matching Slide Step 3)
        m1, m2, m3 = st.columns(3)
        m1.metric("Match Confidence", "98.4%", delta="High")
        m2.metric("Stock Status", "In Stock", delta_color="normal")
        m3.metric("Lead Time", "24 Hours")

        # Logistics Actions (Matching Slide Step 4)
        with st.container(border=True):
            st.write("### 📦 Supply Cart Action")
            st.markdown(response.text)
            
            if st.button("TRANSMIT TO PROD SHOP", type="primary", use_container_width=True):
                st.balloons()
                st.toast("Data sent to Production Superintendent via Falcon-Net.")

    else:
        st.info("Awaiting scanner input. Upload a photo to begin logistics identification.")
