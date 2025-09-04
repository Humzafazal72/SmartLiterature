from .schema import AgentState
from langgraph.graph import StateGraph,START,END
from langgraph.checkpoint.memory import InMemorySaver
from .agents import clarifier, keyworder, scholar_searcher, Selector_1, Selector_2, metadata_getter, clarifier_router

memory = InMemorySaver()
def merge_results(state: AgentState):
    return {
        "selected_papers": state.get("selected_papers_1", []) 
                          + state.get("selected_papers_2", [])
    }

graph = StateGraph(AgentState)

graph.add_node("clarificationAgent", clarifier)
graph.add_node("keywordAgent", keyworder)
graph.add_node("scholar_searcher", scholar_searcher)
graph.add_node("selecter_1", Selector_1)
graph.add_node("selecter_2", Selector_2)
graph.add_node("merger", merge_results)
graph.add_node("metadata_getter", metadata_getter)

graph.add_edge(START, "clarificationAgent")

graph.add_conditional_edges(
    "clarificationAgent",
    clarifier_router,
    {
        "end": END,
        "continue": "keywordAgent"
    }
)

graph.add_edge("keywordAgent", "scholar_searcher")
graph.add_edge("scholar_searcher", "selecter_1")
graph.add_edge("scholar_searcher", "selecter_2")

# Both selectors flow into merger
graph.add_edge("selecter_1", "merger")
graph.add_edge("selecter_2", "merger")

graph.add_edge("merger", "metadata_getter")

graph.add_edge("metadata_getter", END)

graph_app = graph.compile(checkpointer=memory)

