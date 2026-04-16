import streamlit as st
from google import genai
from google.genai import types
from PIL import Image

# 1. Page Config
st.set_page_config(page_title="AF AGE Identifier", page_icon="🛠️", layout="centered")

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
        
        # 2026 SDK: Initialize the Client
        client = genai.Client(api_key=api_key)
        
        prompt = f"""
        ACT AS A USAF LOGISTICS EXPERT. 
        Identify this {selected_class} with a {selected_profile} profile.
        
        If 'Legacy' is selected, you MUST prioritize the Davey H-1 (NSN 4520-01-056-4269).
        If 'Modern' is selected, prioritize the NGH-1 or MH-1 models.
        
        Provide the Top 3 NSN matches and the relevant T.O. number.
        """
        
        try:
            # 2026 SYNTAX: Using 'google_search' instead of 'google_search_retrieval'
            response = client.models.generate_content(
                model="gemini-3-flash-preview",
                contents=[prompt, img],
                config=types.GenerateContentConfig(
                    tools=[types.Tool(google_search=types.GoogleSearch())]
                )
            )
            st.success("Logistics Identified")
            st.markdown(response.text)
        except Exception as e:
            st.error(f"Logic Error: {e}")
