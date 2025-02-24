import streamlit as st

def render_platform_selector():
    if 'platforms' not in st.session_state:
        st.session_state.platforms = {
            "Twitter": False,
            "Linkedin": False,
            "Instagram": False,
            "Blog": False
        }
    
    st.subheader("Select Platforms")
    cols = st.columns(4)
    for i, (platform, value) in enumerate(st.session_state.platforms.items()):
        with cols[i]:
            st.session_state.platforms[platform] = st.checkbox(
                platform,
                value=value,
                key=f"platform_{platform}"
            )
    
    return [p for p, v in st.session_state.platforms.items() if v]