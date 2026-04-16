import streamlit as st
from google import genai
from google.genai import types
from PIL import Image
import re
import time

# 1. CRITICAL: INITIALIZE SESSION STATE FIRST
# This must happen before any sidebar or main layout code runs.
if 'cart' not in st.session_state:
    st.session_state.cart = {}  # Using a dict for quantity aggregation
if 'results' not in st.session_state:
    st.session_state.results = None

# 2. Page Configuration & Optimized CSS
st.set_page_config(page_title="Falcon NSN Lock", page_icon="🦅", layout="wide")

st.markdown("""
    <style>
    .main { background-color: #0e1117; color: #f0f2f6; }
    .decision-card {
        background-color: #1a1d2e; border: 1px solid #2d314c;
        border-radius: 10px; padding: 15px; margin-bottom: 15px;
    }
    .conf-score { font-size: 1.5em; font-weight: 800; padding: 4px 8px; border-radius: 4px; }
    .high-conf { color: #2ecc71; background: rgba(46, 204, 113, 0.1); }
    .med-conf { color: #f1c40f; background: rgba(241, 196, 15, 0.1); }
    .img-label {
        position: absolute; top: 5px; left: 5px; font-size: 0.6em; 
        background: rgba(0,0,0,0.8); color: #fff; padding: 2px 5px; border-radius: 3px;
    }
    /* Falcon Top Loader */
    @keyframes progress-animation { 0% { width: 0%; } 100% { width: 100%; } }
    .falcon-bar-container { width: 100%; height: 3px; background: #2d314c; position: fixed; top: 0; left: 0; z-index: 9999; }
    .falcon-bar-fill { height: 100%; background: #00d4ff; animation: progress-animation 2.5s linear infinite; }
    </style>
    """, unsafe_allow_html=True)

# 3. Sidebar: Aggregated Supply Cart
with st.sidebar:
    st.image("https://upload.wikimedia.org/wikipedia/commons/thumb/d/d3/Seal_of_the_United_States_Department_of_the_Air_Force.svg/1200px-Seal_of_the_United_States_Department_of_the_Air_Force.svg.png", width=50)
    st.title("Falcon Dashboard")
    st.divider()
    
    st.subheader("🛒 Supply Cart")
    
    # Safe iteration using session_state
    if not st.session_state.cart:
        st.caption("No items added.")
    else:
        # We use list() to prevent "dictionary changed size during iteration" errors
        for nsn, data in list(st.session_state.cart.items()):
            c_a, c_b = st.columns([2.5, 1])
            with c_a:
                st.markdown(f"**{nsn}**\n\n{data['name']}")
            with c_b:
                # Standardized Quantity Controls
                if st.button("➕", key=f"plus_{nsn}"):
                    st.session_state.cart[nsn]['qty'] += 1
                    st.rerun()
                st.write(f"**x{data['qty']}**")
                if st.button("➖", key=f"minus_{nsn}"):
                    st.session_state.cart[nsn]['qty'] -= 1
                    if st.session_state.cart[nsn]['qty'] <= 0:
                        del st.session_state.cart[nsn]
                    st.rerun()
        
        st.divider()
        if st.button("📦 Submit Order to Production", type="primary", use_container_width=True):
            st.success("Logistics Tasking Sent.")
            st.session_state.cart = {}
            st.rerun()

# 4. Identification & Decision Logic
col_left, col_right = st.columns([1, 1.4])

with col_left:
    st.header("1. Digital Inspection")
    uploaded_file = st.file_uploader("Upload Scan", type=["jpg", "png"], label_visibility="collapsed")
    if uploaded_file:
        st.image(uploaded_file, use_container_width=True)
        if st.button("🚀 EXECUTE LOGISTICS LOCK", use_container_width=True):
            # Loader State
            loader = st.empty()
            loader.markdown('<div class="falcon-bar-container"><div class="falcon-bar-fill"></div></div>', unsafe_allow_html=True)
            time.sleep(2)
            loader.empty()
            
            # Tiered Results (Simulation of your AI Logic)
            st.session_state.results = [
                {
                    "nsn": "4520-01-135-2770", "name": "HEATER, GROUND SUPPORT (H-1)", 
                    "conf": 96, "img_type": "Exact Match",
                    "just": "High confidence due to vertical exhaust stacks and intake geometry consistent with H-1."
                },
                {
                    "nsn": "4520-01-482-8571", "name": "NEW GENERATION HEATER (NGH-1)", 
                    "conf": 82, "img_type": "Closest Match",
                    "just": "Frame dimensions align but enclosure profile suggests modern replacement."
                },
                {
                    "nsn": "4520-00-540-1444", "name": "HEATER, DUCT TYPE (BT400)", 
                    "conf": 62, "img_type": "Technical Reference",
                    "just": "Similar 12-inch discharge port; rejected primary due to intake layout."
                }
            ]

with col_right:
    st.header("2. NSN Resolution")
    if st.session_state.results:
        for res in st.session_state.results:
            # Fallback Image Logic
            img_src = f"https://www.iso-group.com/Public/Images/NSN/{res['nsn']}.jpg"
            
            st.markdown(f"""
            <div class="nsn-card">
                <div style="display: flex; justify-content: space-between; align-items: center;">
                    <span style="font-family: monospace; font-size: 1.2em; font-weight: bold;">NSN: {res['nsn']}</span>
                    <div class="conf-score {'high-conf' if res['conf'] > 90 else 'med-conf'}">
                        {res['conf']}%
                    </div>
                </div>
                <div style="display: flex; gap: 15px; margin-top: 10px;">
                    <div style="position: relative; width: 120px; height: 120px;">
                        <img src="{img_src}" style="width: 100%; height: 100%; border-radius: 5px; border: 1px solid #333; object-fit: cover;" onerror="this.src='https://placehold.co/200x200/1a1d2e/00d4ff?text=IPB+Unavailable'">
                        <span class="img-label">{res['img_type']}</span>
                    </div>
                    <div style="flex: 1;">
                        <p style="margin:0; font-weight: bold;">{res['name']}</p>
                        <p style="font-size: 0.85em; color: #888; margin-top: 5px;"><em>{res['just']}</em></p>
                    </div>
                </div>
            </div>
            """, unsafe_allow_html=True)
            
            # Correct Add-to-Cart Logic with Aggregation
            if st.button(f"🛒 Add {res['nsn']} to Supply Cart", key=f"add_{res['nsn']}"):
                if res['nsn'] in st.session_state.cart:
                    st.session_state.cart[res['nsn']]['qty'] += 1
                else:
                    st.session_state.cart[res['nsn']] = {"name": res['name'], "qty": 1}
                st.toast(f"Updated {res['nsn']} quantity.")
                st.rerun()
