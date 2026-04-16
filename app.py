import streamlit as st
from google import genai
from google.genai import types
from PIL import Image

# 1. Branding & UI
st.set_page_config(page_title="AF AGE Context-Lock", page_icon="🛠️")
st.title("🛠️ AGE Context-Lock Identifier")
st.caption("Universal Visual Taxonomy & Workflow Logic | 92nd MXS")

# 2. Universal Domain Selection
st.subheader("Step 1: Technical Domain")
domains = [
    "Ground Support Equipment (Full Unit)",
    "Engine / Powerplant Component", 
    "Electrical / Avionics Component",
    "Hydraulic / Pneumatic Component",
    "Hardware / Structural / Universal"
]
selected_domain = st.selectbox("Select Domain:", domains)

# 3. Descriptive Refinement (The "Search Aid")
st.subheader("Step 2: Add Visual Cues")
user_cues = st.text_input("Add specific details (e.g. 'Casting #23505677', '6-bolt flange', 'Bronze gear'):")

# 4. Profile Selection
profiles = {
    "Ground Support Equipment (Full Unit)": ["Mobile/Trailer", "Stationary/Large", "Hand-Held"],
    "Engine / Powerplant Component": ["Internal/Closed", "External/Exposed", "Fuel/Oil System"],
    "Electrical / Avionics Component": ["Sealed/Relay Style", "Wiring/Harness", "Control Panel"],
    "Hydraulic / Pneumatic Component": ["Pump/Motor", "Valve/Manifold", "Hose/Fitting"],
    "Hardware / Structural / Universal": ["Fastener/Bracket", "Housing/Casing", "Unknown/Other"]
}
current_options = profiles.get(selected_domain, ["Standard Configuration"])
selected_profile = st.radio("Visual Profile:", current_options)

# 5. Execution Logic
st.subheader("Step 3: Scan & Execute")
uploaded_file = st.file_uploader("Upload component photo...", type=["jpg", "jpeg", "png"])

if uploaded_file:
    img = Image.open(uploaded_file)
    st.image(img, use_container_width=True)

    if st.button("🚀 EXECUTE LOGISTICS LOCK"):
        api_key = st.secrets["GEMINI_API_KEY"]
        client = genai.Client(api_key=api_key)
        
        prompt = f"""
        ACT AS A USAF MAINTENANCE SUPERINTENDENT.
        DOMAIN: {selected_domain}
        PROFILE: {selected_profile}
        USER-OBSERVED CUES: {user_cues}
        
        TASK:
        1. Identify the TOP 3 most likely NSN matches. 
           - If a Part Number or Casting Number is provided in 'User Cues', prioritize it for the lookup.
           - Explain the difference between any generic results and specific matches found.
        2. Provide the Primary Technical Order (T.O.) number.
        3. SAFETY: Identify 2-3 specific maintenance pitfalls for this profile.
        4. COMMAND LOGIC: Remind the user that for part validation, the Section Chief 
           is the primary contact below the Production Superintendent.
        """
        
        try:
            response = client.models.generate_content(
                model="gemini-3-flash-preview",
                contents=[prompt, img],
                config=types.GenerateContentConfig(
                    tools=[types.Tool(google_search=types.GoogleSearch())]
                )
            )
            st.success("Analysis Complete")
            st.markdown(response.text)
        except Exception as e:
            st.error(f"Logic Error: {e}")
