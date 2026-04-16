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

# 2. Stage 1: Functional Class Selection (The JetDash Fix)
st.subheader("Step 1: Select Equipment/Part Class")

# Broad functional categories (Classes)
class_options = [
    "[Auto-Detect from Silhouette]", 
    "Air Compressor", 
    "Generator / Power Unit",
    "Towbar / Handling",
    "Hydraulic Test Stand",
    "Liquid Oxygen (LOX) Cart",
    "Engine / Component Class"
]

selected_class = st.selectbox(
    "Identify Functional Category:", 
    class_options,
    help="Start with the general category to guide the AI identification."
)

# Progressive Refinement (Subtypes/Models)
final_context = selected_class
if selected_class == "Air Compressor":
    selected_model = st.radio(
        "Select Subtype/Model:",
        ["MC-20 (Lowpack)", "MC-7 (Diesel)", "A/M32A-95 (Turbine)"]
    )
    final_context = f"{selected_class}: {selected_model}"
elif selected_class == "Generator / Power Unit":
    selected_model = st.radio(
        "Select Subtype/Model:",
        ["New-60A Generator", "MEP-806B (60kW)", "A/M32A-60 (Dash 60)"]
    )
    final_context = f"{selected_class}: {selected_model}"
elif selected_class == "Engine / Component Class":
    selected_model = st.radio(
        "Select Engine Series:",
        ["Cummins B-Series (6BT)", "Detroit Diesel", "Continental"]
    )
    final_context = f"{selected_class}: {selected_model}"

# 3. Stage 2: Capture
st.subheader("Step 2: Identify Discrepant Part")
uploaded_file = st.file_uploader("Upload or take a photo of the part...", type=["jpg", "jpeg", "png"])

if uploaded_file:
    img = Image.open(uploaded_file)
    st.image(img, caption="Flight Line Scan", use_column_width=True)

    if st.button("🚀 IDENTIFY & SEARCH NSN"):
        api_key = st.secrets.get("GEMINI_API_KEY")
        if not api_key:
            st.error("Missing API Key. Please configure in Streamlit Secrets.")
        else:
            client = genai.Client(api_key=api_key)
            
            with st.spinner("Scraping Technical Orders & FedLog..."):
                # Updated prompt to handle broad classes vs specific models
                prompt = f"""
                You are an AF logistics assistant. 
                Context: The maintainer is working within the functional class of {final_context}.
                
                Task: 
                1. Identify the specific part or model in the image based on the provided class.
                2. If the user selected a general class, determine the exact model (e.g., if class is Air Compressor, identify if it is an MC-20).
                3. Search for the Top 3 NSN matches (Prioritize the main Unit NSN if a whole machine is shown, or component NSNs if a part is shown).
                4. For each, provide: NSN Number, Nomenclature, and a 'Visual Differentiator'.
                5. Highlight if it is a 'Critical Component'.
                6. Provide the Technical Order (T.O.) reference.
                """
                
                response = client.models.generate_content(
                    model="gemini-3-flash-preview",
                    contents=[prompt, img],
                    config=types.GenerateContentConfig(
                        tools=[types.Tool(google_search=types.GoogleSearch())]
                    )
                )

                st.success("Analysis Complete")
                st.markdown(response.text)
                
                col1, col2 = st.columns(2)
                with col1:
                    st.button("📦 Request Part for 92nd MXS")
                with col2:
                    # Smart Search for TO instead of static button
                    st.link_button("📖 Open T.O. Manual", f"https://www.google.com/search?q=USAF+Technical+Order+Manual")
