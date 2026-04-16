import streamlit as st
from google import genai
from google.genai import types
from PIL import Image

# 1. Page Config
st.set_page_config(page_title="AF AGE Identifier", page_icon="🛠️", layout="centered")

st.markdown("""
    <style>
    .main { background-color: #0e1117; color: #ffffff; }
    .stButton>button { background-color: #1f4068; color: white; border-radius: 5px; width: 100%; }
    </style>
    """, unsafe_allow_html=True)

st.title("🛠️ AGE Context-Lock Identifier")
st.caption("Universal Visual Taxonomy for the 92nd MXS")

# 2. Step 1: Broad Functional Class
st.subheader("Step 1: Select Equipment Category")
class_options = [
    "[Auto-Detect from Silhouette]", 
    "Heater / Environmental Control",
    "Air Compressor", 
    "Generator / Power Unit",
    "Hydraulic Test Stand",
    "Towbar / Handling",
    "Engine / Component Class"
]
selected_class = st.selectbox("Identify Category:", class_options)

# 3. Step 2: Generalizable Visual Filters
selected_profile = "[Not Sure]"
if selected_class != "[Auto-Detect from Silhouette]":
    st.subheader("Step 2: Describe Physical Profile")
    profiles = {
        "Heater / Environmental Control": ["Modern (Yellow / Enclosed)", "Legacy (Grey / Exposed Frame)", "Small (Portable Square)"],
        "Air Compressor": ["Low-Profile (Enclosed Box)", "Large Utility (Exposed Engine)", "High-Pressure (Dual Tank)"],
        "Generator / Power Unit": ["Standard Box (3-Wheel)", "Flat-Front (Flight Line Style)", "Back-Up (Stationary/Large)"],
        "Hydraulic Test Stand": ["Dual Hose (Vertical Reel)", "Compact (Horizontal)", "Electric (Indoor Style)"],
        "Towbar / Handling": ["Telescoping (Adjustable)", "Solid Bar (Fixed Length)", "Universal (Multi-Head)"],
        "Engine / Component Class": ["Small Diesel (Exposed/Fan)", "Large Industrial (Enclosed)", "Electrical Component"]
    }
    current_options = profiles.get(selected_class, ["[Not Sure]"])
    selected_profile = st.radio("What does it look like?", ["[Not Sure]"] + current_options)

final_context = f"{selected_class} - Profile: {selected_profile}"

# 4. Step 3: Scan & Identify
st.subheader("Step 3: Scan & Identify")
uploaded_file = st.file_uploader("Upload unit photo...", type=["jpg", "jpeg", "png"])

if uploaded_file:
    img = Image.open(uploaded_file)
    st.image(img, caption="Unit Scan", use_column_width=True)

    if st.button("🚀 EXECUTE LOGISTICS LOCK"):
        api_key = st.secrets.get("GEMINI_API_KEY")
        if not api_key:
            st.error("API Key not found.")
        else:
            # Reverting to standard initialization to fix 'tools' field mismatch
            client = genai.Client(api_key=api_key)
            
            with st.spinner("Locking Context & Searching T.O.s..."):
                prompt = f"""
                Maintainer Context: {final_context}
                Task: Identify the unit. If 'Legacy' is selected, prioritize older units like the Davey Compressor H-1 (NSN 4520-01-056-4269).
                
                Output:
                1. Top 3 NSN matches.
                2. Visual Differentiators.
                3. Primary T.O. Number.
                4. Safety Warnings.
                """
                
                try:
                    # Using Google Search tool correctly for the GenAI SDK
                    response = client.models.generate_content(
                        model="gemini-1.5-flash", 
                        contents=[prompt, img],
                        config=types.GenerateContentConfig(
                            tools=[types.Tool(google_search=types.GoogleSearch())]
                        )
                    )
                    st.success("Analysis Complete")
                    st.markdown(response.text)
                except Exception as e:
                    st.error(f"Final SDK Error: {e}")
                    st.info("If this persists, check that your requirements.txt uses 'google-genai' and not 'google-generativeai'.")
