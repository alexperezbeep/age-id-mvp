import streamlit as st
from google import genai
from google.genai import types
from PIL import Image
import re
import time

# 1. Page Configuration & Optimized CSS
st.set_page_config(page_title="Falcon NSN Lock", page_icon="🦅", layout="wide")

# Persistent State Management
if 'cart' not in st.session_state:
    st.session_state.cart = {}  # Format: {nsn: {"name": str, "qty": int}}
if 'results' not in st.session_state:
    st.session_state.results = None

st.markdown("""
    <style>
    .main { background-color: #0e1117; color: #f0f2f6; }
    
    /* QUANTITY AGGREGATION STYLING */
    .cart-item-row {
        background: #161b22; border-left: 3px solid #00d4ff;
        padding: 10px; margin-bottom: 8px; border-radius: 4px;
        display: flex; justify-content: space-between; align-items: center;
    }
    
    /* CONFIDENCE BREAKDOWN */
    .conf-score {
        font-size: 1.5em; font-weight: 800; cursor: help;
        padding: 4px 8px; border-radius: 4px;
    }
    .high-conf { color: #2ecc71; background: rgba(46, 204, 113, 0.1); }
    .med-conf { color: #f1c40f; background: rgba(241, 196, 15, 0.1); }
    
    /* IMAGE RENDERING LAYER */
    .img-label {
        position: absolute; top: 5px; left: 5px;
        font-size: 0.6em; background: rgba(0,0,0,0.7);
        color: #fff; padding: 2px 5px; border-radius: 3px;
    }
    .nsn-card {
        background-color: #1a1d2e; border: 1px solid #2d314c;
        border-radius: 10px; padding: 15px; margin-bottom: 15px;
    }
    </style>
    """, unsafe_allow_html=True)

# 2. Sidebar: Aggregated Supply Cart
with st.sidebar:
    st.image("https://upload.wikimedia.org/wikipedia/commons/thumb/d/d3/Seal_of_the_United_States_Department_of_the_Air_Force.svg/1200px-Seal_of_the_United_States_Department_of_the_Air_Force.svg.png", width=50)
    st.title("Falcon Dashboard")
    st.divider()
    
    st.subheader("🛒 Supply Cart")
    if not st.session_state.cart:
        st.caption("No items added.")
    else:
        for nsn, data in list(st.session_state.cart.items()):
            col_a, col_b = st.columns([3, 1])
            with col_a:
                st.markdown(f"**{nsn}** \n{data['name']}")
            with col_b:
                # Quantity Controls
                q_col1, q_col2 = st.columns(2)
                if q_col1.button("−", key=f"min_{nsn}"):
                    st.session_state.cart[nsn]['qty'] -= 1
                    if st.session_state.cart[nsn]['qty'] <= 0:
                        del st.session_state.cart[nsn]
                    st.rerun()
                st.write(f"x{data['qty']}")
        
        if st.button("📦 Submit Order", type="primary", use_container_width=True):
            st.success("Logistics Tasking Sent.")
            st.session_state.cart = {}
            st.rerun()

# 3. Decision Logic & Identification
c1, c2 = st.columns([1, 1.4])

with c1:
    st.header("1. Digital Inspection")
    uploaded_file = st.file_uploader("Upload Scan", type=["jpg", "png"], label_visibility="collapsed")
    if uploaded_file:
        st.image(uploaded_file, use_container_width=True)
        if st.button("🚀 EXECUTE LOGISTICS LOCK", use_container_width=True):
            # Loader State
            progress = st.progress(0)
            for i in range(100):
                time.sleep(0.01)
                progress.progress(i + 1)
            
            # Tier-Driven Identification
            st.session_state.results = [
                {
                    "nsn": "4520-01-135-2770", "name": "HEATER, GROUND SUPPORT (H-1)", 
                    "conf": 96, "img_type": "Exact Match",
                    "just": "High confidence due to vertical exhaust stacks and intake geometry."
                },
                {
                    "nsn": "4520-01-482-8571", "name": "NEW GENERATION HEATER (NGH-1)", 
                    "conf": 82, "img_type": "Closest Match",
                    "just": "Alternative profile; frame dimensions align but enclosure differs."
                },
                {
                    "nsn": "4520-99-AI-GEN", "name": "PROTOTYPE THERMAL UNIT", 
                    "conf": 45, "img_type": "AI-Generated Reference",
                    "just": "Synthetic match based on thermal duct diameter and chassis scale."
                }
            ]

with c2:
    st.header("2. NSN Resolution")
    if st.session_state.results:
        for res in st.session_state.results:
            with st.container():
                # Hybrid Image Rendering logic
                # For demo: placeholders represent the 4-tier system
                img_src = f"https://www.iso-group.com/Public/Images/NSN/{res['nsn']}.jpg"
                if "AI-GEN" in res['nsn']:
                    img_src = "https://placehold.co/200x200/1a1d2e/00d4ff?text=AI+Reference"

                st.markdown(f"""
                <div class="nsn-card">
                    <div style="display: flex; justify-content: space-between; align-items: center;">
                        <span style="font-family: monospace; font-size: 1.2em; font-weight: bold;">NSN: {res['nsn']}</span>
                        <div class="conf-score {'high-conf' if res['conf'] > 90 else 'med-conf'}" title="Breakdown: Visual: 90% | Class: 95% | Inventory: 100%">
                            {res['conf']}%
                        </div>
                    </div>
                    <div style="display: flex; gap: 15px; margin-top: 10px;">
                        <div style="position: relative;">
                            <img src="{img_src}" style="width: 120px; border-radius: 5px; border: 1px solid #333;">
                            <span class="img-label">{res['img_type']}</span>
                        </div>
                        <div>
                            <p style="margin:0; font-weight: bold;">{res['name']}</p>
                            <p style="font-size: 0.85em; color: #888; margin-top: 5px;">{res['just']}</p>
                        </div>
                    </div>
                </div>
                """, unsafe_allow_html=True)
                
                if st.button(f"🛒 Add to Supply Cart", key=f"add_{res['nsn']}"):
                    if res['nsn'] in st.session_state.cart:
                        st.session_state.cart[res['nsn']]['qty'] += 1
                    else:
                        st.session_state.cart[res['nsn']] = {"name": res['name'], "qty": 1}
                    st.rerun()
