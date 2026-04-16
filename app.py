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
    # LAYER 1: Asset Taxonomy
    mode = st.radio("Asset Taxonomy", ["Equipment (AGE)", "Part / Component", "Unknown"], index=2)
    
    # LAYER 1: Functional Categories (Expanded)
    if mode == "Equipment (AGE)":
        class_options = [
            "Ground Support Equipment (AGE)", "Power Generation", "Hydraulic Stands", 
            "Environmental Control / AC", "Pneumatic / Air", "Towing Gear", "Unknown"
        ]
    elif mode == "Part / Component":
        class_options = [
            "Electrical", "Hydraulic", "Fuel System", "Pneumatic / Air", 
            "Mechanical / Structural", "Cable / Interconnect", 
            "Consumable", "Avionics Support", "Unknown"
        ]
    else:
        class_options = ["Auto-Detect (Broad Scan)"]
        
    selected_class = st.selectbox("Functional Category", class_options)
    feature = st.text_input("Distinguishing Feature / Stamped PN", placeholder="e.g. eb 0402 / valve")

    # --- THE REFRESH TRIGGER ---
    current_fp = f"{getattr(uploaded_file, 'name', 'none')}-{mode}-{feature}-{selected_class}"
    if st.session_state.fingerprint != current_fp:
        st.session_state.resolved_results = [] 
        st.session_state.fingerprint = current_fp

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
        with st.spinner("Analyzing Procurement Data..."):
            time.sleep(1.2)
            f_low = feature.lower()

            # LAYER 2: Procurement / Decision Category Logic
            def get_decision_cat(conf, nsn_type="Standard"):
                if conf >= 95: return "High Confidence Identification"
                if "serial" in f_low: return "Serialized / Controlled Item"
                if "critical" in f_low: return "High-Criticality Item"
                if nsn_type == "Multiple": return "Multi-NSN Candidate"
                if conf < 60: return "Low Confidence / Unknown"
                return "Medium Confidence / Ambiguous"
            
            # --- RESOLUTION LOGIC WITH PLAIN ENGLISH NAMES ---
            
            # CASE A: POWER GEN EQUIPMENT
            if "eb 0402" in f_low or (selected_class == "Power Generation" and mode == "Equipment (AGE)"):
                st.session_state.resolved_results = [
                    {"nsn": "6115-01-517-3204", "pn": "A/M32A-60A", "name": "Diesel Generator Set", "conf": 98, "status": "GREEN", "to": "TO 35C2-3-372-11", "action": "Ready to Order", "decision": get_decision_cat(98)},
                    {"nsn": "6115-01-412-1100", "pn": "A/M32A-86", "name": "Electric Generator Set", "conf": 65, "status": "YELLOW", "to": "TO 35C2-3-467-1", "action": "Verify Output", "decision": get_decision_cat(65)}
                ]
            
            # CASE B: HYDRAULIC PARTS
            elif "valve" in f_low or "moog" in f_low or (selected_class == "Hydraulic" and mode == "Part / Component"):
                st.session_state.resolved_results = [
                    {"nsn": "4820-01-512-1001", "pn": "G761-3001P", "name": "Hydraulic Servo Valve", "conf": 97, "status": "GREEN", "to": "TO 1-1-688", "action": "Ready to Order", "decision": get_decision_cat(97)},
                    {"nsn": "4820-01-444-2222", "pn": "G761-200", "name": "Low Flow Valve", "conf": 75, "status": "YELLOW", "to": "TO 1-1-688", "action": "Verify Flow", "decision": get_decision_cat(75)}
                ]

            # CASE C: CONSUMABLES
            elif "gasket" in f_low or (selected_class == "Consumable" and mode == "Part / Component"):
                st.session_state.resolved_results = [
                    {"nsn": "5330-01-123-4567", "pn": "CESSNA-2-1/4", "name": "Fuel Tank Cap Gasket", "conf": 92, "status": "GREEN", "to": "Manual lookup", "action": "Ready to Order", "decision": "Consumable / Routine Replacement"}
                ]
            
            # DEFAULT CASE: Mismatched Category or Unknown
            else:
                st.session_state.resolved_results = [
                    {"nsn": "Multiple", "pn": "VARIOUS", "name": "Unidentified Component", "conf": 60, "status": "YELLOW", "to": "Verify in IPB", "action": "Verify Manual", "decision": get_decision_cat(60, "Multiple")}
                ]
        st.rerun()

with col2:
    st.header("2. NSN Resolution & Validation")
    if not st.session_state.resolved_results:
        st.info("Awaiting input. Select Mode/Class and Stage for Request.")
    else:
        res = sorted(st.session_state.resolved_results, key=lambda x: x['conf'], reverse=True)
        top_3 = res[:3]
        backlog = res[3:]

        st.subheader("Top Matches")
        for item in top_3:
            b_color = {"GREEN": "green", "YELLOW": "orange", "RED": "red"}[item['status']]
            with st.container(border=True):
                ca, cb = st.columns([3, 1])
                with ca:
                    # UPDATED: Prominent Plain English Nomenclature
                    st.markdown(f"### {item['name']}")
                    st.write(f"**NSN:** {item['nsn']} | **PN:** {item['pn']}")
                    st.caption(f"🛡️ **Decision Category:** {item.get('decision', 'Review Required')}")
                    st.write(f"**TO Reference:** :blue[{item['to']}]")
                    st.markdown(f"**Action:** :{b_color}[{item['action']}]")
                with cb:
                    st.metric("Confidence", f"{item['conf']}%")
                    if item['status'] != "RED":
                        qty = st.number_input("Qty", min_value=1, key=f"q_{item['nsn']}")
                        if st.button("Stage Part", key=f"btn_{item['nsn']}"):
                            st.session_state.cart[item['nsn']] = {"pn": item['pn'], "qty": qty}
                            st.rerun()

        # BACKLOG SECTION
        if backlog:
            st.divider()
            with st.expander(f"Additional Potential Matches ({len(backlog)})"):
                for item in backlog:
                    with st.container(border=True):
                        cols = st.columns([3, 1])
                        with cols[0]:
                            st.write(f"**Name:** {item['name']}")
                            st.write(f"**NSN:** {item['nsn']} | **PN:** {item['pn']}")
                        with cols[1]:
                            st.write(f"**{item['conf']}%**")
                            if st.button("Stage from Backlog", key=f"bk_{item['nsn']}"):
                                st.session_state.cart[item['nsn']] = {"pn": item['pn'], "qty": 1}
                                st.rerun()
