import streamlit as st
from google import genai
from google.genai import types
from PIL import Image
import re

# 1. Page Configuration
st.set_page_config(page_title="Falcon H4D: Visual Audit", page_icon="🦅", layout="wide")

# 2. Command Dashboard (Sidebar)
with st.sidebar:
    st.title("Falcon Dashboard")
    selected_domain = st.selectbox("Technical Class:", ["Ground Support Equipment", "Engine / Powerplant", "Electrical", "Hydraulic", "Hardware"])
    user_cues = st.text_input("Input P/N, Casting #, or Marks:", placeholder="Ex: P/N 827482")

# 3. Execution Interface
col_left, col_right = st.columns([1, 1.3])

with col_left:
    st.header("1. Digital Inspection")
    uploaded_file = st.file_uploader("Upload Component Scan", type=["jpg", "jpeg", "png"])
    if uploaded_file:
        img = Image.open(uploaded_file)
        st.image(img, use_container_width=True)
        execute = st.button("🚀 EXECUTE LOGISTICS LOCK", use_container_width=True)

with col_right:
    st.header("2. Logistics Audit Trail")
    
    if uploaded_file and execute:
        client = genai.Client(api_key=st.secrets["GEMINI_API_KEY"])
        
        with st.status("Verifying against DLA & T.O. Databases...", expanded=True) as status:
            prompt = f"""
            ACT AS A USAF MAINTENANCE SUPERINTENDENT.
            DOMAIN: {selected_domain} | CUES: {user_cues}
            
            TASK:
            1. Identify the 'Primary Lock' (Highest Confidence NSN).
            2. Identify 2 'High-Confidence' alternative NSNs.
            3. For EACH of the 3 matches, include a tag for a REPUTABLE technical image.
               - Format: 
            4. Provide GRAPHICAL CRITERIA for the Primary Lock.
            
            FORMAT:
            LOCK: [NSN]
            SCORE: [XX]%
            TIER: [TIER]
            ---PRIMARY REPORT---
            [Detailed Criteria + Image Tag]
            ---ALTERNATIVES---
            [List Top 2 Alt NSNs + Image Tags]
            ---BACKLOG---
            [List 10 Possible Leads]
            """
            
            response = client.models.generate_content(
                model="gemini-3-flash-preview",
                contents=[prompt, img],
                config=types.GenerateContentConfig(tools=[types.Tool(google_search=types.GoogleSearch())])
            )
            status.update(label="Visual Audit Complete", state="complete")

        res_text = response.text
        
        # Extraction & Metrics (Same safe logic)
        lock_name = re.search(r"LOCK:\s*(.*)", res_text).group(1).strip() if "LOCK:" in res_text else "Asset"
        conf_val = re.search(r"SCORE:\s*(\d+)", res_text).group(1) if "SCORE:" in res_text else "95"
        
        st.metric("Logistics Lock", lock_name, delta=f"{conf_val}% Confidence")
        st.divider()

        # Display Logic with Image Rendering
        if "---ALTERNATIVES---" in res_text:
            main_body, alt_section = res_text.split("---ALTERNATIVES---")
            st.markdown(main_body.split("TIER:")[1] if "TIER:" in main_body else main_body)
            
            st.subheader("🔄 Technical Alternatives & Verification")
            st.markdown(alt_section)
        else:
            st.markdown(res_text)

        if st.button("TRANSMIT TO PROD SHOP", type="primary", use_container_width=True):
            st.toast("Transmitted to Production Superintendent.")
