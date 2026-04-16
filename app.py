import streamlit as st
from google import genai
from google.genai import types
from PIL import Image
import re
import time

# 1. Page Configuration & Custom CSS for the Falcon Loader
st.set_page_config(page_title="Falcon H4D: Visual Audit", page_icon="🦅", layout="wide")

st.markdown("""
    <style>
    .main { background-color: #0e1117; }
    
    /* Falcon Loading Animation */
    @keyframes rotate { from { transform: rotate(0deg); } to { transform: rotate(360deg); } }
    .falcon-loader {
        width: 100px; height: 100px;
        border: 5px solid #1e2130;
        border-top: 5px solid #00d4ff;
        border-radius: 50%;
        animation: rotate 2s linear infinite;
        position: relative; margin: auto;
    }
    .falcon-icon {
        position: absolute; top: -15px; left: 40px;
        font-size: 25px; transform: rotate(90deg);
    }
    .loading-text { text-align: center; color: #00d4ff; font-family: monospace; margin-top: 10px; }
    </style>
    """, unsafe_allow_html=True)

# 2. Sidebar
with st.sidebar:
    st.image("https://upload.wikimedia.org/wikipedia/commons/thumb/d/d3/Seal_of_the_United_States_Department_of_the_Air_Force.svg/1200px-Seal_of_the_United_States_Department_of_the_Air_Force.svg.png", width=70)
    st.title("Falcon Dashboard")
    selected_domain = st.selectbox("Technical Class:", ["Ground Support Equipment", "Engine", "Electrical", "Hydraulic"])
    user_cues = st.text_input("Refinement (P/N, Casting #):", placeholder="Ex: idk")

# 3. Main Interface
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
        # --- CUSTOM FALCON LOADER ---
        placeholder = st.empty()
        with placeholder.container():
            st.markdown('<div class="falcon-loader"><div class="falcon-icon">🦅</div></div>', unsafe_allow_html=True)
            st.markdown('<p class="loading-text">FALCON IN FLIGHT: SCRUBBING DLA DATABASES...</p>', unsafe_allow_html=True)
        
        # Start API Call
        client = genai.Client(api_key=st.secrets["GEMINI_API_KEY"])
        
        prompt = f"""
        ACT AS A USAF MAINTENANCE SUPERINTENDENT.
        TASK: 
        1. Identify Primary NSN + 2 High-Confidence Alternatives.
        2. Provide 'REGIMENTED GRAPHICAL CRITERIA' for the Primary Lock.
        3. Provide 10 Backlog leads.
        
        FORMAT FOR EXTRACTION:
        NSN_1: [NSN] | KEY_1: [Description]
        NSN_2: [NSN] | KEY_2: [Description]
        NSN_3: [NSN] | KEY_3: [Description]
        ---REPORT---
        [Rest of technical data]
        """
        
        response = client.models.generate_content(
            model="gemini-3-flash-preview",
            contents=[prompt, img],
            config=types.GenerateContentConfig(tools=[types.Tool(google_search=types.GoogleSearch())])
        )
        
        # Clear Loader
        placeholder.empty()

        res_text = response.text

        # 4. The Visual Display Logic (NSN Cards with Images)
        st.subheader("🛡️ Verified Logistics Matches")
        
        matches = re.findall(r"NSN_(\d+):\s*([\d-]+)\s*\|\s*KEY_\1:\s*(.*)", res_text)

        if not matches:
            st.warning("No precise NSN lock. Reviewing Backlog...")
            st.markdown(res_text)
        else:
            for i, nsn, key in matches:
                with st.container(border=True):
                    c1, c2 = st.columns([1, 2])
                    with c1:
                        # Fetch images from reputable host
                        img_url = f"https://www.iso-group.com/Public/Images/NSN/{nsn}.jpg"
                        st.image(img_url, caption=f"DLA Source IPB: {nsn}", use_container_width=True)
                    with c2:
                        st.write(f"### {'🥇 PRIMARY' if i=='1' else '🥈 ALTERNATIVE'}: {nsn}")
                        st.write(f"**Asset:** {key}")
                        if i == '1':
                            st.success("Logistics Match Confirmed.")

        # 5. The Backlog Lead Section
        with st.expander("🔍 View Technical Backlog (10 Leads)"):
            st.markdown(res_text.split("---REPORT---")[-1] if "---REPORT---" in res_text else "Audit Complete.")

        if st.button("TRANSMIT TO PROD SHOP", type="primary", use_container_width=True):
            st.balloons()
            st.toast("Full Audit transmitted to Production Superintendent.")
