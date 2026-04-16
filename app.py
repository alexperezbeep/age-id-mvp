import streamlit as st
import time
import hashlib

if 'fingerprint' not in st.session_state:
    st.session_state.fingerprint = None
if 'resolved_results' not in st.session_state:
    st.session_state.resolved_results = []
if 'cart' not in st.session_state:
    st.session_state.cart = []

st.set_page_config(page_title="Falcon Dashboard", layout="wide")

with st.sidebar:
    st.title("Falcon Dashboard")
    uploaded_file = st.file_uploader("Upload Image", type=['png', 'jpg', 'jpeg'])

    st.divider()
    mode = st.radio("Mode", ["Equipment", "Part", "Unknown / Not Sure"], index=2)

    class_opts = ["Auto-Detect"] if mode == "Unknown / Not Sure" else ["Hydraulic", "Electrical", "Power Gen"]
    selected_class = st.selectbox("Select Class", class_opts)

    feature = st.text_input("Distinguishing Feature", placeholder="e.g. Pressure Switch")

    # --- REAL FINGERPRINT CHECK ---
    if uploaded_file is not None:
        file_bytes = uploaded_file.getvalue()
        file_hash = hashlib.md5(file_bytes).hexdigest()
    else:
        file_hash = "no_file"

    current_fp = f"{file_hash}|{mode}|{selected_class}|{feature.strip().lower()}"

    if st.session_state.fingerprint != current_fp:
        st.session_state.resolved_results = []
        st.session_state.fingerprint = current_fp

    st.divider()
    st.write(f"### 🛒 Supply Cart ({len(st.session_state.cart)})")
    for item in st.session_state.cart:
        st.caption(f"• {item}")
