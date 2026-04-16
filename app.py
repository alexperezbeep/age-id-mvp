import streamlit as st
import time

# 1. Clear state at startup if needed, but initialize correctly
if 'results' not in st.session_state:
    st.session_state.results = []

# --- SIDEBAR (Logic for Equipment/Part/Unknown) ---
with st.sidebar:
    st.title("Falcon Dashboard")
    uploaded_file = st.file_uploader("Upload Image", type=['png', 'jpg'])
    mode = st.radio("Mode", ["Equipment", "Part", "Unknown / Not Sure"], index=0)
    
    # Categories based on Mode
    if mode == "Equipment":
        cats = ["Power Gen", "HVAC", "Hydraulic Stands"]
    else:
        cats = ["Hydraulic", "Electrical", "Structural"]
    
    selection = st.selectbox("Select Class", cats)
    feature = st.text_input("Distinguishing Feature", value="bulky")

# --- MAIN PANEL ---
col1, col2 = st.columns([1, 1])

with col1:
    st.header("1. Digital Inspection")
    if uploaded_file:
        st.image(uploaded_file, use_column_width=True)
    
    # THE TRIGGER
    if st.button("🚀 EXECUTE LOGISTICS LOCK", type="primary", use_container_width=True):
        with st.spinner("Processing Logistics..."):
            time.sleep(1) # Simulated delay
            
            # THE FIX: Logic that actually changes the data based on your inputs
            if mode == "Equipment" and "bulky" in feature:
                # Mocking 10 results for the Generator
                new_data = []
                for i in range(1, 11):
                    new_data.append({
                        "nsn": f"6115-01-512-100{i}",
                        "pn": f"GEN-TX-{500 + i}",
                        "name": "Generator Set, Diesel Engine",
                        "conf": f"{99 - i}%"
                    })
                st.session_state.results = new_data
            else:
                # Default/Fallback
                st.session_state.results = [{"nsn": "0000", "pn": "N/A", "name": "No Match", "conf": "0%"}]
        st.rerun()

with col2:
    st.header("2. NSN Resolution")
    
    if st.session_state.results:
        st.subheader("Top Matches")
        # Top 3
        for item in st.session_state.results[:3]:
            with st.container(border=True):
                c1, c2 = st.columns([3, 1])
                c1.write(f"**NSN: {item['nsn']}**\n\n**PN: {item['pn']}**")
                c1.caption(f"Identity: {item['name']}")
                c2.subheader(f":green[{item['conf']}]")
                st.button("Add to Supply Cart", key=f"top_{item['nsn']}")
        
        # Backlog (7-10 items)
        with st.expander("View Additional Potential Matches (Backlog)"):
            for item in st.session_state.results[3:10]:
                st.write(f"**{item['nsn']}** | PN: {item['pn']} — {item['conf']}")
                st.button("Add", key=f"back_{item['nsn']}")
    else:
        st.info("Awaiting execution...")
