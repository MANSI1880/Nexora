# Development & Collaboration Guide

## Local Setup

### 1. Clone & Environment
Clone the repository and copy `.env.example` to `.env`. Fill in local values.

### 2. Frontend Setup (Shreya)
Navigate to `frontend/`. Use `npm install` and `npm run dev`.

### 3. Backend & AI Setup (Yukti & Mansi)
Navigate to `backend/`. Use `pip install -r requirements.txt`. Run using `uvicorn app.main:app --reload`.
*(Since AI and Backend share the Python environment, keep `requirements.txt` updated for both FastAPI and LangGraph dependencies).*

### 4. Docker Compose
Run `docker-compose up` to spin up the Database, Backend, and Frontend locally.

## Integration Strategy & Contracts
To allow Mansi, Yukti, and Shreya to work independently:
1. **Shared Schemas First**: Yukti and Mansi must agree on the Pydantic schemas in `backend/app/schemas/` before writing logic. The `ChatResponse` model is the central contract.
2. **Mocking**: 
   - Yukti provides mock endpoints for the Frontend.
   - Mansi builds LangGraph agents that can be run independently via CLI scripts before wiring into FastAPI routes.
3. **Git Workflow**: Use feature branches (`feature/frontend-login`, `feature/backend-auth`, `feature/ai-router`). Merge into `main` via PRs. Do NOT modify another team member's domain without communication.
