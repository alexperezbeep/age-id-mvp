import streamlit as st
import google.generativeai as genai
from PIL import Image

# 1. UI Setup
st.set_page_config(page_title="AF AGE Identifier", page_icon="🛠️")
st.title("🛠️ AGE Context-Lock Identifier")
st.caption("Standardized Visual-First Profiling | 92nd MXS")

# 2. Step 1: Broad Category & Visual Profile
st.subheader("Step 1: Context Selection")
col1, col2 = st.columns(2)

with col1:
    selected_class = st.selectbox("Equipment Category:", 
        ["Heater", "Air Compressor", "Generator", "Hydraulic Stand", "Towbar"])

with col2:
    selected_profile = st.radio("Physical Profile:", 
        ["Modern (Yellow/Enclosed)", "Legacy (Grey/Exposed Frame)", "Compact/Portable"])

# 3. Step 2: Image Scan
st.subheader("Step 2: Upload Photo")
uploaded_file = st.file_uploader("Scan unit...", type=["jpg", "jpeg", "png"])

if uploaded_file:
    img = Image.open(uploaded_file)
    st.image(img, use_container_width=True)

    if st.button("🚀 EXECUTE LOGISTICS LOCK"):
        # This uses your existing Streamlit secret
        api_key = st.secrets["GEMINI_API_KEY"]
        genai.configure(api_key=api_key)
        
        # This is the stable tool call for the production API
        model = genai.GenerativeModel('gemini-1.5-flash', 
                                    tools=[{'google_search_retrieval': {}}])
        
        prompt = f"""
        Identify this USAF {selected_class} equipment. 
        Current Visual Profile: {selected_profile}.
        
        If 'Legacy' is selected, prioritize units like the Davey H-1 (NSN 4520-01-056-4269).
        If 'Modern' is selected, prioritize NGH-1/MH-1 models.
        
        Provide:
        1. Top 3 NSN matches.
        2. Visual Differentiators.
        3. Technical Order (T.O.) Number.
        """
        
        try:
            # Stable call for vision + search
            response = model.generate_content([prompt, img])
            st.success("Logistics Identified")
            st.markdown(response.text)
        except Exception as e:
            st.error(f"System Error: {e}")
