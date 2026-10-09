from langchain_core.prompts import ChatPromptTemplate
from langchain_google_genai import ChatGoogleGenerativeAI
from pydantic import BaseModel, Field

class IntentClassification(BaseModel):
    intent: str = Field(
        description="The classified intent of the user request. Must be one of: vpn_troubleshooting, password_reset, account_unlock, email_issue, software_access, application_access, hardware_request, ticket_creation, general_it_support, unknown."
    )
    confidence: float = Field(description="Confidence score between 0.0 and 1.0")

def route_intent(state: dict, llm: ChatGoogleGenerativeAI) -> dict:
    """Classifies the user intent using the LLM."""
    prompt = ChatPromptTemplate.from_messages([
        ("system", "You are an IT Service Desk intent classifier. Classify the user's message into one of the following categories: vpn_troubleshooting, password_reset, account_unlock, email_issue, software_access, application_access, hardware_request, ticket_creation, general_it_support, unknown. If you are not highly confident (>0.8), default to 'unknown'."),
        ("user", "{user_message}")
    ])
    
    chain = prompt | llm.with_structured_output(IntentClassification)
    
    try:
        result = chain.invoke({"user_message": state.get("user_message", "")})
        return {
            "intent": result.intent,
            "confidence": result.confidence
        }
    except Exception as e:
        return {
            "intent": "unknown",
            "confidence": 0.0
        }
