import streamlit as st
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Set default environment variables if they exist in .env file
if os.getenv("OPENAI_API_KEY"):
    os.environ["OPENAI_API_KEY"] = os.getenv("OPENAI_API_KEY")
if os.getenv("TAVILY_API_KEY"):
    os.environ["TAVILY_API_KEY"] = os.getenv("TAVILY_API_KEY")
if os.getenv("LANGCHAIN_API_KEY"):
    os.environ["LANGCHAIN_API_KEY"] = os.getenv("LANGCHAIN_API_KEY")

user_details = {
  "user_name": "LangGraph Team",
  "business_name": "LangGraph",
  "industry": "AI Tools and Frameworks",
  "business_type": "Tech Startup",
  "target_audience": ["AI Developers", "Machine Learning Enthusiasts", "Enterprise AI Teams"],
  "tone": "Professional",
  "objectives": ["Awareness", "Education"],
  "platforms": ["LinkedIn", "Twitter", "Medium"],
  "preferred_platforms": ["LinkedIn", "Twitter"],
  "platform_specific_details": {
    "twitter_handle": "@LangGraphAI",
    "linkedin_page": "linkedin.com/company/langgraph",
    "medium_page": "medium.com/langgraph"
  },
  "campaigns": [
    {
      "title": "Memory Management Module Launch",
      "date": "2024-05-20",
      "platform": "LinkedIn",
      "success_metric": "1000+ Shares"
    }
  ],
  "popular_hashtags": ["#LangGraph", "#MemoryManagement", "#AIFrameworks"],
  "themes": ["Memory Management", "AI Agent Development"],
  "short_length": 280,
  "long_length": 2000,
  "assets_link": "https://drive.google.com/drive/folders/langgraph-assets",
  "colors": ["#1E88E5", "#FFC107"],
  "brand_keywords": ["Innovative", "Efficient"],
  "restricted_keywords": ["Buggy", "Outdated"],
  "competitors": ["LangChain", "Pinecone"],
  "competitor_metrics": ["Content Shares", "Follower Growth"],
  "posting_schedule": ["Tuesday 10 AM", "Friday 3 PM"],
  "formats": ["Carousel", "Technical Blog"],
  "personal_preferences": "Use technical terms but keep explanations concise."
}

from typing_extensions import TypedDict, List, Literal
from pydantic import BaseModel
from langgraph.graph.message import MessagesState
import operator
from typing import Annotated

Platform = Literal["Twitter","Linkedin","Instagram", "Blog"]


class InputState(TypedDict):
    text : str
    platforms : list[Platform]

class SumamryOutputState(TypedDict):
    text: str
    text_summary: str
    platforms: list[Platform]

class ResearchOutputState(TypedDict):
    text: str
    research: str
    platforms: list[Platform]

class IntentMatchingInputState(TypedDict):
    text: str
    research: str
    platforms: list[Platform]

class FinalState(TypedDict):
    contents: Annotated[list, operator.add]

class GeneratedContent(TypedDict):
    generated_content: str


#Let's Define our Agent Nodes:

from pydantic import BaseModel, Field
from langchain.prompts import ChatPromptTemplate
from langgraph.prebuilt import create_react_agent
from langchain_openai import ChatOpenAI

summ_model = ChatOpenAI(model = "gpt-4o-mini", temperature=0.6)

model = ChatOpenAI(model = "gpt-4o", temperature=0.6)

sumamry_prompt = ChatPromptTemplate.from_template("""
Taks: You need to give a summary of this given text. This summary will help the user to get the idea of the whole text. Do not miss anything important as this summary will take place in Research.

Text:
 {text}

""")

research_agent_prompt = ChatPromptTemplate.from_template("""
You are a member of the Content Generation Team. Your primary task is to research and analyze the provided details to enhance the content creation process.

Here are the client's details:
{user_details}

Below is the summary of the content for which the client wants to generate textual material:
{text_summary}

The client wants to create content for the following platforms:
{platforms}

Your task is to focus on content development enhancements. For each platform, generate onyl 2 questions :

- Suggest best keywords or hashtags relevant to the platform and the content intent.
- Identify key points or themes that should be highlighted or have been emphasized in previous posts.
- Propose possible content elements or formats (e.g., lists, visuals, tone adjustments) tailored to the platform's audience and characteristics.
- .... Anything which is enhances content


Response Format:
[
question1",
 question2",...
]
""")

from langchain_community.tools import TavilySearchResults
from langchain_core.messages import HumanMessage, SystemMessage
from langchain_core.runnables import RunnableConfig


research_tool = TavilySearchResults(
    max_results=2,
    search_depth="advanced",
    include_answer=True,
    include_raw_content=True,
    include_images=True,
)

class ReserachQuestions(TypedDict):
    questions: List[str]

def summary_text(state: InputState) -> SumamryOutputState:
    print("******* Generating summary of the given text *************")
    summary = summ_model.invoke(state["text"]).content
    return {"text": state["text"], "platforms": state["platforms"], "text_summary": summary}

def research_node(state: SumamryOutputState) -> ResearchOutputState:
    print("******* Researching for the best content *************")
    input_ = {"user_details": user_details, "text_summary": state["text_summary"], "platforms": state["platforms"]}
    res = model.with_structured_output(ReserachQuestions, strict=True).invoke(research_agent_prompt.invoke(input_))
    response = research_tool.batch(res["questions"])
    research = ""
    for i,ques in enumerate(res["questions"]):
        research += "question: " + ques + "\n"
        research += "Answers" + "\n\n".join([res["content"] for res in response[i]]) + "\n\n"
    
    return {"text": state["text"], "platforms": state["platforms"], "research": research}

def IntentMatching(state: ResearchOutputState):
    print("******* Sending data to each Platfrom *************")
    # platform_nodes = []
    # for platform in state["platforms"]:
    #     platform_nodes.append(Send(platform, {"text": state["text"],"research": state["research"], "platform": platform}))
    # return platform_nodes
    {"text": state["text"],"research": state["research"], "platforms": state["platforms"]}

instagram_prompt = ChatPromptTemplate.from_template("""
You are a creative social media strategist specializing in Instagram content.  

**Input Details:**  
1. Text: {text}  
2. Research: {research}  

Your task is to create an **Instagram post caption** and provide the following:  
- **Engaging Caption**: Write a compelling caption that aligns with the given text, highlights the key points, and uses an **inspirational or engaging tone** (as per the audience).  
- **Hashtag Suggestions**: Suggest at least 10 hashtags that are **trending and relevant** to the content and target audience.  
- **Call-to-Action (CTA)**: Include a specific action to encourage user engagement (e.g., comment, tag friends, visit website).  
- **Emoji Usage**: Add appropriate emojis to make the caption lively and engaging, without overdoing it.  

**Special Guidelines:**  
1. Keep the caption within 2200 characters but aim for 150–300 characters for better engagement.  
2. Ensure hashtags balance **broad reach (#FitnessGoals)** and **niche relevance (#EcoFitFashion)**.  
3. Optimize for Instagram’s algorithm by starting with a **hook** (e.g., a question or statement).  

**Response Format:**  
Caption: [Your Instagram caption here]  
Hashtags: [#hashtag1, #hashtag2, ...]  
CTA: [Call-to-Action here]  

""")

twitter_prompt = ChatPromptTemplate.from_template("""
You are a social media expert tasked with crafting tweets that drive engagement on Twitter.  

**Input Details:**  
1. Text: {text}  
2. Research: {research}  

Your task is to create **Twitter content** with the following specifications:  
- **Tweet**: Craft a tweet that conveys the essence of the text in **280 characters or less**, ensuring clarity, conciseness, and a conversational tone.  
- **Hashtag Suggestions**: Include up to 3 hashtags that enhance visibility and are platform-specific.  
- **Thread**: If the content cannot fit in a single tweet, create a **thread** with concise, numbered tweets that maintain flow and engagement.  

**Special Guidelines:**  
1. Start with a **strong hook** in the first tweet to grab attention.  
2. Use one or two relevant keywords or phrases identified in the research.  
3. Maintain a balance between **professional** and **relatable** language.  

**Response Format:**  
Tweet: [Your tweet here]  
Hashtags: [#hashtag1, #hashtag2, ...]  
Thread:  
1. [First tweet in the thread]  
2. [Second tweet in the thread]  
...  

""")

linkedin_prompt = ChatPromptTemplate.from_template("""
You are a professional LinkedIn content creator, focused on crafting posts that establish thought leadership and build connections.  

**Input Details:**  
1. Text: {text}  
2. Research: {research}  

Your task is to create a **LinkedIn post** with the following details:  
- **Post Content**: Write a professional, thoughtful post elaborating on the text, tailored to LinkedIn’s audience. Highlight the key takeaways or updates and use a **formal yet engaging tone**.  
- **Hashtags**: Suggest up to 5 hashtags relevant to LinkedIn’s professional audience.  
- **CTA**: Include a CTA encouraging engagement (e.g., “Share your thoughts,” “Let us know how you tackle this,” or “Visit our page for more”).  

**Special Guidelines:**  
1. Aim for **150–300 words**, focusing on storytelling and professional insights.  
2. Structure the post with:  
   - A **hook** to grab attention.  
   - The main body with value-driven insights.  
   - A concluding CTA.  
3. Avoid using jargon unless contextually relevant.  
4. Ensure hashtags are business-focused and professional.  

**Response Format:**  
Post: [Your LinkedIn post here]  
Hashtags: [#hashtag1, #hashtag2, ...]  
CTA: [Call-to-Action here]  

""")

blog_prompt = ChatPromptTemplate.from_template("""
You are a content writer specializing in blogs that captivate readers and provide actionable insights.  

**Input Details:**  
1. Text: {text}  
2. Research: {research}  

Your task is to create a **markdown-formatted blog post** with the following structure:  
- **Title**: Create an eye-catching and SEO-friendly blog title.  
- **Introduction**: Write an engaging opening paragraph that sets the context and hooks the reader.  
- **Main Body**: Elaborate on the text using the research to provide insights, examples, and supporting details. Structure it into sections with headings (H2/H3).  
- **Conclusion**: Summarize key takeaways and include a CTA encouraging readers to take the next step.  

**Special Guidelines:**  
1. Use a tone aligned with the target audience (e.g., casual for general readers, formal for professionals).  
2. Optimize for SEO by incorporating keywords from the research naturally into the content.  
3. Ensure readability by using bullet points, numbered lists, and short paragraphs.  
4. Keep the blog **800–1500 words**.  

**Response Format:**  
```markdown
# [Title of the Blog]  

## Introduction  
[Your introduction here]  

## Section 1: [Heading]  
[Content]  

## Section 2: [Heading]  
[Content]  

## Conclusion  
[Conclusion with CTA]  

""") 

def Insta(state: IntentMatchingInputState) -> FinalState:
    if not "Instagram" in state["platforms"]:
        return {"contents": [""]}
    res = model.invoke(instagram_prompt.invoke({"text": state["text"], "research": state["research"]}))
    return {"contents": [res.content]}

def Twitter(state: IntentMatchingInputState) -> FinalState:
    if not "Twitter" in state["platforms"]:
        return {"contents": [""]}
    res = model.invoke(twitter_prompt.invoke({"text": state["text"], "research": state["research"]}))
    return {"contents": [res.content]}

def Linkedin(state: IntentMatchingInputState) -> FinalState:
    if not "Linkedin" in state["platforms"]:
        return {"contents": [""]}
    res = model.invoke(linkedin_prompt.invoke({"text": state["text"], "research": state["research"]}))
    return { "contents": [res.content]}

def Blog(state: IntentMatchingInputState) -> FinalState:
    if not "Blog" in state["platforms"]:
        return {"contents": [""]}
    res = model.invoke(blog_prompt.invoke({"text": state["text"], "research": state["research"]}))
    return { "contents": [res.content]}

def combining_content(state:FinalState) -> GeneratedContent:
    final_content = ""
    for content in state["contents"]:
        final_content += content + "\n\n"
    return {"generated_content": final_content}



from langgraph.graph import StateGraph, START, END

builder = StateGraph(input=InputState, output=GeneratedContent)

# Nodes
builder.add_node("summary_node",summary_text)
builder.add_node("research_node", research_node)
builder.add_node("intent_matching_node", IntentMatching)
builder.add_node("instagram", Insta)
builder.add_node("twitter", Twitter)
builder.add_node("linkedin", Linkedin)
builder.add_node("blog", Blog)
builder.add_node("combine_content", combining_content)


# Flow
builder.add_edge(START, "summary_node")
builder.add_edge("summary_node", "research_node")
builder.add_edge("research_node", "intent_matching_node")
builder.add_edge("intent_matching_node", "instagram")
builder.add_edge("intent_matching_node", "twitter")
builder.add_edge("intent_matching_node", "linkedin")
builder.add_edge("intent_matching_node", "blog")
builder.add_edge("blog", "combine_content")
builder.add_edge("twitter", "combine_content")
builder.add_edge("instagram", "combine_content")
builder.add_edge("linkedin", "combine_content")
builder.add_edge("combine_content", END)

graph = builder.compile()

def main():
    # Page configuration with custom theme
    st.set_page_config(
        page_title="Content Intelligence AI",
        page_icon="📢",
        layout="wide",
        initial_sidebar_state="expanded"
    )

    # Custom CSS for better styling
    st.markdown("""
    <style>
    .main-header {
        font-size: 2.5rem;
        color: #1E88E5;
        margin-bottom: 0;
    }
    .subheader {
        font-size: 1.2rem;
        color: #666;
        margin-top: 0;
        margin-bottom: 2rem;
    }
    .platform-header {
        font-weight: 600;
        color: #1E88E5;
        margin-bottom: 1rem;
    }
    .section-divider {
        margin-top: 2rem;
        margin-bottom: 2rem;
    }
    .platform-card {
        padding: 1.5rem;
        border-radius: 10px;
        box-shadow: 0 4px 6px rgba(0,0,0,0.1);
        margin-bottom: 1rem;
        transition: transform 0.3s ease;
    }
    .platform-card:hover {
        transform: translateY(-5px);
    }
    .platform-icon {
        font-size: 2rem;
        margin-bottom: 0.5rem;
    }
    .btn-generate {
        background-color: #1E88E5;
        color: white;
        padding: 0.75rem 1.5rem;
        font-weight: 600;
        border-radius: 7px;
        margin-top: 1rem;
    }
    .footer {
        text-align: center;
        margin-top: 3rem;
        color: #666;
        font-size: 0.8rem;
    }
    .api-key-section {
        background-color: #f8f9fa;
        padding: 1.5rem;
        border-radius: 10px;
        margin-bottom: 1.5rem;
    }
    .sidebar-header {
        font-weight: 600;
        margin-bottom: 1rem;
    }
    .result-container {
        padding: 1.5rem;
        border-radius: 10px;
        background-color: #f8f9fa;
        margin-top: 1.5rem;
    }
    </style>
    """, unsafe_allow_html=True)

    # Sidebar
    with st.sidebar:
        st.image("https://place-hold.it/300x100?text=Content%20AI&fontsize=23", width=250)
        
        st.markdown('<p class="sidebar-header">🔧 Configuration</p>', unsafe_allow_html=True)
        
        with st.expander("📋 About", expanded=False):
            st.markdown("""
            **Content Intelligence AI** helps you optimize your content for multiple social media platforms.
            
            Features:
            - Content summarization
            - Platform-specific formatting
            - Hashtag suggestions
            - Engagement optimization
            
            Made with ❤️ using LangGraph
            """)
        
        st.markdown('<div class="api-key-section">', unsafe_allow_html=True)
        st.markdown('<p class="sidebar-header">🔑 API Keys</p>', unsafe_allow_html=True)
        openai_api_key = st.text_input("OpenAI API Key", type="password", 
                                       value=os.environ.get("OPENAI_API_KEY", ""))
        langchain_api_key = st.text_input("LangChain API Key", type="password",
                                         value=os.environ.get("LANGCHAIN_API_KEY", ""))
        tavily_api_key = st.text_input("Tavily API Key", type="password",
                                      value=os.environ.get("TAVILY_API_KEY", ""))
        st.markdown('</div>', unsafe_allow_html=True)
        
        if st.button("💾 Save API Keys", use_container_width=True):
            if openai_api_key and langchain_api_key and tavily_api_key:
                os.environ["OPENAI_API_KEY"] = openai_api_key
                os.environ["LANGCHAIN_API_KEY"] = langchain_api_key
                os.environ["TAVILY_API_KEY"] = tavily_api_key
                st.success("✅ API keys saved successfully!")
            else:
                st.warning("⚠️ Please enter all required API keys!")
    
    # Main content
    st.markdown('<h1 class="main-header">Content Intelligence AI</h1>', unsafe_allow_html=True)
    st.markdown('<p class="subheader">Transform your content into platform-specific masterpieces with AI</p>', unsafe_allow_html=True)
    
    # Create tabs for better organization
    tab1, tab2 = st.tabs(["Create Content", "History"])
    
    with tab1:
        # Input Section
        st.markdown('<p class="platform-header">📝 Content Source</p>', unsafe_allow_html=True)
        
        content_source = st.radio(
            "Select content source:",
            ["Write content", "Upload document", "URL"],
            horizontal=True
        )
        
        if content_source == "Write content":
            user_text = st.text_area(
                "Enter your content below:",
                placeholder="Type or paste your content here...",
                height=200
            )
        elif content_source == "Upload document":
            st.info("📎 Upload a document to extract content")
            uploaded_file = st.file_uploader("Choose a file", type=["txt", "pdf", "docx"])
            if uploaded_file:
                user_text = "Content from: " + uploaded_file.name
                # In a real app, you'd process the file here
            else:
                user_text = ""
        else:  # URL
            url = st.text_input("Enter URL to extract content from:")
            if url:
                user_text = f"Content from URL: {url}"
                # In a real app, you'd scrape content from the URL
            else:
                user_text = ""
        
        # Platform Selection with improved UI
        st.markdown('<p class="platform-header">📱 Select Platforms</p>', unsafe_allow_html=True)
        
        col1, col2, col3, col4 = st.columns(4)
        platforms = []
        
        with col1:
            st.markdown('<div class="platform-card">', unsafe_allow_html=True)
            st.markdown('<div class="platform-icon">🐦</div>', unsafe_allow_html=True)
            if st.checkbox("Twitter", value=True):
                platforms.append("Twitter")
            st.markdown('<div style="font-size:0.8rem; color:#666;">280 character limit, hashtags</div>', unsafe_allow_html=True)
            st.markdown('</div>', unsafe_allow_html=True)
            
        with col2:
            st.markdown('<div class="platform-card">', unsafe_allow_html=True)
            st.markdown('<div class="platform-icon">💼</div>', unsafe_allow_html=True)
            if st.checkbox("LinkedIn", value=True):
                platforms.append("Linkedin")
            st.markdown('<div style="font-size:0.8rem; color:#666;">Professional tone, business focus</div>', unsafe_allow_html=True)
            st.markdown('</div>', unsafe_allow_html=True)
            
        with col3:
            st.markdown('<div class="platform-card">', unsafe_allow_html=True)
            st.markdown('<div class="platform-icon">📸</div>', unsafe_allow_html=True)
            if st.checkbox("Instagram"):
                platforms.append("Instagram")
            st.markdown('<div style="font-size:0.8rem; color:#666;">Visual focus, creative captions</div>', unsafe_allow_html=True)
            st.markdown('</div>', unsafe_allow_html=True)
            
        with col4:
            st.markdown('<div class="platform-card">', unsafe_allow_html=True)
            st.markdown('<div class="platform-icon">📝</div>', unsafe_allow_html=True)
            if st.checkbox("Blog"):
                platforms.append("Blog")
            st.markdown('<div style="font-size:0.8rem; color:#666;">Long-form, SEO optimized</div>', unsafe_allow_html=True)
            st.markdown('</div>', unsafe_allow_html=True)
        
        # Advanced options in an expander
        with st.expander("⚙️ Advanced Options", expanded=False):
            col1, col2 = st.columns(2)
            with col1:
                tone = st.select_slider(
                    "Content Tone",
                    options=["Casual", "Neutral", "Professional", "Enthusiastic", "Authoritative"]
                )
            with col2:
                creativity = st.slider("Creativity Level", min_value=0, max_value=10, value=7)
        
        # Generate button
        st.markdown('<div class="section-divider"></div>', unsafe_allow_html=True)
        
        generate_col1, generate_col2, generate_col3 = st.columns([1, 2, 1])
        with generate_col2:
            generate_clicked = st.button(
                "✨ Generate Optimized Content", 
                use_container_width=True,
                type="primary"
            )
        
        # Results
        if generate_clicked:
            if not user_text:
                st.warning("⚠️ Please enter some content to process.")
            elif not platforms:
                st.warning("⚠️ Select at least one platform.")
            elif not (os.environ.get("OPENAI_API_KEY") and os.environ.get("LANGCHAIN_API_KEY") and os.environ.get("TAVILY_API_KEY")):
                st.warning("⚠️ Please check that all API keys are provided in the sidebar.")
            else:
                with st.spinner("🔄 Processing your content across platforms..."):
                    # Here we would call your LangGraph pipeline
                    try:
                        # Simulate LangGraph processing
                        st.info("⏳ Analyzing content...")
                        st.progress(0.2)
                        st.info("⏳ Researching platform best practices...")
                        st.progress(0.5)
                        st.info("⏳ Optimizing for selected platforms...")
                        st.progress(0.8)
                        
                        # In your actual app, replace this with your graph invocation
                        # result = graph.invoke({"text": user_text, "platforms": platforms})
                        result = {"generated_content": f"This is sample generated content for platforms: {', '.join(platforms)}\n\n[Your actual content would appear here when integrated with LangGraph]"}
                        
                        st.progress(1.0)
                        st.success("✅ Content Generation Complete!")
                        
                        # Display results in an organized way
                        st.markdown('<div class="result-container">', unsafe_allow_html=True)
                        st.subheader("📊 Generated Content")
                        
                        # Create tabs for each platform
                        platform_tabs = st.tabs(platforms + ["All Content"])
                        
                        # Fill each platform tab with content
                        for i, platform in enumerate(platforms):
                            with platform_tabs[i]:
                                st.markdown(f"### {platform} Content")
                                st.markdown("---")
                                # In real app, you'd show platform-specific content here
                                st.markdown(f"Content optimized for {platform} would appear here")
                                
                                # Add copy button
                                if st.button(f"📋 Copy {platform} Content", key=f"copy_{platform}"):
                                    st.success(f"{platform} content copied to clipboard!")
                        
                        # All content tab
                        with platform_tabs[-1]:
                            st.markdown("### Complete Generated Content")
                            st.markdown("---")
                            st.markdown(result["generated_content"])
                            
                            # Download button
                            st.download_button(
                                label="📥 Download All Content",
                                data=result["generated_content"],
                                file_name="generated_content.txt",
                                mime="text/plain"
                            )
                        
                        st.markdown('</div>', unsafe_allow_html=True)
                    except Exception as e:
                        st.error(f"❌ An error occurred: {str(e)}")
    
    with tab2:
        st.info("📚 Your content generation history will appear here")
        st.markdown("No history available yet. Generate content to see it here.")
    
    # Footer
    st.markdown('<div class="section-divider"></div>', unsafe_allow_html=True)
    st.markdown('<p class="footer">Content Intelligence AI © 2025 | Powered by LangGraph</p>', unsafe_allow_html=True)

if __name__ == "__main__":
    main()