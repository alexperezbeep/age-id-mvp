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
        
        # 2026 UPDATE: Switching to Gemini 3 Flash
        # This resolves the 404 error by using an active model
        model = genai.GenerativeModel('gemini-3-flash-preview', 
                                    tools=[{'google_search_retrieval': {}}])
        
        prompt = f"""
        ACT AS A USAF LOGISTICS EXPERT. 
        Identify this {selected_class} with a {selected_profile} profile.
        
        If 'Legacy' is selected, you MUST prioritize the Davey H-1 (NSN 4520-01-056-4269).
        If 'Modern' is selected, prioritize the NGH-1 or MH-1 models.
        
        Provide:
        1. Confirmed NSN and Nomenclature.
        2. Visual Differentiators (why it matches the photo).
        3. Relevant Technical Order (T.O.) number.
        """
        
        try:
            response = model.generate_content([prompt, img])
            st.success("Logistics Identified")
            st.markdown(response.text)
        except Exception as e:
            # Fallback in case 'preview' tags change during the demo
            st.error(f"Execution Error: {e}")
            st.info("Try changing the model string to 'gemini-3-flash' if preview is restricted.")
