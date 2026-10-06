import os
from langgraph.graph import StateGraph, END
from langchain_openai import ChatOpenAI

from app.agents.state import AgentState
from app.agents.router import route_intent
from app.rag.retriever import get_rag_answer

def get_llm():
    return ChatOpenAI(
        model="gpt-4o-mini",
        temperature=0,
        api_key=os.environ.get("OPENAI_API_KEY", "dummy_key")
    )

def router_node(state: AgentState):
    llm = get_llm()
    classification = route_intent(state, llm)
    return classification

def rag_node(state: AgentState):
    llm = get_llm()
    result = get_rag_answer(state["user_message"], state.get("intent", ""), llm)
    return {
        "generated_answer": result["answer"],
        "retrieved_documents": result["sources"],
        "final_status": "resolved"
    }

def action_node(state: AgentState):
    return {
        "generated_answer": "I have created an IT request for this action. It is pending approval.",
        "requested_action": state.get("intent"),
        "approval_requirement": True,
        "final_status": "pending_approval"
    }

def unknown_node(state: AgentState):
    return {
        "generated_answer": "I'm sorry, I couldn't understand your request or don't have enough information. Would you like me to open a general support ticket?",
        "intent": "unknown",
        "final_status": "needs_escalation"
    }

def route_after_intent(state: AgentState):
    intent = state.get("intent")
    conf = state.get("confidence", 0.0)
    
    if intent == "unknown" or conf < 0.7:
        return "unknown"
    
    rag_intents = ["vpn_troubleshooting", "password_reset", "email_issue", "general_it_support"]
    if intent in rag_intents:
        return "rag"
    
    return "action"

def create_orchestrator():
    workflow = StateGraph(AgentState)
    
    workflow.add_node("router", router_node)
    workflow.add_node("rag", rag_node)
    workflow.add_node("action", action_node)
    workflow.add_node("unknown", unknown_node)
    
    workflow.set_entry_point("router")
    
    workflow.add_conditional_edges(
        "router",
        route_after_intent,
        {
            "rag": "rag",
            "action": "action",
            "unknown": "unknown"
        }
    )
    
    workflow.add_edge("rag", END)
    workflow.add_edge("action", END)
    workflow.add_edge("unknown", END)
    
    return workflow.compile()

app_workflow = create_orchestrator()

def process_chat_request(message: str) -> dict:
    initial_state = {
        "user_message": message,
        "conversation_history": [],
        "intent": None,
        "confidence": 0.0,
        "retrieved_documents": [],
        "generated_answer": "",
        "requested_action": None,
        "ticket_info": None,
        "approval_requirement": False,
        "final_status": "processing"
    }
    
    result = app_workflow.invoke(initial_state)
    
    # Ensure source paths are safe/stringified
    sources = []
    for doc in result.get("retrieved_documents", []):
        meta = doc.get("metadata", {})
        source_val = meta.get("source", "")
        sources.append(str(source_val))
        
    return {
        "response": result.get("generated_answer", ""),
        "intent": result.get("intent", "unknown"),
        "confidence": result.get("confidence", 0.0),
        "sources": sources,
        "ticket_id": result.get("ticket_info", {}).get("id") if result.get("ticket_info") else None,
        "action": result.get("requested_action"),
        "status": result.get("final_status", "resolved")
    }
