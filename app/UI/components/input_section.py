import streamlit as st

def render_input_section():
    st.subheader("Input Text")
    input_text = st.text_area(
        "Enter your text here...",
        height=200,
        key="input_text"
    )
    return input_text