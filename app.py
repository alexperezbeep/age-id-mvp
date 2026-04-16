import streamlit as st
from google import genai
from google.genai import types
from PIL import Image

# 1. UI Branding
st.set_page_config(page_title="AF AGE Context-Lock", page_icon="🛠️", layout="centered")
st.title("🛠️ AGE Context-Lock Identifier")
st.caption("Standardized Visual Taxonomy & Workflow Logic | 92nd MXS")

# 2. Step 1: Expanded Technical Categories
st.subheader("Step 1: Select Equipment Category")
class_options = [
    "Heater / Environmental Control",
    "Air Compressor", 
    "Generator / Power Unit",
    "Hydraulic Test Stand",
    "Towbar / Handling",
    "Engine / Component Class"
]
selected_class = st.selectbox("Technical Class:", class_options)

# 3. Step 2: Context-Lock Profiles
st.subheader("Step 2: Describe Physical Profile")
profiles = {
    "Heater / Environmental Control": ["Modern (Yellow / Enclosed)", "Legacy (Grey / Exposed Frame)", "Small (Portable Square)"],
    "Air Compressor": ["Low-Profile (Enclosed Box)", "Large Utility (Exposed Engine)", "High-Pressure (Dual Tank)"],
    "Generator / Power Unit": ["Standard Box (3-Wheel)", "Flat-Front (Flight Line Style)", "Back-Up (Stationary/Large)"],
    "Hydraulic Test Stand": ["Dual Hose (Vertical Reel)", "Compact (Horizontal)", "Electric (Indoor Style)"],
    "Towbar / Handling": ["Telescoping (Adjustable)", "Solid Bar (Fixed Length)", "Universal (Multi-Head)"],
    "Engine / Component Class": ["Small Diesel (Exposed/Fan)", "Large Industrial (Enclosed)", "Electrical Component"]
}

current_options = profiles.get(selected_class, ["Standard Configuration"])
selected_profile = st.radio("Visual Profile:", current_options)

# 4. Step 3: Scan & Workflow Execution
st.subheader("Step 3: Scan & Execute")
uploaded_file = st.file_uploader("Upload unit photo...", type=["jpg", "jpeg", "png"])

if uploaded_file:
    img = Image.open(uploaded_file)
    st.image(img, use_container_width=True)

    if st.button("🚀 EXECUTE LOGISTICS LOCK"):
        api_key = st.secrets["GEMINI_API_KEY"]
        client = genai.Client(api_key=api_key)
        
        # This prompt now includes the organizational logic you corrected
        prompt = f"""
        ACT AS A USAF MAINTENANCE SUPERINTENDENT.
        Target Equipment: {selected_class} - {selected_profile}
        
        Task:
        1. Identify the NSN (Prioritize 4520-01-056-4269 for Legacy Heaters).
        2. Provide the Primary Technical Order (T.O.) for this unit.
        3. SAFETY: Identify 2-3 high-risk maintenance pitfalls for this specific profile.
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
