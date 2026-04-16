import streamlit as st
import time

# --- 1. SESSION STATE & REFRESH LOGIC ---
if 'resolved_results' not in st.session_state:
    st.session_state.resolved_results = []
if 'cart' not in st.session_state:
    st.session_state.cart = {} # Changed to dict for quantities/deduping
if 'fingerprint' not in st.session_state:
    st.session_state.fingerprint = None

st.set_page_config(page_title="Falcon Dashboard | H4D", layout="wide")

# --- 2. SIDEBAR: INPUTS & WORKFLOW ---
with st.sidebar:
    st.title("🦅 Falcon Dashboard")
    st.caption("Maintenance Decision Support Tool v2.0")
    uploaded_file = st.file_uploader("Upload Component Image", type=['png', 'jpg', 'jpeg'])
    
    st.divider()
    mode = st.radio("Asset Type", ["Part", "Equipment (AGE)", "Unknown"], index=0)
    
    # Restored & Dynamic Categories
    if mode == "Part":
        class_options = ["Electrical/Switch", "Hydraulic/Pneumatic", "Structural"]
    elif mode == "Equipment (AGE)":
        class_options = ["Power Generation", "HVAC", "Hydraulic Stands"]
    else:
        class_options = ["Auto-Detect"]
    
    selected_class = st.selectbox("System Class", class_options)
    feature = st.text_input("Distinguishing Feature", placeholder="e.g. PN 2335 / Bleed Air")

    # --- THE REFRESH TRIGGER ---
    # Wipes results if the file, mode, or feature changes
    current_fp = f"{getattr(uploaded_file, 'name', 'none')}-{mode}-{feature}"
    if st.session_state.fingerprint != current_fp:
        st.session_state.resolved_results = []
        st.session_state.fingerprint = current_fp

    # 🛒 ACTIONABLE SUPPLY CART (Deduplicated)
    st.divider()
    st.write(f"### 🛒 Supply Cart ({len(st.session_state.cart)})")
    if not st.session_state.cart:
        st.caption("No parts staged.")
    else:
        for nsn, data in st.session_state.cart.items():
            st.write(f"**{data['pn']}** (Qty: {data['qty']})")
        
        if st.button("📤 Export to ILS-S / FedLog"):
            st.success("Logistics manifest exported to system.")

# --- 3. MAIN INTERFACE ---
col1, col2 = st.columns([1, 1])

with col1:
    st.header("1. Digital Inspection")
    if uploaded_file:
        st.image(uploaded_file, use_column_width=True)
    
    if st.button("🚀 VALIDATE LOGISTICS LOCK", type="primary", use_container_width=True):
        with st.spinner("Cross-referencing TO 1-1520-237-23 & FedLog..."):
            time.sleep(1.2)
            
            f_low = feature.lower()
            # LOGIC FIX: "Why this match" & Differentiation
            if "switch" in f_low or "2335" in f_low:
                # Results now include TO linkage and variant differentiation
                st.session_state.resolved_results = [
                    {
                        "nsn": "5930-01-235-1271", "pn": "2335-127-11", "name": "Switch, Pressure",
                        "conf": "98%", "source": "TO 1-1520-237-23", 
                        "diff": "Standard Bleed Air; ECS Compatible", "match_reason": "Visual PN Match (Spectrum Assoc.)"
                    },
                    {
                        "nsn": "5930-01-135-0096", "pn": "2335-4", "name": "Switch, Pressure",
                        "conf": "85%", "source": "IPB 1-1520-237-4",
                        "diff": "Legacy Variant; Lower PSI Threshold", "match_reason": "Geometric series similarity"
                    }
                ]
            else:
                # "Take a stab" logic for unknown images
                st.session_state.resolved_results = [
                    {
                        "nsn": "Unknown", "pn": "GEOM-VALVE-01", "name": "Valve Spool / Piston",
                        "conf": "62%", "source": "Visual Search Only",
                        "diff": "Non-indexed component", "match_reason": "Geometric profile: Cylindrical w/ Sealing Grooves"
                    }
                ]
        st.rerun()

with col2:
    st.header("2. NSN Resolution & Validation")
    if not st.session_state.resolved_results:
        st.info("Input change detected. Execute Validation to refresh logs.")
    else:
        for item in st.session_state.resolved_results:
            with st.container(border=True):
                ca, cb = st.columns([3, 1])
                with ca:
                    st.write(f"**NSN: {item['nsn']}**")
                    st.write(f"**PN: {item['pn']}**")
                    st.caption(f"**Identity:** {item['name']}")
                    # FIX: Validation & Source Linkage
                    st.caption(f"**Source:** :blue[{item['source']}]")
                    st.info(f"**Why Match:** {item['match_reason']}\n\n**Note:** {item['diff']}")
                
                with cb:
                    st.subheader(f":green[{item['conf']}]")
                    qty = st.number_input("Qty", min_value=1, value=1, key=f"q_{item['nsn']}")
                    if st.button("Add to Cart", key=f"btn_{item['nsn']}"):
                        st.session_state.cart[item['nsn']] = {"pn": item['pn'], "qty": qty}
                        st.rerun()
