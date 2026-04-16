import streamlit as st
import time

# --- 1. INITIALIZATION ---
if 'resolved_results' not in st.session_state:
    st.session_state.resolved_results = []
if 'cart' not in st.session_state:
    st.session_state.cart = []

st.set_page_config(page_title="Falcon Dashboard", layout="wide")

# --- 2. SIDEBAR: DYNAMIC TAXONOMY ---
with st.sidebar:
    st.title("Falcon Dashboard")
    uploaded_file = st.file_uploader("Upload Image", type=['png', 'jpg', 'jpeg'])
    
    st.divider()
    st.write("### Taxonomy Selection")
    mode = st.radio("Mode", ["Equipment", "Part", "Unknown / Not Sure"], index=2)
    
    if mode == "Equipment":
        cats = ["Not Sure", "Power Gen", "HVAC", "Hydraulic Stands", "Towing"]
    elif mode == "Part":
        cats = ["Not Sure", "Hydraulic", "Electrical", "Structural", "Pneumatic"]
    else:
        cats = ["Auto-Detect Category"]
        
    class_selection = st.selectbox("Select Class", cats)
    feature = st.text_input("Distinguishing Feature (Optional)", placeholder="e.g. PN 338127-11")

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
        with st.spinner("Resolving Logistics Data..."):
            time.sleep(1.2)
            # MOCK DATA GENERATION (Simulating 10+ results)
            # In production, this data comes from your model/API
            results = []
            for i in range(1, 14):
                results.append({
                    "nsn": f"4520-01-135-277{i}",
                    "pn": f"PN-MLW-{100 + i}",
                    "name": "Hydraulic Pump Assembly" if i < 4 else "Alternate Component",
                    "conf": f"{98 - (i*3)}%"
                })
            st.session_state.resolved_results = results
        st.rerun()

with col2:
    st.header("2. NSN Resolution")
    
    if not st.session_state.resolved_results:
        st.info("Awaiting visual input for logistics resolution.")
    else:
        # TOP 3 CHOICES
        st.subheader("Top Matches")
        for item in st.session_state.resolved_results[:3]:
            with st.container(border=True):
                c_a, c_b = st.columns([3, 1])
                with c_a:
                    st.write(f"**NSN: {item['nsn']}**")
                    st.write(f"**PN: {item['pn']}**")
                    st.caption(f"Identity: {item['name']}")
                with c_b:
                    st.subheader(f":green[{item['conf']}]")
                
                if st.button("Add to Supply Cart", key=f"top_{item['nsn']}"):
                    st.session_state.cart.append(f"{item['nsn']} (PN: {item['pn']})")
                    st.toast(f"Added {item['pn']} to Cart")

        st.divider()

        # BACKLOG DROPDOWN (Results 4-13)
        with st.expander("View Additional Potential Matches (Backlog)"):
            for item in st.session_state.resolved_results[3:13]:
                inner_1, inner_2 = st.columns([4, 1])
                inner_1.write(f"**{item['nsn']}** | PN: {item['pn']} — {item['name']}")
                inner_2.write(f"**{item['conf']}**")
                if st.button("Add", key=f"back_{item['nsn']}"):
                    st.session_state.cart.append(f"{item['nsn']} (PN: {item['pn']})")
                    st.rerun()
