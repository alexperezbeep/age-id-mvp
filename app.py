import streamlit as st
import time

# --- 1. STATE INITIALIZATION ---
if 'resolved_results' not in st.session_state:
    st.session_state.resolved_results = []
if 'cart' not in st.session_state:
    st.session_state.cart = []
if 'fingerprint' not in st.session_state:
    st.session_state.fingerprint = None

st.set_page_config(page_title="Falcon Dashboard", layout="wide")

# --- 2. SIDEBAR WITH CLASS RESTORATION ---
with st.sidebar:
    st.title("Falcon Dashboard")
    uploaded_file = st.file_uploader("Upload Image", type=['png', 'jpg', 'jpeg'])
    
    st.divider()
    # Mode determines which classes appear below
    mode = st.radio("Mode", ["Equipment", "Part", "Unknown / Not Sure"], index=0)
    
    # THE RESTORATION: Explicitly defining categories for each mode
    if mode == "Equipment":
        class_options = ["Power Gen", "HVAC", "Hydraulic Stands", "Towing Gear"]
    elif mode == "Part":
        class_options = ["Hydraulic", "Electrical", "Structural", "Pneumatic"]
    else:
        class_options = ["Auto-Detect Category"]
        
    # This was likely missing or wrapped in an incorrect 'if' statement
    selected_class = st.selectbox("Select Class", class_options)
    
    feature = st.text_input("Distinguishing Feature", placeholder="e.g. Pressure Switch / PN 2335")

    # --- AUTO-RESET LOGIC ---
    current_fp = f"{getattr(uploaded_file, 'name', 'none')}-{mode}-{feature}"
    if st.session_state.fingerprint != current_fp:
        st.session_state.resolved_results = []
        st.session_state.fingerprint = current_fp

    # SUPPLY CART
    st.divider()
    st.write(f"### 🛒 Supply Cart ({len(st.session_state.cart)})")
    for item in st.session_state.cart:
        st.caption(f"• {item}")

# --- 3. MAIN INTERFACE ---
col1, col2 = st.columns([1, 1])

with col1:
    st.header("1. Digital Inspection")
    if uploaded_file:
        st.image(uploaded_file, use_column_width=True)
    
    if st.button("🚀 EXECUTE LOGISTICS LOCK", type="primary", use_container_width=True):
        with st.spinner("Locking Logistics..."):
            time.sleep(1)
            
            # Dynamic Logic based on Inputs
            f_low = feature.lower()
            if "switch" in f_low or "pressure" in f_low:
                name, ns_pre, pn_pre = "Switch, Pressure, Bleed Air", "5930-01-235", "PN-2335-127-11"
            elif mode == "Equipment":
                name, ns_pre, pn_pre = "Generator Set, Diesel", "6115-01-512", "PN-GEN-TX-501"
            else:
                name, ns_pre, pn_pre = "Probable Valve Spool", "53XX-XX-XXX", "PN-UNKNOWN-GEOM"

            st.session_state.resolved_results = [
                {"nsn": f"{ns_pre}-{1270+i}", "pn": f"{pn_pre}-{i}", "name": name, "conf": f"{98-i}%"}
                for i in range(1, 14)
            ]
        st.rerun()

with col2:
    st.header("2. NSN Resolution")
    if not st.session_state.resolved_results:
        st.info("Awaiting input. Select Mode and Class, then Execute Lock.")
    else:
        st.subheader("Top Matches")
        for item in st.session_state.resolved_results[:3]:
            with st.container(border=True):
                ca, cb = st.columns([3, 1])
                with ca:
                    st.write(f"**NSN: {item['nsn']}**\n**PN: {item['pn']}**")
                    st.caption(f"Identity: {item['name']}")
                cb.subheader(f":green[{item['conf']}]")
                if st.button("Add to Supply Cart", key=f"t_{item['nsn']}"):
                    st.session_state.cart.append(f"{item['pn']} ({item['nsn']})")
                    st.rerun()

        with st.expander("View Additional Potential Matches (Backlog)"):
            for item in st.session_state.resolved_results[3:13]:
                st.write(f"**{item['nsn']}** | PN: {item['pn']} — {item['conf']}")
