import streamlit as st
import time

# --- 1. STATE & FINGERPRINT (STRICT REFRESH) ---
if 'resolved_results' not in st.session_state:
    st.session_state.resolved_results = []
if 'cart' not in st.session_state:
    st.session_state.cart = {}
if 'fingerprint' not in st.session_state:
    st.session_state.fingerprint = None

st.set_page_config(page_title="Falcon Dashboard | Mission Ready", layout="wide")

# --- 2. SIDEBAR: AIR FORCE PROCESS FOCUS ---
with st.sidebar:
    st.title("🦅 Falcon Dashboard")
    st.caption("Integrated Decision Support | H4D Phase 3")
    uploaded_file = st.file_uploader("Upload Component Image", type=['png', 'jpg', 'jpeg'])
    
    st.divider()
    mode = st.radio("Asset Taxonomy", ["Part/Component", "Equipment (AGE)"], index=0)
    
    # Hierarchy-based Class Selection
    class_options = ["Electrical (5930)", "Hydraulic (4730)", "Mechanical (5340)"] if mode == "Part/Component" else ["Power Gen (6115)", "HVAC (4120)"]
    selected_class = st.selectbox("Federal Supply Class (FSC)", class_options)
    feature = st.text_input("Distinguishing Feature / Stamped PN", placeholder="e.g. 2335-127-11")

    # REFRESH TRIGGER
    current_fp = f"{getattr(uploaded_file, 'name', 'none')}-{mode}-{feature}"
    if st.session_state.fingerprint != current_fp:
        st.session_state.resolved_results = []
        st.session_state.fingerprint = current_fp

    # ACTIONABLE SUPPLY CART
    st.divider()
    st.write(f"### 🛒 Supply Request Stage ({len(st.session_state.cart)})")
    for nsn, data in st.session_state.cart.items():
        st.caption(f"**{data['pn']}** | Qty: {data['qty']}")
    
    if st.session_state.cart:
        if st.button("📤 Generate TO Slip / Export to ILS-S", use_container_width=True):
            st.toast("Manifest Staged for Supply Sergeant Review")

# --- 3. MAIN INTERFACE ---
col1, col2 = st.columns([1, 1.2])

with col1:
    st.header("1. Digital Inspection")
    if uploaded_file:
        st.image(uploaded_file, use_column_width=True)
    
    if st.button("📝 STAGE FOR SUPPLY REQUEST", type="primary", use_container_width=True):
        with st.spinner("Querying FedLog & Technical Orders..."):
            time.sleep(1.2)
            f_low = feature.lower()
            
            # CONFIDENCE BANDING LOGIC
            if "2335" in f_low or "switch" in f_low:
                st.session_state.resolved_results = [
                    {
                        "nsn": "5930-01-235-1271", "pn": "2335-127-11", "name": "Switch, Pressure",
                        "conf": 98, "status": "GREEN", "to": "1-1520-237-23", "fedlog": "Verified",
                        "notes": "Standard Bleed Air Switch for UH-60 ECS.", "action": "Ready to Order"
                    },
                    {
                        "nsn": "5930-01-135-0096", "pn": "2335-4", "name": "Switch, Pressure",
                        "conf": 72, "status": "YELLOW", "to": "1-1520-237-4", "fedlog": "Verified",
                        "notes": "Legacy variant. Verify PSI threshold in TO before staging.", "action": "Manual Verification Required"
                    }
                ]
            else:
                st.session_state.resolved_results = [
                    {
                        "nsn": "Unknown", "pn": "UNIDENTIFIED", "name": "Unindexed Component",
                        "conf": 45, "status": "RED", "to": "N/A", "fedlog": "No Match",
                        "notes": "Visual match low. High risk of incorrect part.", "action": "Escalate to Level 7 / Master Maintainer"
                    }
                ]
        st.rerun()

with col2:
    st.header("2. NSN Resolution & Risk Assessment")
    if not st.session_state.resolved_results:
        st.info("Awaiting input. Select FSC and Stage for Request.")
    else:
        for item in st.session_state.resolved_results:
            # Color coding by confidence banding
            border_color = {"GREEN": "#28a745", "YELLOW": "#ffc107", "RED": "#dc3545"}[item['status']]
            
            with st.container(border=True):
                ca, cb = st.columns([3, 1])
                with ca:
                    st.markdown(f"### NSN: {item['nsn']}")
                    st.write(f"**PN:** {item['pn']} | **TO:** :blue[{item['to']}]")
                    st.write(f"**FedLog Status:** {item['fedlog']}")
                    st.caption(f"**Maintainer Note:** {item['notes']}")
                    st.error(f"**Required Action:** {item['action']}") if item['status'] == "RED" else st.warning(f"**Required Action:** {item['action']}") if item['status'] == "YELLOW" else st.success(f"**Action:** {item['action']}")
                
                with cb:
                    st.metric("Confidence", f"{item['conf']}%", delta=None)
                    if item['status'] != "RED":
                        qty = st.number_input("Qty", min_value=1, key=f"q_{item['nsn']}")
                        if st.button("Stage Part", key=f"btn_{item['nsn']}"):
                            st.session_state.cart[item['nsn']] = {"pn": item['pn'], "qty": qty}
                            st.rerun()
