import streamlit as st
import time

# --- 1. MANDATORY RESET CALLBACK ---
def clear_on_upload():
    """Wipes all logistics data as soon as a new file is detected"""
    st.session_state.resolved_results = []
    # Optionally clear the 'Distinguishing Feature' text too
    if 'feature_input' in st.session_state:
        st.session_state.feature_input = ""

# Initialize states
if 'resolved_results' not in st.session_state:
    st.session_state.resolved_results = []
if 'cart' not in st.session_state:
    st.session_state.cart = []

# --- 2. SIDEBAR WITH CALLBACKS ---
with st.sidebar:
    st.title("Falcon Dashboard")
    # THE KEY: on_change triggers the clear_on_upload function immediately
    uploaded_file = st.file_uploader(
        "Upload Image", 
        type=['png', 'jpg', 'jpeg'], 
        on_change=clear_on_upload
    )
    
    st.divider()
    mode = st.radio("Mode", ["Equipment", "Part", "Unknown / Not Sure"], index=2)
    
    # Auto-adjust class options based on mode
    class_opts = ["Auto-Detect"] if mode == "Unknown / Not Sure" else ["Hydraulic", "Electrical", "Power Gen"]
    st.selectbox("Select Class", class_opts)
    
    feature = st.text_input("Distinguishing Feature", key="feature_input")

    # Supply Cart visibility
    st.divider()
    st.write(f"### 🛒 Supply Cart ({len(st.session_state.cart)})")
    for item in st.session_state.cart:
        st.caption(f"• {item}")

# --- 3. MAIN DASHBOARD ---
col1, col2 = st.columns([1, 1])

with col1:
    st.header("1. Digital Inspection")
    if uploaded_file:
        st.image(uploaded_file, use_column_width=True)
    
    if st.button("🚀 EXECUTE LOGISTICS LOCK", type="primary", use_container_width=True):
        with st.spinner("Analyzing..."):
            time.sleep(1.2)
            
            # Logic branch: Identify based on 'feature' or 'mode'
            f_low = feature.lower()
            if "switch" in f_low or "pressure" in f_low:
                name, ns_pre, pn_pre = "Switch, Pressure", "5930", "PN-SW-3381"
            elif mode == "Equipment":
                name, ns_pre, pn_pre = "Generator Set", "6115", "PN-GEN-TX-50"
            else:
                name, ns_pre, pn_pre = "Hydraulic Pump", "4520", "PN-MLW-10"

            # Fill Top 3 + Backlog results
            st.session_state.resolved_results = [
                {"nsn": f"{ns_pre}-01-235-{1270+i}", "pn": f"{pn_pre}{i}", "name": name, "conf": f"{99-i}%"}
                for i in range(1, 14)
            ]
        st.rerun()

with col2:
    st.header("2. NSN Resolution")
    if not st.session_state.resolved_results:
        # User sees this instantly after a new upload
        st.info("New image detected. Please execute logistics lock to resolve.")
    else:
        # Render Top 3
        for item in st.session_state.resolved_results[:3]:
            with st.container(border=True):
                ca, cb = st.columns([3, 1])
                ca.write(f"**NSN: {item['nsn']}**\n\n**PN: {item['pn']}**")
                ca.caption(f"Identity: {item['name']}")
                cb.subheader(f":green[{item['conf']}]")
                if st.button("Add to Supply Cart", key=f"t_{item['nsn']}"):
                    st.session_state.cart.append(f"{item['nsn']} (PN: {item['pn']})")
                    st.rerun()

        # Render Backlog Dropdown
        with st.expander("View Additional Potential Matches (Backlog)"):
            for item in st.session_state.resolved_results[3:13]:
                st.write(f"**{item['nsn']}** | PN: {item['pn']} — {item['conf']}")
