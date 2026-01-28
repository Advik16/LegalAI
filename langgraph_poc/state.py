from typing import TypedDict, List, Dict

class RAGState(TypedDict):
    question: str
    retrieved_docs: List[str]
    answer: str
    messages: List[Dict[str, str]]
