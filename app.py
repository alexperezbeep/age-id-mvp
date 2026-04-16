import streamlit as st
import time

# --- 1. THE ULTIMATE RESET TRIGGER ---
# We track the 'fingerprint' of the current session to detect ANY change
if 'fingerprint' not in st.session_state:
    st.session_state.fingerprint = None
if 'resolved_results' not in st.session_state:
    st.session_state.resolved_results = []
if 'cart' not in st.session_state:
    st.session_state.cart = []

st.set_page_config(page_title="Falcon Dashboard", layout="wide")

# --- 2. SIDEBAR & INPUTS ---
with st.sidebar:
    st.title("Falcon Dashboard")
    uploaded_file = st.file_uploader("Upload Image", type=['png', 'jpg', 'jpeg'])
    
    st.divider()
    mode = st.radio("Mode", ["Equipment", "Part", "Unknown / Not Sure"], index=2)
    
    # Class Selection
    class_opts = ["Auto-Detect"] if mode == "Unknown / Not Sure" else ["Hydraulic", "Electrical", "Power Gen"]
    st.selectbox("Select Class", class_opts)
    
    # Feature Input
    feature = st.text_input("Distinguishing Feature", placeholder="e.g. Pressure Switch")

    # --- FINGERPRINT CHECK ---
    # If the file or text changes, we KILLED the old results immediately
    current_fp = f"{getattr(uploaded_file, 'name', 'none')}-{feature}"
    if st.session_state.fingerprint != current_fp:
        st.session_state.resolved_results = [] # WIPE
        st.session_state.fingerprint = current_fp

    # Supply Cart Display
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
    
    # THE LOCK-IN TRIGGER
    if st.button("🚀 EXECUTE LOGISTICS LOCK", type="primary", use_container_width=True):
        with st.spinner("Locking Logistics Data..."):
            time.sleep(1.2)
            
            # HARD-WIRED LOGIC MATCHING YOUR UPLOADS
            f_low = feature.lower()
            if "switch" in f_low or "pressure" in f_low:
                identity, ns_pre, pn_pre = "Switch, Pressure, Bleed Air", "5930-01-235", "PN-338127-11"
            elif mode == "Equipment" or "bulky" in f_low:
                identity, ns_pre, pn_pre = "Generator Set, Diesel", "6115-01-512", "PN-GEN-TX-501"
            else:
                identity, ns_pre, pn_pre = "Hydraulic Pump Assembly", "4520-01-135", "PN-MLW-101"

            # Generate 13 results (Top 3 + 10 Backlog)
            st.session_state.resolved_results = [
                {"nsn": f"{ns_pre}-{1270+i}", "pn": f"{pn_pre}-{i}", "name": identity, "conf": f"{99-i}%"}
                for i in range(1, 14)
            ]
        st.rerun()

with col2:
    st.header("2. NSN Resolution")
    
    if not st.session_state.resolved_results:
        # This will now correctly trigger the second you upload a new image
        st.info("New data detected. Execute logistics lock to resolve.")
    else:
        # TOP 3 MATCHES
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

        # BACKLOG DROPDOWN
        st.divider()
        with st.expander("View Additional Potential Matches (Backlog)"):
            for item in st.session_state.resolved_results[3:13]:
                st.write(f"**{item['nsn']}** | PN: {item['pn']} — {item['name']}")
                if st.button("Add", key=f"b_{item['nsn']}"):
                    st.session_state.cart.append(item['nsn'])
                    st.rerun()
