import streamlit as st
import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "../..")))
from app.config import ettings
from app.Langgra.graph import graph
from app.UI.components.sidebar import render_sidebar
from app.UI.components.platform_selector import render_platform_selector
from app.UI.components.input_section import render_input_section
from app.UI.components.content_display import render_content_display
import getpass

def _set_env(name:str):
    if not os.getenv(name):
        os.environ[name] = getpass.getpass(f"{name}:")
    


def main():
    _set_env("OPENAI_API_KEY")

    _set_env("TAVILY_API_KEY")
    st.set_page_config(
        page_title=ettings.PROJECT_NAME,
        layout="wide",
        initial_sidebar_state="expanded"
    )

    # Load custom CSS
    with open("app/ui/styles/main.css") as f:
        st.markdown(f"<style>{f.read()}</style>", unsafe_allow_html=True)

    # Title and Description
    st.title(ettings.PROJECT_NAME)
    st.markdown("Transform your text into platform-optimized content across multiple social media channels")

    # Render sidebar
    render_sidebar()

    # Input Section
    input_text = render_input_section()

    # Platform Selection
    selected_platforms = render_platform_selector()

    # Generate Button
    if st.button("Generate Content", 
                 disabled=not (input_text and selected_platforms),
                 key="generate_button"):
        
        with st.spinner("Generating content..."):
            try:
                # Direct call to LangGraph
                result = graph.invoke({
                    "text": input_text,
                    "platforms": selected_platforms
                })
                
                render_content_display(result["generated_content"])

            except Exception as e:
                st.error(f"Error generating content: {str(e)}")

if __name__ == "__main__":
    main()