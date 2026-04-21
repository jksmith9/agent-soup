from langgraph.graph import StateGraph, START, END
from .state import AgentState
from .nodes import data_fetcher_node, analyst_node, advisor_node

def route_after_fetch(state: AgentState):
    if state.get("error"):
        return END
    return "analyst"

def route_after_analyst(state: AgentState):
    if state.get("error"):
        return END
    return "advisor"

def build_graph() -> StateGraph:
    workflow = StateGraph(AgentState)
    
    # Add nodes
    workflow.add_node("data_fetcher", data_fetcher_node)
    workflow.add_node("analyst", analyst_node)
    workflow.add_node("advisor", advisor_node)
    
    # Define edges
    # START -> data_fetcher
    workflow.add_edge(START, "data_fetcher")
    
    # data_fetcher -> analyst OR END (if error)
    workflow.add_conditional_edges(
        "data_fetcher",
        route_after_fetch,
        {"analyst": "analyst", END: END}
    )
    
    # analyst -> advisor OR END (if error)
    workflow.add_conditional_edges(
        "analyst",
        route_after_analyst,
        {"advisor": "advisor", END: END}
    )
    
    # advisor -> END
    workflow.add_edge("advisor", END)
    
    # Compile graph
    app = workflow.compile()
    return app
