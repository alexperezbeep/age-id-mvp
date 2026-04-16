import streamlit as st
import google.generativeai as genai
from PIL import Image

# 1. UI Setup
st.set_page_config(page_title="AF AGE Identifier", page_icon="🛠️")
st.title("🛠️ AGE Context-Lock Identifier")
st.caption("Standardized Visual-First Profiling | 92nd MXS")

# 2. Context Selection
st.subheader("Step 1: Context Selection")
col1, col2 = st.columns(2)
with col1:
    selected_class = st.selectbox("Category:", ["Heater", "Compressor", "Generator", "Towbar"])
with col2:
    selected_profile = st.radio("Profile:", ["Modern (Yellow)", "Legacy (Grey)", "Small/Portable"])

# 3. Image Upload
st.subheader("Step 2: Upload Photo")
uploaded_file = st.file_uploader("Scan unit...", type=["jpg", "jpeg", "png"])

if uploaded_file:
    img = Image.open(uploaded_file)
    st.image(img, use_container_width=True)

    if st.button("🚀 EXECUTE LOGISTICS LOCK"):
        api_key = st.secrets["GEMINI_API_KEY"]
        genai.configure(api_key=api_key)
        
        # We use a direct model call without extra tools to bypass the 404/v1beta issue
        model = genai.GenerativeModel('gemini-1.5-flash')
        
        prompt = f"""
        ACT AS A USAF LOGISTICS EXPERT. 
        Identify this {selected_class} with a {selected_profile} profile.
        
        If 'Legacy' is selected, you MUST prioritize the Davey H-1 (NSN 4520-01-056-4269).
        If 'Modern' is selected, prioritize the NGH-1 or MH-1 models.
        
        Provide the Top 3 NSN matches and the relevant T.O. number.
        """
        
        try:
            response = model.generate_content([prompt, img])
            st.success("Logistics Identified")
            st.markdown(response.text)
        except Exception as e:
            st.error(f"Final Attempt Error: {e}")
