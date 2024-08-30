import streamlit as st

def infopage():
    st.markdown("""
        <h1 style="color:#9b51e0;">
            Background information page
        </h1>
    """, unsafe_allow_html=True)
    left, right = st.columns([8, 2])
    with left:
        st.write("<style>div.block-container{padding-top:2rem;}</style>", unsafe_allow_html=True)
    with right:
        st.button("Sales bot", on_click=lambda: st.session_state.update(page="salesbot"))
