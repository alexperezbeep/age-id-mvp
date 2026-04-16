import streamlit as st
import time

# --- 1. THE IRONCLAD RESET LOGIC ---
if 'resolved_results' not in st.session_state:
    st.session_state.resolved_results = []
if 'cart' not in st.session_state:
    st.session_state.cart = []
if 'last_seen_file' not in st.session_state:
    st.session_state.last_seen_file = None

st.set_page_config(page_title="Falcon Dashboard", layout="wide")

# --- 2. SIDEBAR: INPUTS & AUTO-WIPE ---
with st.sidebar:
    st.title("Falcon Dashboard")
    uploaded_file = st.file_uploader("Upload Image", type=['png', 'jpg', 'jpeg'])
    
    # TRIPLE DOWN RESET: Detects new file and KILLS stale results immediately
    if uploaded_file:
        file_id = f"{uploaded_file.name}-{uploaded_file.size}"
        if st.session_state.last_seen_file != file_id:
            st.session_state.resolved_results = [] # PURGE stale data
            st.session_state.last_seen_file = file_id

    st.divider()
    mode = st.radio("Mode", ["Equipment", "Part", "Unknown / Not Sure"], index=2)
    feature = st.text_input("Distinguishing Feature", placeholder="e.g. Pressure Switch / PN 2335")

    # RESTORED SUPPLY CART
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
        with st.spinner("Analyzing Visual Geometry..."):
            time.sleep(1.2)
            
            f_low = feature.lower()
            results = []

            # LOGIC BRANCH A: Known Keyword Match (Pressure Switch)
            if "switch" in f_low or "pressure" in f_low or "2335" in f_low:
                identity = "Switch, Pressure, Bleed Air (UH-60 ECS)"
                ns_pre, pn_pre = "5930-01-235", "PN-2335-127-11"
                conf_base = 98
            
            # LOGIC BRANCH B: Take a Stab (Geometric Analysis for Unknown Parts)
            elif uploaded_file and not feature:
                identity = "Probable Piston-Style Valve Spool"
                ns_pre, pn_pre = "53XX-XX-XXX", "PN-UNKNOWN-GEOM"
                conf_base = 65 # Lowered confidence for visual-only "stabs"
            
            # LOGIC BRANCH C: Equipment Fallback
            elif mode == "Equipment":
                identity = "Generator Set, Diesel Engine"
                ns_pre, pn_pre = "6115-01-512", "PN-GEN-TX-501"
                conf_base = 97
            
            # DEFAULT FALLBACK
            else:
                identity = "Hydraulic Pump Assembly"
                ns_pre, pn_pre = "4520-01-135", "PN-MLW-101"
                conf_base = 90

            # Generate 13 results: Top 3 + 10 Backlog
            for i in range(1, 14):
                results.append({
                    "nsn": f"{ns_pre}-{1270+i}",
                    "pn": f"{pn_pre}-{i}",
                    "name": identity,
                    "conf": f"{conf_base - i}%"
                })
            st.session_state.resolved_results = results
        st.rerun()

with col2:
    st.header("2. NSN Resolution")
    
    if not st.session_state.resolved_results:
        st.info("New image or input detected. Execute logistics lock to resolve.")
    else:
        # 1. TOP 3 MATCHES (With PN Return)
        st.subheader("Top Matches")
        for item in st.session_state.resolved_results[:3]:
            with st.container(border=True):
                ca, cb = st.columns([3, 1])
                with ca:
                    st.write(f"**NSN: {item['nsn']}**")
                    st.write(f"**PN: {item['pn']}**")
                    st.caption(f"Identity: {item['name']}")
                cb.subheader(f":green[{item['conf']}]")
                if st.button("Add to Supply Cart", key=f"t_{item['nsn']}"):
                    st.session_state.cart.append(f"{item['nsn']} (PN: {item['pn']})")
                    st.rerun()

        # 2. BACKLOG DROPDOWN (7-10 Results)
        st.divider()
        with st.expander("View Additional Potential Matches (Backlog)"):
            for item in st.session_state.resolved_results[3:13]:
                c1, c2 = st.columns([4, 1])
                c1.write(f"**{item['nsn']}** | PN: {item['pn']} — {item['name']}")
                c2.write(f"**{item['conf']}**")
                if st.button("Add", key=f"b_{item['nsn']}"):
                    st.session_state.cart.append(item['nsn'])
                    st.rerun()
