from typing import Any, Dict
from langgraph.graph import END, START, StateGraph
from state.state import LaunchGraphState


def pm_node(state: LaunchGraphState) -> Dict[str, Any]:
    """Node to trigger the Product Manager agent."""
    print("-> PM Node Executing...")
    return {}


def tech_node(state: LaunchGraphState) -> Dict[str, Any]:
    """Node to trigger the Technical Lead agent."""
    print("-> Tech Lead Node Executing...")
    return {}


def marketing_node(state: LaunchGraphState) -> Dict[str, Any]:
    """Node to trigger the Marketing Lead agent."""
    print("-> Marketing Node Executing...")
    return {}


def synthesis_node(state: LaunchGraphState) -> Dict[str, Any]:
    """Node to compile PM, Tech, and Marketing briefs into the final package."""
    print("-> Synthesis Node Executing...")
    return {}


# Initialize graph
workflow = StateGraph(LaunchGraphState)

# Define nodes
workflow.add_node("pm", pm_node)
workflow.add_node("tech_lead", tech_node)
workflow.add_node("marketing", marketing_node)
workflow.add_node("synthesis", synthesis_node)

# Define transitions
workflow.add_edge(START, "pm")
workflow.add_edge("pm", "tech_lead")
workflow.add_edge("pm", "marketing")
workflow.add_edge("tech_lead", "synthesis")
workflow.add_edge("marketing", "synthesis")
workflow.add_edge("synthesis", END)

# Compile graph
launch_graph = workflow.compile()
