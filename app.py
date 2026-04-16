import streamlit as st
from google import genai
from google.genai import types
from PIL import Image
import re
import time

# 1. Page Configuration & Integrated CSS
st.set_page_config(page_title="Falcon NSN Lock & Supply", page_icon="🦅", layout="wide")

# Initialize Session State for Cart and Results to prevent data loss on re-run
if 'cart' not in st.session_state:
    st.session_state.cart = []
if 'last_results' not in st.session_state:
    st.session_state.last_results = None

st.markdown("""
    <style>
    .main { background-color: #0e1117; color: #f0f2f6; }
    .decision-card {
        background-color: #1a1d2e; border-radius: 8px; 
        padding: 15px; margin-bottom: 12px; border: 1px solid #2d314c;
    }
    .primary-card { border: 2px solid #00d4ff; box-shadow: 0 0 10px rgba(0, 212, 255, 0.1); }
    .nsn-display { font-family: 'Roboto Mono', monospace; font-size: 1.4em; font-weight: bold; color: #fff; }
    .cart-item {
        background: #0d1117; border-left: 3px solid #00d4ff;
        padding: 8px; margin-bottom: 8px; border-radius: 4px; font-size: 0.85em;
    }
    /* Falcon Top Loader */
    @keyframes progress-animation { 0% { width: 0%; } 100% { width: 100%; } }
    .falcon-bar-container { width: 100%; height: 3px; background: #2d314c; position: fixed; top: 0; left: 0; z-index: 9999; }
    .falcon-bar-fill { height: 100%; background: #00d4ff; animation: progress-animation 2.5s linear infinite; }
    </style>
    """, unsafe_allow_html=True)

# 2. Sidebar: Mission Input & Persistent Supply Cart
with st.sidebar:
    st.image("https://upload.wikimedia.org/wikipedia/commons/thumb/d/d3/Seal_of_the_United_States_Department_of_the_Air_Force.svg/1200px-Seal_of_the_United_States_Department_of_the_Air_Force.svg.png", width=50)
    st.title("Falcon Dashboard")
    st.divider()
    
    eq_class = st.selectbox("Select Equipment Class:", ["Select...", "Generator", "Heater", "Compressor", "Towbar"])
    uploaded_file = st.file_uploader("Upload Scan", type=["jpg", "png"], label_visibility="collapsed")
    
    st.divider()
    st.subheader("🛒 Supply Cart")
    
    if not st.session_state.cart:
        st.info("Cart is empty.")
    else:
        for idx, item in enumerate(st.session_state.cart):
            st.markdown(f"""<div class="cart-item"><strong>{item['nsn']}</strong><br>{item['name']}</div>""", unsafe_allow_html=True)
        if st.button("📦 Submit Order to Production", type="primary", use_container_width=True):
            st.success("Order Submitted.")
            st.session_state.cart = [] # Clear after submission

# 3. Main Operational Layout
col_left, col_right = st.columns([1, 1.4])

with col_left:
    st.header("1. Digital Inspection")
    if uploaded_file:
        img = Image.open(uploaded_file)
        st.image(img, use_container_width=True)
        if st.button("🚀 Lock NSN & Proceed", use_container_width=True, type="primary"):
            # Trigger Loader
            loader = st.empty()
            for state in ["Matching NSNs...", "Verifying Stock Status..."]:
                loader.markdown(f'<div class="falcon-bar-container"><div class="falcon-bar-fill"></div></div><p style="color:#00d4ff; text-align:center;">{state}</p>', unsafe_allow_html=True)
                time.sleep(1)
            loader.empty()
            
            # Simulated AI Extraction for Top 3 NSNs
            st.session_state.last_results = [
                {"nsn": "4520-01-135-2770", "name": "HEATER, GROUND SUPPORT (H-1)", "conf": 96},
                {"nsn": "4520-01-482-8571", "name": "NEW GENERATION HEATER (NGH-1)", "conf": 84},
                {"nsn": "4520-00-540-1444", "name": "HEATER, DUCT TYPE (BT400)", "conf": 62}
            ]

with col_right:
    st.header("2. Logistics Audit Trail")
    if st.session_state.last_results:
        st.subheader("Top 3 NSN Matches")
        for i, res in enumerate(st.session_state.last_results):
            is_primary = (i == 0)
            card_type = "primary-card" if is_primary else ""
            # Ensure images pull from reputable tech diagram host
            img_url = f"https://www.iso-group.com/Public/Images/NSN/{res['nsn']}.jpg"
            
            st.markdown(f"""
            <div class="decision-card {card_type}">
                <div style="display: flex; justify-content: space-between; font-size: 0.7em; color: #888;">
                    <span>{'RECOMMENDED' if is_primary else 'ALTERNATIVE'}</span>
                    <span style="color: #2ecc71;">{res['conf']}% MATCH</span>
                </div>
                <div style="display: flex; gap: 15px; margin-top: 10px;">
                    <img src="{img_url}" style="width: 100px; height: 100px; border-radius: 4px; border: 1px solid #333; object-fit: cover;">
                    <div>
                        <div class="nsn-display">{res['nsn']}</div>
                        <div style="font-size: 0.85em; color: #bdc3c7;">{res['name']}</div>
                    </div>
                </div>
            </div>
            """, unsafe_allow_html=True)
            
            # Action Buttons
            if st.button(f"🛒 Add {res['nsn']} to Supply Cart", key=f"btn_{res['nsn']}"):
                st.session_state.cart.append(res)
                st.toast(f"Added {res['nsn']} to Cart")
                st.rerun() # Forces the sidebar to update immediately
