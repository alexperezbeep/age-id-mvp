import streamlit as st
import time

# --- 1. INITIALIZATION & RESET LOGIC ---
if 'resolved_results' not in st.session_state:
    st.session_state.resolved_results = []
if 'cart' not in st.session_state:
    st.session_state.cart = []

def reset_results():
    """Callback to clear old data when a new image is uploaded"""
    st.session_state.resolved_results = []

# --- 2. SIDEBAR ---
with st.sidebar:
    st.title("Falcon Dashboard")
    
    # The 'on_change' trigger is the secret to the reset
    uploaded_file = st.file_uploader(
        "Upload Image", 
        type=['png', 'jpg', 'jpeg'], 
        on_change=reset_results
    )
    
    st.divider()
    mode = st.radio("Mode", ["Equipment", "Part", "Unknown / Not Sure"], index=2)
    
    if mode == "Equipment":
        cats = ["Not Sure", "Power Gen", "HVAC", "Hydraulic Stands"]
    elif mode == "Part":
        cats = ["Not Sure", "Hydraulic", "Electrical", "Structural"]
    else:
        cats = ["Auto-Detect Category"]
        
    class_selection = st.selectbox("Select Class", cats)
    feature = st.text_input("Distinguishing Feature", placeholder="e.g. Pressure Switch")

    # Supply Cart
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
        with st.spinner("Analyzing new visual data..."):
            time.sleep(1.2)
            
            # THE LOGIC: Checks 'feature' or 'mode' to determine results
            new_data = []
            f_low = feature.lower()
            
            if "switch" in f_low or "pressure" in f_low:
                name, ns_pre, pn_pre = "Switch, Pressure", "5930", "PN-SW-3381"
            elif mode == "Equipment":
                name, ns_pre, pn_pre = "Generator Set", "6115", "PN-GEN-TX-50"
            else:
                name, ns_pre, pn_pre = "Hydraulic Pump", "4520", "PN-MLW-10"

            for i in range(1, 14):
                new_data.append({
                    "nsn": f"{ns_pre}-01-235-{1270+i}",
                    "pn": f"{pn_pre}{i}",
                    "name": name,
                    "conf": f"{99 - i}%"
                })
            st.session_state.resolved_results = new_data
        st.rerun()

with col2:
    st.header("2. NSN Resolution")
    
    if not st.session_state.resolved_results:
        # This will now show correctly as soon as you upload a new image
        st.info("New image detected. Please execute logistics lock to resolve.")
    else:
        st.subheader("Top Matches")
        for item in st.session_state.resolved_results[:3]:
            with st.container(border=True):
                ca, cb = st.columns([3, 1])
                with ca:
                    st.write(f"**NSN: {item['nsn']}**\n\n**PN: {item['pn']}**")
                    st.caption(f"Identity: {item['name']}")
                cb.subheader(f":green[{item['conf']}]")
                if st.button("Add to Supply Cart", key=f"t_{item['nsn']}"):
                    st.session_state.cart.append(f"{item['nsn']} (PN: {item['pn']})")
                    st.rerun()

        st.divider()
        with st.expander("View Additional Potential Matches (Backlog)"):
            for item in st.session_state.resolved_results[3:13]:
                st.write(f"**{item['nsn']}** | PN: {item['pn']} — {item['conf']}")
                if st.button("Add", key=f"b_{item['nsn']}"):
                    st.session_state.cart.append(item['nsn'])
                    st.rerun()
