import streamlit as st

def render_content_display(content: str):
    st.subheader("Generated Content")
    content_sections = content.split("\n\n")
    
    for section in content_sections:
        if section.strip():
            with st.expander("Platform Content", expanded=True):
                st.text_area(
                    "",
                    value=section,
                    height=150,
                    key=f"content_{hash(section)}"
                )
                if st.button("Copy", key=f"copy_{hash(section)}"):
                    st.write("Content copied to clipboard!")