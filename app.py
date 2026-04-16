import streamlit as st
import time

# --- Page Config ---
st.set_page_config(page_title="Falcon Dashboard", layout="wide")

# --- Custom CSS for the "Warzone" Dark Theme ---
st.markdown("""
    <style>
    .main { background-color: #0e1117; color: white; }
    .stButton>button { width: 100%; border-radius: 5px; }
    .nsn-card {
        border: 1px solid #262730;
        padding: 15px;
        border-radius: 10px;
        background-color: #161b22;
        margin-bottom: 10px;
    }
    .conf-green { color: #2ea043; font-weight: bold; font-size: 1.2rem; }
    </style>
    """, unsafe_allow_html=True)

# --- Session State Initialization ---
if 'nsn_results' not in st.session_state:
    st.session_state.nsn_results = []
if 'cart' not in st.session_state:
    st.session_state.cart = []

# --- Sidebar Taxonomy & Inputs ---
with st.sidebar:
    st.title("Falcon Dashboard")
    
    uploaded_file = st.file_uploader("Upload Image", type=['jpg', 'jpeg', 'png'])
    
    st.write("### Taxonomy Selection")
    mode = st.radio("Type", ["Equipment", "Part"], index=1, label_visibility="collapsed")
    
    st.write("### Select Part Class")
    part_class = st.selectbox("Class", ["Hydraulic", "Electrical", "Structural", "Avionics"], label_visibility="collapsed")
    
    st.write("### Distinguishing Feature (Optional)")
    feature = st.text_input("Feature", value="hydraylic punpk", label_visibility="collapsed")

    st.divider()
    st.write("### 🛒 Supply Cart")
    if not st.session_state.cart:
        st.caption("No items added.")
    else:
        for item in st.session_state.cart:
            st.write(f"- {item}")

# --- Main Logic ---
col1, col2 = st.columns([1, 1])

with col1:
    st.header("1. Digital Inspection")
    
    # Display Uploaded Image or Placeholder
    if uploaded_file:
        st.image(uploaded_file, use_column_width=True)
    else:
        st.info("Please upload an image to begin inspection.")

    # Execute Button
    if st.button("🚀 EXECUTE LOGISTICS LOCK", type="primary"):
        with st.spinner("Analyzing Logistics Data..."):
            # Simulation of API/Model Logic
            time.sleep(1.5) 
            
            # Logic: If 'pump' is detected (even with your typo), return these NSNs
            if "pump" in feature.lower() or "punpk" in feature.lower():
                st.session_state.nsn_results = [
                    {"nsn": "4520-01-135-2770", "name": "Hydraulic (H-1)", "conf": "96%"},
                    {"nsn": "4520-01-482-8571", "name": "Hydraulic (NGH-1)", "conf": "82%"},
                    {"nsn": "4520-00-540-1444", "name": "Hydraulic (BT400)", "conf": "62%"}
                ]
            else:
                st.session_state.nsn_results = [
                    {"nsn": "0000-00-000-0000", "name": "Unknown Component", "conf": "0%"}
                ]
        st.rerun()

with col2:
    st.header("2. NSN Resolution")
    
    if st.session_state.nsn_results:
        for res in st.session_state.nsn_results:
            # Render individual cards dynamically
            with st.container():
                st.markdown(f"""
                <div class="nsn-card">
                    <div style="display: flex; justify-content: space-between;">
                        <div>
                            <span style="color: #8b949e;">NSN:</span> <strong>{res['nsn']}</strong><br>
                            <span style="font-size: 0.9rem;">{res['name']}</span><br>
                            <span style="font-size: 0.8rem; color: #8b949e;">Logistics Match Confirmed via Visual Anchors.</span>
                        </div>
                        <div class="conf-green">{res['conf']}</div>
                    </div>
                </div>
                """, unsafe_allow_html=True)
                
                if st.button(f"Add to Supply Cart", key=res['nsn']):
                    st.session_state.cart.append(f"{res['name']} ({res['nsn']})")
                    st.toast(f"Added {res['nsn']} to cart!")
    else:
        st.info("Awaiting logistics execution...")
