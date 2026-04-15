import streamlit as st
from google import genai
from google.genai import types
from PIL import Image
import io

# 1. Page Config
st.set_page_config(page_title="AF AGE Identifier", page_icon="🛠️", layout="centered")

# Custom CSS for "Military-Spec" look
st.markdown("""
    <style>
    .main { background-color: #0e1117; color: #ffffff; }
    .stButton>button { background-color: #1f4068; color: white; border-radius: 5px; width: 100%; }
    .critical { color: #e94560; font-weight: bold; }
    </style>
    """, unsafe_allow_html=True)

st.title("🛠️ AGE Context-Lock Identifier")
st.caption("Reducing mental burden for the 92nd MXS | Project H4D")

# 2. Stage 1: Context Locking (The JetDash Fix)
st.subheader("Step 1: Set Equipment Context")
context_input = st.selectbox(
    "Identify Primary Unit:",
    ["[Auto-Detect from Silhouette]", "A/M32A-95 (Turbine Compressor)", "MC-7 (Diesel Compressor)", "MC-20", "New-60A Generator"],
    help="Locking the unit prevents 2-hour latency in part identification."
)

# 3. Stage 2: Capture
st.subheader("Step 2: Identify Discrepant Part")
uploaded_file = st.file_uploader("Upload or take a photo of the part...", type=["jpg", "jpeg", "png"])

if uploaded_file:
    img = Image.open(uploaded_file)
    st.image(img, caption="Flight Line Scan", use_column_width=True)

    if st.button("🚀 IDENTIFY & SEARCH NSN"):
        # Retrieve API Key from Secrets
        api_key = st.secrets.get("GEMINI_API_KEY")
        if not api_key:
            st.error("Missing API Key. Please configure in Streamlit Secrets.")
        else:
            client = genai.Client(api_key=api_key)
            
            # THE CORE LOGIC: Image + Grounding
            with st.spinner("Scraping Technical Orders & FedLog..."):
                prompt = f"""
                You are an AF logistics assistant. 
                Context: The maintainer is looking at {context_input}.
                Task: 
                1. Identify the part in the image.
                2. Search for the Top 3 NSN matches.
                3. For each, provide: NSN Number, Nomenclature, and a 'Visual Differentiator'.
                4. Highlight if it is a 'Critical Component'.
                5. Provide the Technical Order (T.O.) reference.
                """
                
                # Using Gemini 3 Flash with Google Search Grounding
                response = client.models.generate_content(
                    model="gemini-3-flash-preview",
                    contents=[prompt, img],
                    config=types.GenerateContentConfig(
                        tools=[types.Tool(google_search=types.GoogleSearch())]
                    )
                )

                st.success("Analysis Complete")
                st.markdown(response.text)
                
                # Action Buttons for Demo
                col1, col2 = st.columns(2)
                with col1:
                    st.button("📦 Request Part for 92nd MXS")
                with col2:
                    st.button("📖 Open T.O. Manual")