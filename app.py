import streamlit as st
import time

# --- 1. STATE INITIALIZATION & REFRESH ---
if 'cart' not in st.session_state or isinstance(st.session_state.cart, list):
    st.session_state.cart = {} 
if 'resolved_results' not in st.session_state:
    st.session_state.resolved_results = []
if 'fingerprint' not in st.session_state:
    st.session_state.fingerprint = None

st.set_page_config(page_title="Falcon Dashboard | Mission Ready", layout="wide")

# --- 2. SIDEBAR: RESTORED TAXONOMY & CATEGORIES ---
with st.sidebar:
    st.title("🦅 Falcon Dashboard")
    uploaded_file = st.file_uploader("Upload Component Image", type=['png', 'jpg', 'jpeg'])
    
    st.divider()
    # RESTORED: The "IDK" safety net is back
    mode = st.radio("Asset Mode", ["Equipment", "Part", "Unknown / Not Sure"], index=2)
    
    # RESTORED: Important categories for specific maintenance workflows
    if mode == "Equipment":
        class_options = ["Power Gen", "HVAC", "Hydraulic Stands", "Towing Gear"]
    elif mode == "Part":
        class_options = ["Hydraulic", "Electrical", "Structural", "Pneumatic"]
    else:
        # The IDK step defaults to a broad scan
        class_options = ["Auto-Detect Category (Broad Scan)"]
        
    selected_class = st.selectbox("Select Class", class_options)
    feature = st.text_input("Distinguishing Feature", placeholder="e.g. Pressure Switch / PN 2335")

    # --- THE REFRESH TRIGGER ---
    # Monitors everything to ensure the NSN log purges on ANY change
    current_fp = f"{getattr(uploaded_file, 'name', 'none')}-{mode}-{feature}-{selected_class}"
    if st.session_state.fingerprint != current_fp:
        st.session_state.resolved_results = [] # PURGE stale NSNs
        st.session_state.fingerprint = current_fp

    # ACTIONABLE SUPPLY CART
    st.divider()
    st.write(f"### 🛒 Supply Request Stage ({len(st.session_state.cart)})")
    for nsn, data in st.session_state.cart.items():
        st.caption(f"**{data['pn']}** | Qty: {data['qty']}")
    
    if st.session_state.cart and st.button("📤 Export to ILS-S / FedLog"):
        st.success("Manifest Staged for Logistics Review")

# --- 3. MAIN INTERFACE ---
col1, col2 = st.columns([1, 1.2])

with col1:
    st.header("1. Digital Inspection")
    if uploaded_file:
        st.image(uploaded_file, use_column_width=True)
    
    if st.button("📝 STAGE FOR SUPPLY REQUEST", type="primary", use_container_width=True):
        with st.spinner("Locking Logistics..."):
            time.sleep(1)
            f_low = feature.lower()
            
            # Smart Branching based on your Restored Taxonomy
            if mode == "Unknown / Not Sure" and not feature:
                # The "True IDK" Result
                st.session_state.resolved_results = [{
                    "nsn": "Unknown", "pn": "PENDING_VISUAL_ID", "name": "Unindexed component",
                    "conf": 45, "status": "RED", "to": "N/A", 
                    "notes": "Low confidence. Geometry suggests valve or spool.", "action": "Escalate to Level 7"
                }]
            elif "switch" in f_low or "2335" in f_low:
                # The "Verified Part" Result
                st.session_state.resolved_results = [
                    {
                        "nsn": "5930-01-235-1271", "pn": "2335-127-11", "name": "Switch, Pressure",
                        "conf": 98, "status": "GREEN", "to": "1-1520-237-23", 
                        "notes": "Standard Bleed Air Switch.", "action": "Ready to Order"
                    }
                ]
            else:
                # Fallback for Generic AGE
                st.session_state.resolved_results = [{
                    "nsn": "6115-01-512-1001", "pn": "GEN-TX-501", "name": "Generator Set",
                    "conf": 88, "status": "YELLOW", "to": "TO 35C2-3-445-1", 
                    "notes": "Verify model variant matches image.", "action": "Verify in TO"
                }]
        st.rerun()

with col2:
    st.header("2. NSN Resolution & Validation")
    if not st.session_state.resolved_results:
        st.info("New inputs detected. Please Stage for Request to refresh logs.")
    else:
        for item in st.session_state.resolved_results:
            b_color = {"GREEN": "green", "YELLOW": "orange", "RED": "red"}[item['status']]
            with st.container(border=True):
                ca, cb = st.columns([3, 1])
                with ca:
                    st.markdown(f"### NSN: {item['nsn']}")
                    st.write(f"**PN:** {item['pn']} | **TO:** :blue[{item['to']}]")
                    st.markdown(f"**Required Action:** :{b_color}[{item['action']}]")
                with cb:
                    st.metric("Confidence", f"{item['conf']}%")
                    if item['status'] != "RED":
                        qty = st.number_input("Qty", min_value=1, key=f"q_{item['nsn']}")
                        if st.button("Stage Part", key=f"btn_{item['nsn']}"):
                            st.session_state.cart[item['nsn']] = {"pn": item['pn'], "qty": qty}
                            st.rerun()
