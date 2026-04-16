import streamlit as st
import time

# --- 1. STATE INITIALIZATION ---
if 'cart' not in st.session_state or isinstance(st.session_state.cart, list):
    st.session_state.cart = {} 
if 'resolved_results' not in st.session_state:
    st.session_state.resolved_results = []
if 'fingerprint' not in st.session_state:
    st.session_state.fingerprint = None

st.set_page_config(page_title="Falcon Dashboard | H4D Phase 3", layout="wide")

# --- 2. SIDEBAR: THE NUDGE ENGINE ---
with st.sidebar:
    st.title("🦅 Falcon Dashboard")
    uploaded_file = st.file_uploader("Upload Component Image", type=['png', 'jpg', 'jpeg'])
    
    st.divider()
    # The 'IDK' option is preserved as the neutral starting point
    mode = st.radio("Asset Mode", ["Equipment", "Part", "Unknown / Not Sure"], index=2)
    
    # RESTORED: Specific categories to nudge the AI's search parameters
    if mode == "Equipment":
        class_options = ["Power Gen", "HVAC", "Hydraulic Stands", "Towing Gear", "Light Carts"]
    elif mode == "Part":
        class_options = ["Hydraulic", "Electrical", "Structural", "Pneumatic", "Avionics"]
    else:
        class_options = ["Auto-Detect (Broad Search)"]
        
    selected_class = st.selectbox("Select Class (Nudge AI)", class_options)
    feature = st.text_input("Distinguishing Feature", placeholder="e.g. Pressure Switch / PN 2335")

    # --- THE REFRESH TRIGGER ---
    # Now monitors 'selected_class' so the AI refreshes when you nudge it
    current_fp = f"{getattr(uploaded_file, 'name', 'none')}-{mode}-{feature}-{selected_class}"
    if st.session_state.fingerprint != current_fp:
        st.session_state.resolved_results = [] 
        st.session_state.fingerprint = current_fp

    # SUPPLY CART
    st.divider()
    st.write(f"### 🛒 Supply Request Stage ({len(st.session_state.cart)})")
    for nsn, data in st.session_state.cart.items():
        st.caption(f"**{data['pn']}** | Qty: {data['qty']}")
    
    if st.session_state.cart:
        if st.button("📤 Export to ILS-S / FedLog"):
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
            
            # Logic that respects the user's "Nudge"
            if mode == "Unknown / Not Sure" and not feature:
                st.session_state.resolved_results = [{
                    "nsn": "Unknown", "pn": "PENDING_ID", "name": "Unindexed component",
                    "conf": 45, "status": "RED", "to": "N/A", 
                    "notes": "Broad scan active. Provide Class nudge for better accuracy.", "action": "Escalate to Level 7"
                }]
            elif "switch" in f_low or "2335" in f_low:
                st.session_state.resolved_results = [
                    {
                        "nsn": "5930-01-235-1271", "pn": "2335-127-11", "name": "Switch, Pressure",
                        "conf": 98, "status": "GREEN", "to": "1-1520-237-23", 
                        "notes": "Verified match via PN feature.", "action": "Ready to Order"
                    }
                ]
            elif selected_class == "Power Gen":
                st.session_state.resolved_results = [{
                    "nsn": "6115-01-512-1001", "pn": "GEN-TX-501", "name": "Generator Set",
                    "conf": 92, "status": "GREEN", "to": "35C2-3-445-1", 
                    "notes": "Nudge applied: Power Gen Class.", "action": "Ready to Order"
                }]
            else:
                st.session_state.resolved_results = [{
                    "nsn": "Multiple Matches", "pn": "VARIOUS", "name": "System Match",
                    "conf": 60, "status": "YELLOW", "to": "Verify in IPB", 
                    "notes": f"Search filtered by {selected_class}.", "action": "Verify Manual"
                }]
        st.rerun()

with col2:
    st.header("2. NSN Resolution & Validation")
    if not st.session_state.resolved_results:
        st.info("Awaiting input. Select Mode/Class and Stage for Request.")
    else:
        for item in st.session_state.resolved_results:
            b_color = {"GREEN": "green", "YELLOW": "orange", "RED": "red"}[item['status']]
            with st.container(border=True):
                ca, cb = st.columns([3, 1])
                with ca:
                    st.markdown(f"### NSN: {item['nsn']}")
                    st.write(f"**PN:** {item['pn']} | **TO:** :blue[{item['to']}]")
                    st.markdown(f"**Action:** :{b_color}[{item['action']}]")
                with cb:
                    st.metric("Confidence", f"{item['conf']}%")
                    if item['status'] != "RED":
                        qty = st.number_input("Qty", min_value=1, key=f"q_{item['nsn']}")
                        if st.button("Stage Part", key=f"btn_{item['nsn']}"):
                            st.session_state.cart[item['nsn']] = {"pn": item['pn'], "qty": qty}
                            st.rerun()
