from langgraph.graph import StateGraph, START, END
from .nodes import *

def create_graph():
    builder = StateGraph(input=InputState, output=GeneratedContent)
    
    # Add nodes
    builder.add_node("summary_node", summary_text)
    builder.add_node("research_node", research_node)
    builder.add_node("intent_matching_node", IntentMatching)
    builder.add_node("instagram", Insta)
    builder.add_node("twitter", Twitter)
    builder.add_node("linkedin", Linkedin)
    builder.add_node("blog", Blog)
    builder.add_node("combine_content", combining_content)
    
    # Add edges
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
    
    return builder.compile()

graph = create_graph()