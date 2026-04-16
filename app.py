import streamlit as st
import time

# --- 1. ROBUST STATE INITIALIZATION ---
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
    st.caption("Decision Support for 92nd MXS")
    uploaded_file = st.file_uploader("Upload Component Image", type=['png', 'jpg', 'jpeg'])
    
    st.divider()
    # Preserved "Unknown" as the baseline safety net
    mode = st.radio("Asset Mode", ["Equipment", "Part", "Unknown / Not Sure"], index=2)
    
    # Nudge categories to direct the AI's logic
    if mode == "Equipment":
        class_options = ["Power Gen", "HVAC", "Hydraulic Stands", "Towing Gear"]
    elif mode == "Part":
        class_options = ["Hydraulic", "Electrical", "Structural", "Pneumatic"]
    else:
        class_options = ["Auto-Detect (Broad Scan)"]
        
    selected_class = st.selectbox("Select Class (Nudge AI)", class_options)
    feature = st.text_input("Distinguishing Feature", placeholder="e.g. 4-pin connector / PN 2335")

    # --- THE REFRESH TRIGGER ---
    # Purges logs if ANY input changes to prevent stale NSN display
    current_fp = f"{getattr(uploaded_file, 'name', 'none')}-{mode}-{feature}-{selected_class}"
    if st.session_state.fingerprint != current_fp:
        st.session_state.resolved_results = [] 
        st.session_state.fingerprint = current_fp

    # SUPPLY CART (LHS)
    st.divider()
    st.write(f"### 🛒 Supply Request Stage ({len(st.session_state.cart)})")
    for nsn, data in st.session_state.cart.items():
        st.caption(f"**{data['pn']}** | Qty: {data['qty']}")
    
    if st.session_state.cart:
        if st.button("📤 Export to ILS-S / Generate TO Slip", use_container_width=True):
            st.success("Manifest Staged for Logistics Review")

# --- 3. MAIN INTERFACE ---
col1, col2 = st.columns([1, 1.2])

with col1:
    st.header("1. Digital Inspection")
    if uploaded_file:
        st.image(uploaded_file, use_column_width=True)
    
    if st.button("📝 STAGE FOR SUPPLY REQUEST", type="primary", use_container_width=True):
        with st.spinner("Locking Logistics..."):
            time.sleep(1.2)
            f_low = feature.lower()
            
            # --- SIMULATED LOGIC BRANCHES ---
            if "switch" in f_low or "2335" in f_low:
                st.session_state.resolved_results = [
                    {"nsn": "5930-01-235-1271", "pn": "2335-127-11", "name": "Switch, Pressure", "conf": 98, "status": "GREEN", "to": "1-1520-237-23", "action": "Ready to Order"},
                    {"nsn": "5930-01-135-0096", "pn": "2335-4", "name": "Switch, Pressure", "conf": 72, "status": "YELLOW", "to": "1-1520-237-4", "action": "Verify PSI"},
                    {"nsn": "5930-01-000-1111", "pn": "ALT-2335", "name": "Switch, Alt", "conf": 45, "status": "YELLOW", "to": "N/A", "action": "Check Fit"},
                    {"nsn": "5930-01-999-9999", "pn": "LEGACY-X", "name": "Obsolete Switch", "conf": 12, "status": "RED", "to": "N/A", "action": "Halt Order"}
                ]
            elif "moog" in f_low or ("valve" in f_low and selected_class == "Hydraulic"):
                st.session_state.resolved_results = [
                    {"nsn": "4820-01-512-1001", "pn": "G761-3000P", "name": "Valve, Servo, Hydraulic", "conf": 97, "status": "GREEN", "to": "TO 1-1-688", "action": "Ready to Order"},
                    {"nsn": "4820-01-444-2222", "pn": "G761-200", "name": "Valve, Low Flow", "conf": 65, "status": "YELLOW", "to": "TO 1-1-688", "action": "Verify Flow Rate"},
                    {"nsn": "4820-01-111-3333", "pn": "MOOG-GEN", "name": "General Valve", "conf": 40, "status": "YELLOW", "to": "N/A", "action": "Check Dimensions"},
                    {"nsn": "4820-01-888-0000", "pn": "PNEU-V", "name": "Pneumatic Alt", "conf": 15, "status": "RED", "to": "N/A", "action": "Wrong System"}
                ]
            else:
                st.session_state.resolved_results = [
                    {"nsn": "Multiple", "pn": "VARIOUS", "name": "System Match", "conf": 60, "status": "YELLOW", "to": "Verify in IPB", "action": "Verify Manual"}
                ]
        st.rerun()

with col2:
    st.header("2. NSN Resolution & Validation")
    if not st.session_state.resolved_results:
        st.info("Awaiting input. Select Mode/Class and Stage for Request.")
    else:
        # Sort by confidence descending
        res = sorted(st.session_state.resolved_results, key=lambda x: x['conf'], reverse=True)
        top_3 = res[:3]
        backlog = res[3:]

        # TOP MATCHES
        st.subheader("Top Matches")
        for item in top_3:
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

        # BACKLOG DROPDOWN
        if backlog:
            st.divider()
            with st.expander(f"View Additional Potential Matches (Backlog: {len(backlog)})"):
                for item in backlog:
                    with st.container(border=True):
                        cols = st.columns([3, 1])
                        with cols[0]:
                            st.write(f"**NSN:** {item['nsn']} | **PN:** {item['pn']}")
                            st.caption(f"Reasoning: Secondary match via {selected_class} logic.")
                        with cols[1]:
                            st.write(f"**{item['conf']}%**")
                            if st.button("Stage from Backlog", key=f"bk_{item['nsn']}"):
                                st.session_state.cart[item['nsn']] = {"pn": item['pn'], "qty": 1}
                                st.rerun()
