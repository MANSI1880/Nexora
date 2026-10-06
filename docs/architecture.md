# System Architecture - Nexora

## High-Level Flow
```
User
 ↓
React Frontend
 ↓
FastAPI Backend
 ↓
LangGraph Orchestrator
 ↓
Router / Intent Agent
 ↓
 ├── Knowledge / RAG Agent
 ├── Diagnostic Agent
 └── Action Agent
          ↓
     Secure Tool Layer
          ↓
     RBAC / Approval
          ↓
     IT Operation
          ↓
      Audit Log
          ↓
     Final Response
```

## Directory Structure
```text
Nexora/
├── frontend/           # Shreya: React, Tailwind, Next.js/Vite
├── backend/            # Yukti & Mansi (Python Backend & AI)
│   └── app/
│       ├── api/        # Yukti: FastAPI routes
│       ├── agents/     # Mansi: LangGraph agents & AI router
│       ├── rag/        # Mansi: Knowledge retrieval & vector DB integrations
│       ├── tools/      # Yukti/Mansi: Defined secure tools for AI
│       ├── auth/       # Yukti: JWT & RBAC
│       ├── database/   # Yukti: DB connection & setup
│       ├── models/     # Yukti: SQLAlchemy models
│       ├── schemas/    # Yukti/Mansi: Pydantic schemas (data contracts)
│       ├── services/   # Yukti: Core business logic
│       └── main.py     # Application entrypoint
├── knowledge-base/     # Raw knowledge files for RAG
├── tests/              # Shared test suite
├── docs/               # Team documentation
├── docker-compose.yml  # Shreya: Local development orchestration
├── .env.example        # Shared environment variables
└── README.md
```

## API Boundaries

### Frontend <-> Backend

`POST /api/chat`
- **Request:** `{ "message": "My VPN is not working" }`
- **Response:** 
```json
{
  "response": "I see you are having VPN issues. I have created a ticket...",
  "intent": "vpn_troubleshooting",
  "confidence": 0.95,
  "sources": ["kb/vpn-troubleshooting.md"],
  "ticket_id": "TKT-123",
  "action": "CREATE_TICKET",
  "status": "resolved"
}
```

`GET /api/tickets`
- **Request:** Headers (Auth Token)
- **Response:** `[ { "id": "TKT-123", "status": "OPEN", "created_at": "..." } ]`

### AI Architecture inside Backend
The AI layer (Mansi) is integrated directly into the FastAPI backend to avoid complex microservices overhead and simplify deployment. The API routes (`backend/app/api`) will call the LangGraph orchestrator (`backend/app/agents/orchestrator.py`).
