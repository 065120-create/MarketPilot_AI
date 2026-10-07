# MarketPilot AI — Render Production Launch Checklist

Use this checklist before and after deploying MarketPilot AI to Render to ensure a zero-defect, production-grade cloud deployment.

---

### Phase A: Pre-Deployment Repository Audit
- [ ] Working source code tested locally with all 69 pytest tests passing.
- [ ] No `.env` file, private API keys, or raw passwords present in git status.
- [ ] `.env.example` is complete and up to date.
- [ ] `.gitignore` properly excludes `__pycache__/`, `.pytest_cache/`, `uploads/`, `*.log`, `.DS_Store`.
- [ ] `requirements.txt` contains valid, compatible dependencies.
- [ ] `Dockerfile` and `docker-compose.yml` configured properly.
- [ ] `README.md` updated with architecture, quickstart, and live endpoints.

---

### Phase B: Render Web Service Configuration
- [ ] Render account connected to GitHub repository.
- [ ] Web Service created with branch `main`.
- [ ] Runtime selected: `Python 3` (or `Docker`).
- [ ] Build Command: `pip install -r requirements.txt`.
- [ ] Start Command: `uvicorn app.main:app --host 0.0.0.0 --port $PORT`.
- [ ] Environment variable `PYTHON_VERSION` set to `3.11.9`.
- [ ] Environment variable `LLM_PROVIDER` set to `gemini` (or `openai`).
- [ ] Environment variable `GOOGLE_API_KEY` added (if using live Gemini inference).
- [ ] Environment variable `DEBUG` set to `false`.
- [ ] Environment variable `LOG_LEVEL` set to `INFO`.
- [ ] Environment variable `N8N_ENABLED` set to `true` (if n8n active).
- [ ] Environment variable `N8N_WEBHOOK_URL` set to production webhook URL.

---

### Phase C: Live Verification on Render URL
- [ ] `/health` returns HTTP 200 `{"status": "healthy"}`.
- [ ] `/docs` renders Swagger interactive API explorer.
- [ ] Homepage `/` and `/index.html` loads with hero styling and working buttons.
- [ ] Demo Mode: "Launch Academic Demo" creates job and displays live ROAS/CPA on `/dashboard.html`.
- [ ] New Campaign: `/campaign.html` completes spelling normalization, review, and swarm analysis.
- [ ] Observability: `/agents.html` shows live multi-agent execution pipeline and Quality reflection loop.
- [ ] Customer Insights: `/insights.html` renders sentiment doughnut and feedback cards.
- [ ] Segmentation: `/segments.html` displays K-Means cluster share and radar profiles.
- [ ] Journey Funnel: `/journey.html` displays 5-stage conversion funnel and bottleneck loss flags.
- [ ] Budget Optimizer: `/budget.html` displays convex baseline vs recommended allocation table.
- [ ] Scenario Simulator: `/scenarios.html` interactive sliders recalculate revenue lift on input.
- [ ] Human Governance: `/recommendations.html` displays synthesized strategic directive package.
- [ ] RAG Explorer: `/rag.html` returns relevant chunks for marketing queries.
- [ ] Executive Brief: `/reports.html` displays clean printable brief.

---

### Phase D: Downstream Automation Verification
- [ ] n8n Cloud workflow is activated.
- [ ] "Approve & Trigger n8n Workflow" button clicked on `/recommendations.html`.
- [ ] HTTP 200 received from n8n webhook.
- [ ] New row logged in Google Sheets with Job ID, Brand, Budget, and Recommendations.
- [ ] Report URL archived in Google Drive.
- [ ] Executive email briefing received in inbox.
