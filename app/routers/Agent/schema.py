from langgraph.graph import add_messages
from langchain_core.messages import BaseMessage
from typing import TypedDict, List,Optional, Annotated,Sequence, Dict, Union


class Clarification(TypedDict):
    needs_improvement :  bool
    questions: Optional[Union[List[str], None]] = None

class KeywordExtractionOutput(TypedDict):
    openalex_keywords: List[str]

class Selection(TypedDict):
    paper_titles: List[str]

class AgentState(TypedDict):
    clarification : Clarification
    keywords : KeywordExtractionOutput
    messages : Annotated[Sequence[BaseMessage],add_messages]
    initial_metadata: Dict[str,List[str]]
    selected_papers_1 : List[str]
    selected_papers_2 : List[str]
    final_metadata: Dict[str,List[str]]