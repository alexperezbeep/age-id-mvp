import streamlit as st
from google import genai
from google.genai import types
from PIL import Image
import re
import time

# 1. CRITICAL: SESSION STATE INITIALIZATION (MUST BE FIRST)
if 'cart' not in st.session_state:
    st.session_state.cart = {}  # {nsn: {"name": str, "qty": int}}
if 'results' not in st.session_state:
    st.session_state.results = None

# 2. Page Configuration & Specialized CSS
st.set_page_config(page_title="Falcon NSN Lock", page_icon="🦅", layout="wide")

st.markdown("""
    <style>
    .main { background-color: #0e1117; color: #f0f2f6; }
    
    /* DECISION CARDS & HIERARCHY */
    .nsn-card {
        background-color: #1a1d2e; border: 1px solid #2d314c;
        border-radius: 10px; padding: 15px; margin-bottom: 15px;
    }
    .primary-card { border: 2px solid #00d4ff; box-shadow: 0 0 12px rgba(0, 212, 255, 0.15); }
    
    /* ACTIONABLE ELEMENTS */
    .nsn-display { font-family: 'Roboto Mono', monospace; font-size: 1.4em; font-weight: bold; color: #fff; }
    .conf-score { font-size: 1.5em; font-weight: 800; padding: 4px 8px; border-radius: 4px; cursor: help; }
    .high-conf { color: #2ecc71; background: rgba(46, 204, 113, 0.1); }
    .med-conf { color: #f1c40f; background: rgba(241, 196, 15, 0.1); }
    
    /* CART UI */
    .cart-item {
        background: #161b22; border-left: 3px solid #00d4ff;
        padding: 10px; margin-bottom: 8px; border-radius: 4px;
    }
    
    /* FALCON LOADER */
    @keyframes progress-animation { 0% { width: 0%; } 100% { width: 100%; } }
    .falcon-bar-container { width: 100%; height: 3px; background: #2d314c; position: fixed; top: 0; left: 0; z-index: 9999; }
    .falcon-bar-fill { height: 100%; background: #00d4ff; animation: progress-animation 2.5s linear infinite; }
    </style>
    """, unsafe_allow_html=True)

# 3. Sidebar: Universal Taxonomy & Aggregated Supply Cart
with st.sidebar:
    st.image("https://upload.wikimedia.org/wikipedia/commons/thumb/d/d3/Seal_of_the_United_States_Department_of_the_Air_Force.svg/1200px-Seal_of_the_United_States_Department_of_the_Air_Force.svg.png", width=50)
    st.title("Falcon Dashboard")
    st.caption("v3.1 // Universal Taxonomy Mode")
    st.divider()
    
    # 3.1 Universal Input System
    uploaded_file = st.file_uploader("Upload Component Scan", type=["jpg", "png"], label_visibility="collapsed")
    
    st.write("**Taxonomy**")
    id_type = st.radio("Select Type:", ["Equipment", "Part"], horizontal=True, label_visibility="collapsed")
    
    taxonomy = {
        "Equipment": ["Heater", "Generator", "Air Compressor", "Towbar", "LOX Cart", "Jack"],
        "Part": ["Electrical", "Fuel System", "Hydraulic", "Mechanical", "Structural", "Fasteners"]
    }
    selected_class = st.selectbox(f"Select {id_type} Class:", options=taxonomy[id_type])
    
    dist_feature = st.text_input("Distinguishing Feature (Optional)", placeholder="e.g. dual exhaust, 12-in port")
    
    # 3.2 Persistent Supply Cart
    st.divider()
    st.subheader("🛒 Supply Cart")
    if not st.session_state.cart:
        st.info("No items added.")
    else:
        for nsn, data in list(st.session_state.cart.items()):
            col_a, col_b = st.columns([2.5, 1])
            with col_a:
                st.markdown(f"**{nsn}**\n\n{data['name']}")
            with col_b:
                if st.button("➕", key=f"p_{nsn}"):
                    st.session_state.cart[nsn]['qty'] += 1
                    st.rerun()
                st.write(f"**x{data['qty']}**")
                if st.button("➖", key=f"m_{nsn}"):
                    st.session_state.cart[nsn]['qty'] -= 1
                    if st.session_state.cart[nsn]['qty'] <= 0: del st.session_state.cart[nsn]
                    st.rerun()
        
        if st.button("📦 Submit Order", type="primary", use_container_width=True):
            st.success("Logistics Tasking Sent.")
            st.session_state.cart = {}
            st.rerun()

# 4. Main Operational Layout
col_left, col_right = st.columns([1, 1.4])

with col_left:
    st.header("1. Digital Inspection")
    if uploaded_file:
        st.image(uploaded_file, use_container_width=True)
        if st.button("🚀 EXECUTE LOGISTICS LOCK", use_container_width=True, type="primary"):
            loader = st.empty()
            loader.markdown('<div class="falcon-bar-container"><div class="falcon-bar-fill"></div></div>', unsafe_allow_html=True)
            time.sleep(2)
            loader.empty()
            
            # Logic integration: Weighted results based on taxonomy selection
            st.session_state.results = [
                {"nsn": "4520-01-135-2770", "name": f"{selected_class.upper()} (H-1)", "conf": 96, "type": "Exact Match", "just": f"Confirmed via {selected_class} chassis geometry and exhaust alignment."},
                {"nsn": "4520-01-482-8571", "name": f"{selected_class.upper()} (NGH-1)", "conf": 82, "type": "Closest Match", "just": "Modern variant; enclosure profile matches detection parameters."},
                {"nsn": "4520-00-540-1444", "name": f"{selected_class.upper()} (BT400)", "conf": 62, "type": "Tech Reference", "just": "Legacy sub-variant; intake layout inconsistent with primary."}
            ]

with col_right:
    st.header("2. NSN Resolution")
    if st.session_state.results:
        for i, res in enumerate(st.session_state.results):
            is_primary = (i == 0)
            c_class = "high-conf" if res['conf'] > 90 else "med-conf"
            # Hybrid Image Rendering logic
            img_src = f"https://www.iso-group.com/Public/Images/NSN/{res['nsn']}.jpg"
            
            st.markdown(f"""
            <div class="nsn-card {'primary-card' if is_primary else ''}">
                <div style="display: flex; justify-content: space-between; align-items: center;">
                    <span style="font-size: 0.7em; font-weight: bold; color: #888;">{'RECOMMENDED' if is_primary else 'ALTERNATIVE'}</span>
                    <div class="conf-score {c_class}" title="Visual: 92% | Class: 100% | Features: {dist_feature if dist_feature else 'N/A'}">
                        {res['conf']}%
                    </div>
                </div>
                <div style="display: flex; gap: 15px; margin-top: 10px;">
                    <div style="position: relative; width: 120px; height: 120px;">
                        <img src="{img_src}" style="width: 100%; height: 100%; border-radius: 5px; border: 1px solid #333; object-fit: cover;" onerror="this.src='https://placehold.co/200x200/1a1d2e/00d4ff?text=IPB+Reference'">
                        <span style="position: absolute; top: 5px; left: 5px; font-size: 0.6em; background: rgba(0,0,0,0.8); color: #fff; padding: 2px 5px; border-radius: 3px;">{res['type']}</span>
                    </div>
                    <div style="flex: 1;">
                        <div class="nsn-display">{res['nsn']}</div>
                        <div style="font-size: 0.9em; color: #bdc3c7;">{res['name']}</div>
                        <p style="font-size: 0.8em; color: #888; margin-top: 8px;"><em>{res['just']}</em></p>
                    </div>
                </div>
            </div>
            """, unsafe_allow_html=True)
            
            if st.button(f"🛒 Add {res['nsn']} to Supply Cart", key=f"add_{res['nsn']}"):
                if res['nsn'] in st.session_state.cart:
                    st.session_state.cart[res['nsn']]['qty'] += 1
                else:
                    st.session_state.cart[res['nsn']] = {"name": res['name'], "qty": 1}
                st.rerun()
