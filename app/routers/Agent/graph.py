from .schema import AgentState
from langgraph.graph import StateGraph,START,END
from .agents import (clarifier, keyworder, OpenAlex_searcher, 
                     Selector_1, Selector_2,  clarifier_router,
                     merge_results)

#memory = InMemorySaver()
def build_graph():
    graph = StateGraph(AgentState)

    graph.add_node("clarificationAgent", clarifier)
    graph.add_node("keywordAgent", keyworder)
    graph.add_node("scholar_searcher", OpenAlex_searcher)
    graph.add_node("selecter_1", Selector_1)
    graph.add_node("selecter_2", Selector_2)
    graph.add_node("merger", merge_results)

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

    graph.add_edge("merger", END)
    return graph

# graph_app = graph.compile(checkpointer=memory)