import streamlit as st
from PIL import Image
import time

# 1. INITIALIZE SESSION STATE (RESILIENT)
if 'cart' not in st.session_state:
    st.session_state.cart = {}
if 'results' not in st.session_state:
    st.session_state.results = []

# 2. Page Configuration & Improved CSS
st.set_page_config(page_title="Falcon NSN Lock", page_icon="🦅", layout="wide")

st.markdown("""
    <style>
    .main { background-color: #0e1117; color: #f0f2f6; }
    .nsn-card {
        background-color: #1a1d2e; border: 1px solid #2d314c;
        border-radius: 10px; padding: 15px; margin-bottom: 15px;
    }
    .primary-card { border: 2px solid #00d4ff; box-shadow: 0 0 10px rgba(0, 212, 255, 0.15); }
    .conf-score { font-size: 1.5em; font-weight: 800; padding: 4px 8px; border-radius: 4px; }
    .high-conf { color: #2ecc71; background: rgba(46, 204, 113, 0.1); }
    .img-label {
        position: absolute; top: 5px; left: 5px; font-size: 0.6em; 
        background: rgba(0,0,0,0.8); color: #fff; padding: 2px 5px; border-radius: 3px;
    }
    </style>
    """, unsafe_allow_html=True)

# 3. Sidebar: Mission Input & Aggregated Cart
with st.sidebar:
    st.title("Falcon Dashboard")
    st.divider()
    
    uploaded_file = st.file_uploader("Upload Scan", type=["jpg", "png"], label_visibility="collapsed")
    
    # Hierarchical Selection
    st.write("**Taxonomy Selection**")
    id_type = st.radio("Type:", ["Equipment", "Part"], horizontal=True, label_visibility="collapsed")
    taxonomy = {
        "Equipment": ["Heater", "Generator", "Air Compressor", "Towbar", "LOX Cart"],
        "Part": ["Electrical", "Fuel System", "Hydraulic", "Mechanical", "Structural"]
    }
    selected_class = st.selectbox(f"Select {id_type} Class:", options=taxonomy[id_type])
    dist_feature = st.text_input("Distinguishing Feature (Optional)", placeholder="e.g. dual exhaust")
    
    st.divider()
    st.subheader("🛒 Supply Cart")
    if not st.session_state.cart:
        st.caption("No items added.")
    else:
        for nsn, data in list(st.session_state.cart.items()):
            c1, c2 = st.columns([3, 1])
            with c1: st.write(f"**{nsn}**\n{data['name']}")
            with c2: 
                st.write(f"x{data['qty']}")
                if st.button("➖", key=f"del_{nsn}"):
                    st.session_state.cart[nsn]['qty'] -= 1
                    if st.session_state.cart[nsn]['qty'] <= 0: del st.session_state.cart[nsn]
                    st.rerun()
        
        if st.button("📦 Submit Order", type="primary", use_container_width=True):
            st.success("Logistics Tasking Sent.")
            st.session_state.cart = {}
            st.rerun()

# 4. Main Operational Layout
col_insp, col_res = st.columns([1, 1.4])

with col_insp:
    st.header("1. Digital Inspection")
    if uploaded_file:
        st.image(uploaded_file, use_container_width=True)
        if st.button("🚀 EXECUTE LOGISTICS LOCK", use_container_width=True, type="primary"):
            with st.spinner("Analyzing Visual Anchors..."):
                time.sleep(1.5)
            # SAFE DATA GENERATION: Every dict contains a 'type' key
            st.session_state.results = [
                {"nsn": "4520-01-135-2770", "name": f"{selected_class} (H-1)", "conf": 96, "type": "Exact Match"},
                {"nsn": "4520-01-482-8571", "name": f"{selected_class} (NGH-1)", "conf": 82, "type": "Closest Match"},
                {"nsn": "4520-00-540-1444", "name": f"{selected_class} (BT400)", "conf": 62, "type": "Reference"}
            ]
            st.rerun()

with col_res:
    st.header("2. NSN Resolution")
    if st.session_state.results:
        for i, res in enumerate(st.session_state.results):
            is_p = (i == 0)
            # THE FIX: use .get() to avoid KeyError if the key is missing
            img_label = res.get('type', 'Reference') 
            img_url = f"https://www.iso-group.com/Public/Images/NSN/{res['nsn']}.jpg"
            
            st.markdown(f"""
            <div class="nsn-card {'primary-card' if is_p else ''}">
                <div style="display: flex; justify-content: space-between; align-items: center;">
                    <span style="font-family: monospace; font-weight: bold;">NSN: {res['nsn']}</span>
                    <div class="conf-score high-conf">{res['conf']}%</div>
                </div>
                <div style="display: flex; gap: 15px; margin-top: 10px;">
                    <div style="position: relative; width: 100px; height: 100px;">
                        <img src="{img_url}" style="width: 100%; height: 100%; object-fit: cover; border-radius: 5px;" onerror="this.src='https://placehold.co/200x200/1a1d2e/00d4ff?text=IPB'">
                        <span class="img-label">{img_label}</span>
                    </div>
                    <div>
                        <div style="font-weight: bold;">{res['name']}</div>
                        <div style="font-size: 0.8em; color: #888;">Logistics Match Confirmed via Visual Anchors.</div>
                    </div>
                </div>
            </div>
            """, unsafe_allow_html=True)
            
            if st.button(f"🛒 Add to Supply Cart", key=f"btn_{res['nsn']}"):
                if res['nsn'] in st.session_state.cart:
                    st.session_state.cart[res['nsn']]['qty'] += 1
                else:
                    st.session_state.cart[res['nsn']] = {"name": res['name'], "qty": 1}
                st.rerun()
    else:
        st.info("Awaiting scan analysis...")
