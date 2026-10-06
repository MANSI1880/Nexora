from typing import TypedDict, List, Optional, Any
from langchain_core.messages import BaseMessage

class AgentState(TypedDict):
    # Input
    user_message: str
    conversation_history: List[BaseMessage]
    
    # Intent classification
    intent: Optional[str]
    confidence: float
    
    # RAG
    retrieved_documents: List[dict]
    
    # Final Output
    generated_answer: str
    requested_action: Optional[str]
    ticket_info: Optional[dict]
    approval_requirement: bool
    final_status: str
