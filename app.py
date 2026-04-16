import streamlit as st
import time

# --- 1. INITIALIZATION ---
if 'resolved_data' not in st.session_state:
    st.session_state.resolved_data = []
if 'cart' not in st.session_state:
    st.session_state.cart = []

st.set_page_config(page_title="Falcon Dashboard", layout="wide")

# --- 2. SIDEBAR: TAXONOMY & INPUTS ---
with st.sidebar:
    st.title("Falcon Dashboard")
    
    # Image Upload
    uploaded_file = st.file_uploader("Upload Image", type=['png', 'jpg', 'jpeg'])
    
    st.divider()
    
    # Taxonomy Selection
    st.write("### Taxonomy Selection")
    tax_mode = st.radio("Mode", ["Equipment", "Part"], index=1, label_visibility="collapsed")
    
    # Dynamic Category Mapping
    if tax_mode == "Equipment":
        st.write("### Select Equipment Class")
        categories = ["Power Generation", "Air Conditioning", "Hydraulic Test Stands", "Towing Gear"]
    else:
        st.write("### Select Part Class")
        categories = ["Hydraulic", "Electrical", "Structural", "Pneumatic", "Avionics"]
        
    class_selection = st.selectbox("Class", categories, label_visibility="collapsed")
    
    # Feature Input
    st.write("### Distinguishing Feature (Optional)")
    feature_text = st.text_input("Feature", placeholder="e.g. pump, connector", label_visibility="collapsed")

    # Supply Cart Display
    st.divider()
    st.write("### 🛒 Supply Cart")
    if not st.session_state.cart:
        st.caption("No items in cart.")
    else:
        for item in st.session_state.cart:
            st.write(f"- {item}")

# --- 3. MAIN INTERFACE: TWO-COLUMN LAYOUT ---
col1, col2 = st.columns([1, 1])

with col1:
    st.header("1. Digital Inspection")
    if uploaded_file:
        st.image(uploaded_file, use_column_width=True)
    else:
        st.info("Awaiting image upload...")
    
    # THE TRIGGER
    if st.button("🚀 EXECUTE LOGISTICS LOCK", type="primary", use_container_width=True):
        with st.spinner(f"Resolving {tax_mode} logistics..."):
            time.sleep(1.5) # Simulated API Latency
            
            # MOCK LOGIC: Changes based on input
            if "pump" in feature_text.lower() or "punpk" in feature_text.lower():
                st.session_state.resolved_data = [
                    {"nsn": "4520-01-135-2770", "name": "Hydraulic (H-1)", "conf": "96%"},
                    {"nsn": "4520-01-482-8571", "name": "Hydraulic (NGH-1)", "conf": "82%"}
                ]
            elif tax_mode == "Equipment":
                st.session_state.resolved_data = [
                    {"nsn": "6115-01-512-1234", "name": "Generator, Diesel", "conf": "91%"}
                ]
            else:
                st.session_state.resolved_data = [
                    {"nsn": "Unknown", "name": "No Exact Match Found", "conf": "0%"}
                ]
        st.rerun()

with col2:
    st.header("2. NSN Resolution")
    
    if not st.session_state.resolved_data:
        st.info(f"Upload {tax_mode} image and execute lock.")
    else:
        # DYNAMIC CARD RENDERING
        for item in st.session_state.resolved_data:
            with st.container(border=True):
                c_left, c_right = st.columns([3, 1])
                with c_left:
                    st.write(f"**NSN: {item['nsn']}**")
                    st.caption(f"{item['name']}\nLogistics Match Confirmed via Visual Anchors.")
                with c_right:
                    st.subheader(f":green[{item['conf']}]")
                
                if st.button(f"Add to Cart", key=item['nsn']):
                    st.session_state.cart.append(f"{item['name']} ({item['nsn']})")
                    st.toast(f"Logged {item['nsn']} for Production Superintendent review.")
