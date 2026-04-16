import streamlit as st
import time

# --- INITIALIZATION ---
# This ensures your results don't reset when you click "Add to Cart"
if 'resolved_nsns' not in st.session_state:
    st.session_state.resolved_nsns = []
if 'cart' not in st.session_state:
    st.session_state.cart = {}

st.set_page_config(page_title="Falcon Dashboard", layout="wide")

# --- CUSTOM CSS ---
st.markdown("""
    <style>
    .stApp { background-color: #0E1117; }
    .nsn-card {
        background-color: #161B22;
        border: 1px solid #30363D;
        padding: 20px;
        border-radius: 10px;
        margin-bottom: 15px;
    }
    .confidence { color: #2EA043; font-weight: bold; font-size: 1.5rem; }
    </style>
    """, unsafe_allow_html=True)

# --- SIDEBAR ---
with st.sidebar:
    st.title("Falcon Dashboard")
    uploaded_file = st.file_uploader("Upload Image", type=['png', 'jpg', 'jpeg'])
    
    st.write("### Taxonomy Selection")
    taxonomy = st.radio("Type", ["Equipment", "Part"], index=1, label_visibility="collapsed")
    
    st.write("### Select Part Class")
    p_class = st.selectbox("Class", ["Hydraulic", "Electrical", "Structural"], label_visibility="collapsed")
    
    st.write("### Distinguishing Feature (Optional)")
    feature = st.text_input("Feature", value="hydraylic punpk", label_visibility="collapsed")

    st.divider()
    st.write("### 🛒 Supply Cart")
    if not st.session_state.cart:
        st.caption("No items in cart.")
    else:
        for nsn, qty in st.session_state.cart.items():
            st.write(f"**{nsn}** (Qty: {qty})")

# --- MAIN INTERFACE ---
col1, col2 = st.columns([1, 1])

with col1:
    st.header("1. Digital Inspection")
    if uploaded_file:
        st.image(uploaded_file, use_column_width=True)
    
    # THE TRIGGER: This breaks the "Full Block"
    if st.button("🚀 EXECUTE LOGISTICS LOCK", type="primary", use_container_width=True):
        with st.spinner("Analyzing maintenance data..."):
            time.sleep(1.2) # Simulate model latency
            
            # CALCULATION LOGIC: 
            # In a real app, this calls your AGE-ID-MVP model.
            # Here, we update the state so the right column reacts.
            if "pump" in feature.lower() or "punpk" in feature.lower():
                st.session_state.resolved_nsns = [
                    {"nsn": "4520-01-135-2770", "label": "Hydraulic (H-1)", "conf": "96%"},
                    {"nsn": "4520-01-482-8571", "label": "Hydraulic (NGH-1)", "conf": "82%"},
                    {"nsn": "4520-00-540-1444", "label": "Hydraulic (BT400)", "conf": "62%"}
                ]
            else:
                st.session_state.resolved_nsns = [{"nsn": "Unknown", "label": "Manual Lookup Req", "conf": "N/A"}]
        st.rerun()

with col2:
    st.header("2. NSN Resolution")
    
    # If state is empty, show the "Static" message or instructions
    if not st.session_state.resolved_nsns:
        st.info("Upload AGE part image and execute logistics lock to resolve NSN.")
    else:
        # DYNAMIC RENDERING: Loops through the results in session state
        for item in st.session_state.resolved_nsns:
            with st.container():
                st.markdown(f"""
                <div class="nsn-card">
                    <div style="display: flex; justify-content: space-between; align-items: center;">
                        <div>
                            <div style="color: #8B949E; font-size: 0.8rem;">NSN: {item['nsn']}</div>
                            <div style="font-weight: bold; font-size: 1.1rem;">{item['label']}</div>
                            <div style="color: #8B949E; font-size: 0.75rem;">Logistics Match Confirmed via Visual Anchors.</div>
                        </div>
                        <div class="confidence">{item['conf']}</div>
                    </div>
                </div>
                """, unsafe_allow_html=True)
                
                # Dynamic Button Logic for the Cart
                if st.button(f"Add to Supply Cart", key=f"btn_{item['nsn']}"):
                    st.session_state.cart[item['nsn']] = st.session_state.cart.get(item['nsn'], 0) + 1
                    st.toast(f"NSN {item['nsn']} added to workflow.")
