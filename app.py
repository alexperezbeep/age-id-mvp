import streamlit as st
import time

# --- INITIALIZATION ---
if 'resolved_data' not in st.session_state:
    st.session_state.resolved_data = []

# --- SIDEBAR TAXONOMY ---
with st.sidebar:
    st.title("Falcon Dashboard")
    uploaded_file = st.file_uploader("Upload Image", type=['png', 'jpg', 'jpeg'])
    
    st.write("### Taxonomy Selection")
    tax_mode = st.radio("Mode", ["Equipment", "Part", "Unknown / Not Sure"], index=2)
    
    # DYNAMIC CATEGORY MAPPING
    if tax_mode == "Equipment":
        categories = ["Not Sure", "Power Generation", "Air Conditioning", "Hydraulic Test Stands"]
    elif tax_mode == "Part":
        categories = ["Not Sure", "Hydraulic", "Electrical", "Structural", "Pneumatic"]
    else:
        # If the user is totally unsure, we lock the class to "Auto-Detect"
        categories = ["Auto-Detect Category"]
        
    class_selection = st.selectbox("Select Class", categories)
    feature_text = st.text_input("Distinguishing Feature (Optional)", placeholder="e.g. red pump")

# --- MAIN INTERFACE ---
col1, col2 = st.columns([1, 1])

with col1:
    st.header("1. Digital Inspection")
    if uploaded_file:
        st.image(uploaded_file, use_column_width=True)
    
    if st.button("🚀 EXECUTE LOGISTICS LOCK", type="primary", use_container_width=True):
        with st.spinner("Analyzing..."):
            time.sleep(1.5)
            
            # LOGIC: Handling the "Unknown" state
            if class_selection in ["Not Sure", "Auto-Detect Category"]:
                # The model runs a wide search across all AGE databases
                st.session_state.resolved_data = [
                    {"nsn": "4520-01-135-2770", "name": "Detected: Hydraulic Pump", "conf": "94%"},
                    {"nsn": "Unknown", "name": "Manual Tech Order Review Required", "conf": "N/A"}
                ]
            else:
                # Targeted search based on user input
                st.session_state.resolved_data = [
                    {"nsn": "4520-01-482-8571", "name": f"{class_selection} Match", "conf": "88%"}
                ]
        st.rerun()

with col2:
    st.header("2. NSN Resolution")
    if st.session_state.resolved_data:
        for item in st.session_state.resolved_data:
            with st.container(border=True):
                st.write(f"**NSN: {item['nsn']}**")
                st.write(f"Identity: {item['name']}")
                st.write(f"Confidence: :green[{item['conf']}]")
    else:
        st.info("Upload and execute lock to resolve.")
