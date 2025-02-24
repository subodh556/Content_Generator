import streamlit as st

def render_sidebar():
    st.sidebar.subheader("About")
    st.sidebar.markdown("""
    This content generation tool helps you create optimized content for different social media platforms.
    
    **Features:**
    - Multi-platform support
    - AI-powered content generation
    - Platform-specific optimization
    - Easy copy-paste functionality
    
    **Supported Platforms:**
    - Twitter
    - LinkedIn
    - Instagram
    - Blog
    """)