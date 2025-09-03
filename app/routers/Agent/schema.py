from langgraph.graph import add_messages
from langchain_core.messages import BaseMessage
from typing import TypedDict, List,Optional, Annotated,Sequence,Set, Dict


class Clarification(TypedDict):
    needs_improvement :  bool
    questions : Optional[List[str]]


class KeywordExtractionOutput(TypedDict):
    google_scholar_queries: List[str]


class Selection(TypedDict):
    paper_titles: List[str]


class AgentState(TypedDict):
    clarification : Clarification
    keywords : KeywordExtractionOutput
    messages : Annotated[Sequence[BaseMessage],add_messages]
    scholar_titles : Set[str]
    selected_papers_1 : List[str]
    selected_papers_2 : List[str]
    metadata: Dict[str,List[str]]