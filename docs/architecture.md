# MarketPilot AI System Architecture

## System Overview

MarketPilot AI is an advanced, multi-agent artificial intelligence platform designed to automate and optimize marketing campaigns. By leveraging LLMs (Large Language Models), RAG (Retrieval-Augmented Generation), and complex multi-agent orchestration, the system acts as a fully autonomous marketing analyst and execution engine. 

```text
+-------------------------------------------------------------------+
|                           User Interface                          |
|  (React/Next.js/Streamlit - Campaign Setup, Dashboards, Reports)  |
+---------------------------------+---------------------------------+
                                  | HTTP / WebSocket
+---------------------------------v---------------------------------+
|                       API Gateway / FastAPI                       |
|   (Authentication, Rate Limiting, Request Routing, Webhooks)      |
+---------------------------------+---------------------------------+
                                  |
+---------------------------------v---------------------------------+
|                    Multi-Agent Orchestrator                       |
|   (LangChain / AutoGen / CrewAI based Agent Orchestration)        |
+---------+-----------------------+-----------------------+---------+
          |                       |                       |
+---------v---------+   +---------v---------+   +---------v---------+
| Data Analyst Agent|   | Strategist Agent  |   | Executor Agent    |
| (Cleans, validates|   | (Plans, optimizes |   | (Takes action,    |
|   market data)    |   | budget & audience)|   |   notifies n8n)   |
+---------+---------+   +---------+---------+   +---------+---------+
          |                       |                       |
+---------v---------+   +---------v---------+   +---------v---------+
| Vector Store (DB) |   |  LLM API (OpenAI) |   | External Tools &  |
|  (ChromaDB / RAG) |   | (GPT-4 / Claude)  |   | Automations (n8n) |
+-------------------+   +-------------------+   +-------------------+
```

## Component Architecture

### 1. Backend (FastAPI)
The backend is built with FastAPI, providing a high-performance, asynchronous REST API. 
- **Role:** Handles client requests, manages state, triggers agent workflows, and serves RAG endpoints.
- **Key Modules:**
  - `routers/`: API endpoints for campaigns, agents, and data.
  - `agents/`: Core logic for multi-agent workflows.
  - `services/`: Interfaces with vector databases, n8n, and external LLM providers.
  - `models/`: Pydantic data models for input validation.

### 2. Frontend
The UI provides a dashboard for marketers to input campaign parameters, upload data, and visualize agent recommendations.
- **Role:** User interaction, data visualization, execution trace monitoring, human-in-the-loop approval.
- **Key Features:** Campaign configuration, chat interface with agents, data upload, RAG source transparency.

### 3. RAG System (Retrieval-Augmented Generation)
- **Role:** Provides context-aware memory and domain knowledge to the agents.
- **Components:** ChromaDB vector database, embedding models (OpenAI), chunking pipeline for historical marketing data and reports.

### 4. Workflow Automation (n8n)
- **Role:** Executes real-world actions approved by the user.
- **Integration:** Triggered via webhooks from the backend. Performs actions like sending emails, updating Google Sheets, or creating ad campaigns via APIs.

## Data Flow
1. **Input:** User submits a campaign brief and optional CSV data via the UI.
2. **Validation:** Backend validates data using Pydantic and data quality engines.
3. **Retrieval:** Agents query the RAG vector store for historical context and similar past campaigns.
4. **Orchestration:** Orchestrator assigns tasks to the Data Analyst, then the Strategist, and finally the Executor.
5. **Review:** Recommendations are sent back to the UI for Human-in-the-Loop (HITL) approval.
6. **Execution:** Upon approval, the backend fires a webhook to n8n for final execution.

## Technology Stack
- **Language:** Python 3.10+
- **Framework:** FastAPI
- **LLM Integration:** LangChain, OpenAI GPT-4o
- **Vector Database:** ChromaDB
- **Automation:** n8n
- **Containerization:** Docker, Docker Compose
- **Deployment:** Render / AWS

## Design Decisions
1. **Multi-Agent over Single LLM:** A single LLM struggles with complex, multi-step reasoning. Separating roles (Analyst, Strategist, Executor) with strict tools and prompts reduces hallucinations and increases reliability.
2. **Human-in-the-Loop (HITL):** Financial decisions (ad spend) must be approved by a human. The system prepares the action but pauses execution until explicit approval.
3. **Local Vector Store for Dev:** ChromaDB is used as a local, embedded database to simplify setup and eliminate the need for a separate database server during testing.

## Scalability Considerations
- **Stateless APIs:** FastAPI endpoints are stateless, allowing horizontal scaling.
- **Async Execution:** Heavy agent runs are pushed to background tasks (or message queues like Celery/Redis in production) to prevent blocking the API.
- **Vector DB Scaling:** In production, ChromaDB can be swapped for managed Pinecone or Weaviate.

## Security Architecture
- **API Keys:** Securely stored in `.env` and managed via environment variables. Never committed to version control.
- **Input Validation:** Strict Pydantic models prevent injection attacks and malformed data.
- **Authentication:** (Planned for production) JWT-based authentication for UI to Backend communication.
- **Webhook Security:** Secret tokens are passed in headers to verify n8n webhook triggers.
