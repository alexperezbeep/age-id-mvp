import streamlit as st
import time

# --- 1. INITIALIZATION ---
# Using session_state ensures the cart and results persist across reruns
if 'resolved_results' not in st.session_state:
    st.session_state.resolved_results = []
if 'cart' not in st.session_state:
    st.session_state.cart = []

st.set_page_config(page_title="Falcon Dashboard", layout="wide")

# --- 2. SIDEBAR: TAXONOMY & SUPPLY CART ---
with st.sidebar:
    st.title("Falcon Dashboard")
    uploaded_file = st.file_uploader("Upload Image", type=['png', 'jpg', 'jpeg'])
    
    st.divider()
    st.write("### Taxonomy Selection")
    mode = st.radio("Mode", ["Equipment", "Part", "Unknown / Not Sure"], index=0)
    
    # Dynamic Category Mapping based on user input
    if mode == "Equipment":
        cats = ["Power Gen", "HVAC", "Hydraulic Stands", "Towing Gear"]
    elif mode == "Part":
        cats = ["Hydraulic", "Electrical", "Structural", "Pneumatic"]
    else:
        cats = ["Auto-Detect Category"]
        
    class_selection = st.selectbox("Select Class", cats)
    feature = st.text_input("Distinguishing Feature", placeholder="e.g. bulky", value="bulky")

    # --- RESTORED SUPPLY CART ---
    st.divider()
    st.write(f"### 🛒 Supply Cart ({len(st.session_state.cart)})")
    if not st.session_state.cart:
        st.caption("No items added to workflow.")
    else:
        for item in st.session_state.cart:
            st.caption(f"• {item}")
        if st.button("Clear Cart"):
            st.session_state.cart = []
            st.rerun()

# --- 3. MAIN INTERFACE ---
col1, col2 = st.columns([1, 1])

with col1:
    st.header("1. Digital Inspection")
    if uploaded_file:
        st.image(uploaded_file, use_column_width=True)
    
    if st.button("🚀 EXECUTE LOGISTICS LOCK", type="primary", use_container_width=True):
        with st.spinner("Resolving Logistics..."):
            time.sleep(1.2)
            
            # Logic: Simulating 13 results to fill Top 3 + 10 Backlog
            new_results = []
            prefix = "6115" if mode == "Equipment" else "4520"
            label = "Generator Set" if mode == "Equipment" else "Hydraulic Pump"
            
            for i in range(1, 14):
                new_results.append({
                    "nsn": f"{prefix}-01-512-100{i}",
                    "pn": f"PN-GEN-TX-{500 + i}" if mode == "Equipment" else f"PN-MLW-{100 + i}",
                    "name": f"{label}, Diesel Engine",
                    "conf": f"{99 - i}%"
                })
            st.session_state.resolved_results = new_results
        st.rerun()

with col2:
    st.header("2. NSN Resolution")
    
    if not st.session_state.resolved_results:
        st.info("Awaiting visual input for logistics resolution.")
    else:
        # TOP 3 MATCHES
        st.subheader("Top Matches")
        for item in st.session_state.resolved_results[:3]:
            with st.container(border=True):
                c_a, c_b = st.columns([3, 1])
                with c_a:
                    st.write(f"**NSN: {item['nsn']}**")
                    st.write(f"**PN: {item['pn']}**") # PN Return
                    st.caption(f"Identity: {item['name']}")
                with c_b:
                    st.subheader(f":green[{item['conf']}]")
                
                # Button adds to the restored sidebar cart
                if st.button(f"Add to Supply Cart", key=f"top_{item['nsn']}"):
                    st.session_state.cart.append(f"{item['nsn']} (PN: {item['pn']})")
                    st.toast(f"Logged {item['pn']} for review.")
                    st.rerun()

        st.divider()

        # BACKLOG DROPDOWN (7-10 Results)
        with st.expander("View Additional Potential Matches (Backlog)"):
            for item in st.session_state.resolved_results[3:13]:
                inner_1, inner_2 = st.columns([4, 1])
                inner_1.write(f"**{item['nsn']}** | PN: {item['pn']} — {item['name']}")
                inner_2.write(f"**{item['conf']}**")
                if st.button("Add", key=f"back_{item['nsn']}"):
                    st.session_state.cart.append(f"{item['nsn']} (PN: {item['pn']})")
                    st.rerun()
