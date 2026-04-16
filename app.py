import streamlit as st
import time

# --- 1. ROBUST STATE INITIALIZATION ---
# Forces the cart to a dict if it was a list in a previous session (Fixes AttributeError)
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
    # PRESERVED: 'Unknown / Not Sure' as the default safety net
    mode = st.radio("Asset Mode", ["Equipment", "Part", "Unknown / Not Sure"], index=2)
    
    # RESTORED: Critical categories for user nudging
    if mode == "Equipment":
        class_options = ["Power Gen", "HVAC", "Hydraulic Stands", "Towing Gear"]
    elif mode == "Part":
        class_options = ["Hydraulic", "Electrical", "Structural", "Pneumatic"]
    else:
        class_options = ["Auto-Detect (Broad Scan)"]
        
    selected_class = st.selectbox("Select Class (Nudge AI)", class_options)
    feature = st.text_input("Distinguishing Feature", placeholder="e.g. 4-pin connector / PN 2335")

    # --- THE REFRESH TRIGGER ---
    # Monitors name, mode, feature, and class. If ANY change, logs are PURGED.
    current_fp = f"{getattr(uploaded_file, 'name', 'none')}-{mode}-{feature}-{selected_class}"
    if st.session_state.fingerprint != current_fp:
        st.session_state.resolved_results = [] # Instant purge for fresh data
        st.session_state.fingerprint = current_fp

    # ACTIONABLE SUPPLY REQUEST STAGE
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
            
            # --- BRANCH 1: HIGH-CONFIDENCE SWITCHES ---
            if "switch" in f_low or "2335" in f_low:
                st.session_state.resolved_results = [
                    {
                        "nsn": "5930-01-235-1271", "pn": "2335-127-11", "name": "Switch, Pressure",
                        "conf": 98, "status": "GREEN", "to": "1-1520-237-23", 
                        "notes": "Verified match via PN feature.", "action": "Ready to Order"
                    }
                ]
            
            # --- BRANCH 2: MOOG/HYDRAULIC RESOLUTION (The Fix) ---
            elif "moog" in f_low or ("4-pin" in f_low and selected_class == "Hydraulic"):
                st.session_state.resolved_results = [
                    {
                        "nsn": "4820-01-512-1001", "pn": "G761-3000P", "name": "Valve, Servo, Hydraulic",
                        "conf": 97, "status": "GREEN", "to": "TO 1-1-688", 
                        "notes": "Confidence jump based on Hydraulic Class + 4-pin profile.", "action": "Ready to Order"
                    }
                ]

            # --- BRANCH 3: THE 'IDK' / LOW-CONFIDENCE CATCH-ALL ---
            else:
                st.session_state.resolved_results = [{
                    "nsn": "Multiple Matches", "pn": "VARIOUS", "name": "System Match",
                    "conf": 60, "status": "YELLOW", "to": "Verify in IPB", 
                    "notes": f"Broad search in {selected_class}. Nudge with Feature for 90%+", "action": "Verify Manual"
                }]
        st.rerun()

with col2:
    st.header("2. NSN Resolution & Validation")
    if not st.session_state.resolved_results:
        st.info("Input change detected. Stage for Request to see fresh logs.")
    else:
        for item in st.session_state.resolved_results:
            b_color = {"GREEN": "green", "YELLOW": "orange", "RED": "red"}[item['status']]
            with st.container(border=True):
                ca, cb = st.columns([3, 1])
                with ca:
                    st.markdown(f"### NSN: {item['nsn']}")
                    st.write(f"**PN:** {item['pn']} | **TO:** :blue[{item['to']}]")
                    st.markdown(f"**Required Action:** :{b_color}[{item['action']}]")
                with cb:
                    st.metric("Confidence", f"{item['conf']}%")
                    if item['status'] != "RED":
                        qty = st.number_input("Qty", min_value=1, key=f"q_{item['nsn']}")
                        if st.button("Stage Part", key=f"btn_{item['nsn']}"):
                            st.session_state.cart[item['nsn']] = {"pn": item['pn'], "qty": qty}
                            st.rerun()
