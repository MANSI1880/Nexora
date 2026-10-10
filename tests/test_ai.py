import pytest
from unittest.mock import patch, MagicMock
from app.agents.orchestrator import process_chat_request
from app.schemas.chat import ChatResponse

@patch("app.agents.orchestrator.route_intent")
@patch("app.agents.orchestrator.ChatGoogleGenerativeAI")
@patch("app.rag.retriever.init_vector_store")
def test_vpn_request(mock_init_vs, mock_llm_orch, mock_route_intent):
    # Mock Router
    mock_route_intent.return_value = {"intent": "vpn_troubleshooting", "confidence": 0.95}
    
    # Mock RAG Vector Store
    mock_vs = MagicMock()
    mock_doc = MagicMock()
    mock_doc.page_content = "To fix VPN, restart Cisco AnyConnect."
    mock_doc.metadata = {"source": "../knowledge-base/vpn.md"}
    mock_vs.as_retriever.return_value.invoke.return_value = [mock_doc]
    mock_init_vs.return_value = mock_vs
    
    from langchain_core.messages import AIMessage
    mock_msg = AIMessage(content="To fix VPN, restart Cisco AnyConnect.")
    mock_llm_orch.return_value.invoke.return_value = mock_msg
    mock_llm_orch.return_value.return_value = mock_msg

    result = process_chat_request("My VPN is not working")
    
    # Validate against schema contract
    validated_response = ChatResponse(**result)
    
    assert validated_response.intent == "vpn_troubleshooting"
    assert "vpn.md" in validated_response.sources[0]
    assert validated_response.status == "resolved"

@patch("app.agents.orchestrator.route_intent")
def test_unknown_request(mock_route_intent):
    # Mock Router
    mock_route_intent.return_value = {"intent": "unknown", "confidence": 0.4}
    
    result = process_chat_request("What is the meaning of life?")
    
    validated_response = ChatResponse(**result)
    
    assert validated_response.intent == "unknown"
    assert validated_response.status == "needs_escalation"

@patch("app.agents.orchestrator.route_intent")
def test_action_request(mock_route_intent):
    # Mock Router
    mock_route_intent.return_value = {"intent": "application_access", "confidence": 0.90}
    
    result = process_chat_request("I need access to Jira")
    
    validated_response = ChatResponse(**result)
    
    assert validated_response.intent == "application_access"
    assert validated_response.status == "pending_approval"
    assert validated_response.action == "application_access"
