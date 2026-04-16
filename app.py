import streamlit as st
import time

# --- INITIALIZATION ---
if 'resolved_results' not in st.session_state:
    st.session_state.resolved_results = []

# --- SIDEBAR & DIGITAL INSPECTION ---
# (Keep your existing sidebar logic here...)

with col2:
    st.header("2. NSN Resolution")
    
    if not st.session_state.resolved_results:
        st.info("Execute Logistics Lock to see results.")
    else:
        # 1. TOP 3 CHOICES
        st.subheader("Top Matches")
        top_3 = st.session_state.resolved_results[:3]
        backlog = st.session_state.resolved_results[3:13] # Next 7-10 items

        for item in top_3:
            with st.container(border=True):
                c1, c2 = st.columns([3, 1])
                with c1:
                    st.write(f"**NSN: {item['nsn']}**")
                    # Returning Part Number if available
                    if item.get('pn'):
                        st.write(f"**PN: {item['pn']}**")
                    st.caption(f"Identity: {item['name']}")
                with c2:
                    st.subheader(f":green[{item['conf']}]")
                
                st.button("Add to Supply Cart", key=f"top_{item['nsn']}")

        st.divider()

        # 2. BACKLOG DROPDOWN (7-10 Items)
        if backlog:
            with st.expander("View Additional Potential Matches (Backlog)"):
                for item in backlog:
                    inner_c1, inner_c2 = st.columns([4, 1])
                    pn_str = f" | PN: {item['pn']}" if item.get('pn') else ""
                    inner_c1.write(f"**{item['nsn']}**{pn_str} — {item['name']}")
                    inner_c2.write(f"**{item['conf']}**")
                    if st.button("Add", key=f"back_{item['nsn']}"):
                        st.session_state.cart.append(item['nsn'])
