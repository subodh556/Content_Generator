from typing import Dict, List
from langchain_openai import ChatOpenAI
from langchain_community.tools import TavilySearchResults
from .prompts import *

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
import os 
import getpass

def _set_env(name:str):
    if not os.getenv(name):
        os.environ[name] = getpass.getpass(f"{name}:")
    
_set_env("OPENAI_API_KEY")

_set_env("TAVILY_API_KEY")


summ_model = ChatOpenAI(model="gpt-4-mini", temperature=0.6)
model = ChatOpenAI(model="gpt-4", temperature=0.6)


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


research_tool = TavilySearchResults(
    max_results=2,
    search_depth="advanced",
    include_answer=True,
    include_raw_content=True,
    include_images=True,
)

def summary_text(state: Dict) -> Dict:
    print("******* Generating summary of the given text *************")
    summary = summ_model.invoke(state["text"]).content
    return {
        "text": state["text"],
        "platforms": state["platforms"],
        "text_summary": summary
    }

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

class ReserachQuestions(TypedDict):
    questions: List[str]

def IntentMatching(state: ResearchOutputState):
    print("******* Sending data to each Platfrom *************")
    # platform_nodes = []
    # for platform in state["platforms"]:
    #     platform_nodes.append(Send(platform, {"text": state["text"],"research": state["research"], "platform": platform}))
    # return platform_nodes
    {"text": state["text"],"research": state["research"], "platforms": state["platforms"]}

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
