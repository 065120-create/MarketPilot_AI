# MarketPilot AI — Master Execution Checklist for Group 6

This comprehensive checklist provides an unambiguous, step-by-step roadmap for final submission, live demonstration, and cloud deployment of **MarketPilot AI**.

---

## Part A: ALREADY DONE BY ANTIGRAVITY

- [x] **Canonical Local Project Verified:** Confirmed `~/Desktop/MarketPilot_AI/` contains the full working application with dynamic multi-brand support and zero hardcoded metrics.
- [x] **Core System Architecture:** Complete FastAPI backend with asynchronous lifespan, in-memory thread-safe `JobStore`, and clean RESTful API endpoints.
- [x] **10 Autonomous Agents:** Implemented Orchestrator, Campaign Performance, Customer Voice, Segmentation, Customer Journey, Optimization, Budget, Content, Quality Governance, and Synthesis agents.
- [x] **Deterministic-AI Separation:** Mathematical calculations (CTR, CPC, CPA, ROAS, RFM, $k$-means, budget optimization) computed in pure Python `pandas`/`numpy`/`scikit-learn`.
- [x] **Input Normalization & State Machine:** Fuzzy string matching with sequence matcher; verified state gate (`INPUT_VERIFICATION = COMPLETE`) before swarm execution.
- [x] **RAG Knowledge Base:** 10 curated marketing frameworks indexed into ChromaDB with zero-dependency TF-IDF fallback.
- [x] **Quality Governance Loop:** Automated programmatic verification of budget conservation ($\sum B_{\text{proposed}} = B_{\text{total}}$), arithmetic consistency, and evidence grounding with retry loop.
- [x] **Responsive Modern Frontend:** Complete HTML5/CSS/Vanilla JS interface with Dark/Light theme, interactive Chart.js charts, and live Stepper.
- [x] **n8n Workflow Schema Alignment:** Audited `n8n/MarketPilot_n8n_workflow.json` against `app/api/routes.py` with explicit POST method and expression matching.
- [x] **Docker & Render Configuration:** Updated `Dockerfile` with dynamic `${PORT:-8000}` binding and documented Render deployment procedures.
- [x] **Group 6 Word Submission Document:** Created `~/Desktop/MarketPilot_AI_Group_6_Submission.docx` on Desktop containing all 6 team members and academic write-ups.
- [x] **45-Section Academic Project Report:** Created `docs/FINAL_PROJECT_REPORT.md` thoroughly detailing the entire architecture and test outcomes.
- [x] **Architecture Diagrams:** Created all 7 Mermaid diagrams in `docs/diagrams/` (Overall System, Multi-Agent, RAG, Data Flow, Quality Recovery, n8n Automation, Render Deployment).
- [x] **Presentation & Viva Guides:** Updated `docs/DEMO_SCRIPT.md` (5-minute 12-step flow), `docs/PRESENTATION.md` (12-slide executive presentation), and `docs/VIVA_QUESTIONS.md` (120 questions).
- [x] **Test Verification:** Executed 69 automated tests with 100% pass rate.

---

## Part B: I NEED TO DO — GITHUB REPOSITORY SETUP

- [ ] **Step B.1:** Log in to your personal or university GitHub account ([github.com](https://github.com)).
- [ ] **Step B.2:** Click **[New Repository]**.
- [ ] **Step B.3:** Name the repository `MarketPilot_AI` (or `MarketPilot-AI-Group6`).
- [ ] **Step B.4:** Set visibility to **Public** (required for easy Render connection and faculty evaluation).
- [ ] **Step B.5:** Leave "Add a README file", ".gitignore", and "License" **UNCHECKED** (we already provide pre-built, tested files).
- [ ] **Step B.6:** In your local terminal, navigate to the final GitHub folder on your Desktop:
  ```bash
  cd ~/Desktop/MarketPilot_AI_GitHub_Final
  git init -b main
  git add .
  git commit -m "feat: initial production release of MarketPilot AI v1.0.0"
  git remote add origin https://github.com/<YOUR_GITHUB_USERNAME>/MarketPilot_AI.git
  git push -u origin main
  ```
- [ ] **Step B.7:** Verify your repository loads on GitHub and shows the professional `README.md` with badges.

---

## Part C: I NEED TO DO — N8N CLOUD CONFIGURATION

- [ ] **Step C.1:** Sign in to your n8n Cloud instance ([app.n8n.cloud](https://app.n8n.cloud)).
- [ ] **Step C.2:** In the top right menu, click **Import from File...** and select `~/Desktop/MarketPilot_AI_GitHub_Final/n8n/MarketPilot_n8n_workflow.json`.
- [ ] **Step C.3:** In Google Sheets:
  - Create a new Google Sheet titled **"MarketPilot Campaign Insights"**.
  - Add 9 headers in Row 1: `Job ID`, `Brand`, `Campaign`, `Date`, `Budget`, `Confidence Score`, `Key Findings`, `Recommendations`, `Status`.
- [ ] **Step C.4:** In n8n Cloud Credentials:
  - Connect your Google account for **Google Sheets OAuth2 API**.
  - Connect your Google account for **Google Drive OAuth2 API**.
  - Connect your Google account (or SMTP) for **Gmail OAuth2 API**.
- [ ] **Step C.5:** Open each node in the n8n canvas and select your newly configured credentials.
- [ ] **Step C.6:** In the Google Sheets node, select the "MarketPilot Campaign Insights" sheet from the dropdown.
- [ ] **Step C.7:** Click the **Webhook** node, toggle to the **Production URL**, and click **Copy Webhook URL** (e.g., `https://your-workspace.app.n8n.cloud/webhook/marketpilot`).
- [ ] **Step C.8:** Toggle the workflow switch in the top right to **Active** (Published).

---

## Part D: I NEED TO DO — RENDER CLOUD DEPLOYMENT

- [ ] **Step D.1:** Sign in to Render ([dashboard.render.com](https://dashboard.render.com)).
- [ ] **Step D.2:** Click **[New +]** $\rightarrow$ **[Web Service]**.
- [ ] **Step D.3:** Choose **Build and deploy from a Git repository**, click **Next**, and connect your `MarketPilot_AI` repository.
- [ ] **Step D.4:** Configure Web Service settings:
  - **Name:** `marketpilot-ai`
  - **Region:** Singapore / Frankfurt / Oregon (choose closest to you)
  - **Branch:** `main`
  - **Runtime:** `Python 3`
  - **Build Command:** `pip install -r requirements.txt`
  - **Start Command:** `uvicorn app.main:app --host 0.0.0.0 --port $PORT`
  - **Instance Type:** `Free`
- [ ] **Step D.5:** Under **Environment Variables**, add:
  - `LLM_PROVIDER` = `gemini`
  - `GOOGLE_API_KEY` = `<YOUR_ACTUAL_GEMINI_API_KEY>`
  - `GEMINI_MODEL` = `gemini-2.0-flash`
  - `DEBUG` = `false`
  - `LOG_LEVEL` = `INFO`
  - `MAX_UPLOAD_SIZE_MB` = `50`
  - `N8N_ENABLED` = `true`
  - `N8N_WEBHOOK_URL` = `<COPIED_N8N_PRODUCTION_WEBHOOK_URL>`
- [ ] **Step D.6:** Click **[Create Web Service]** and monitor the build logs until you see: `Application startup complete` and `Service is live`.
- [ ] **Step D.7:** Copy your public Render URL (e.g., `https://marketpilot-ai.onrender.com`).

---

## Part E: I NEED TO DO — FINAL LIVE TESTING

- [ ] **Step E.1:** Open your deployed Render URL in Google Chrome.
- [ ] **Step E.2:** Verify the landing page loads cleanly with active CSS styling and navigation links.
- [ ] **Step E.3:** Click **[Start Academic Demo]** and confirm the multi-agent analysis runs end-to-end.
- [ ] **Step E.4:** Navigate to **Campaign Dashboard** (`/dashboard.html`): verify ROAS, CPA, charts, and funnel render correctly.
- [ ] **Step E.5:** Navigate to **New Campaign** (`/campaign.html`): enter `cocacola` and test the input normalization state machine.
- [ ] **Step E.6:** Navigate to **Scenario Simulator** (`/scenarios.html`): adjust budget sliders and verify real-time recalculation.
- [ ] **Step E.7:** Navigate to **Recommendations** (`/recommendations.html`): click **[Approve Recommendations]**.
- [ ] **Step E.8:** Switch to your Google Sheet: verify a new row has appeared with your campaign data.
- [ ] **Step E.9:** Check your email inbox: verify receipt of the executive summary notification.

---

## Part F: I NEED TO DO — ACADEMIC SUBMISSION

- [ ] **Step F.1:** Locate `MarketPilot_AI_Group_6_Submission.docx` on your Desktop.
- [ ] **Step F.2:** Open the Word document and review the Group 6 member names on Page 1:
  1. Aditya Mishra
  2. Aman Kumar Singh
  3. Hardik Srivastava
  4. Rohit Kumar Jha
  5. Shouvik Das
  6. Satyam Raj
- [ ] **Step F.3:** Insert your public GitHub repository URL and live Render deployment URL into the document links section.
- [ ] **Step F.4:** Save the final `.docx` and export an official `.pdf` copy if required by your portal.
- [ ] **Step F.5:** Upload `MarketPilot_AI_Group_6_Submission.docx` and `MarketPilot_AI_GitHub_Final.zip` to your university LMS / Canvas / Google Classroom.

---

## Part G: I NEED TO DO — PRESENTATION PREPARATION

- [ ] **Step G.1:** Open `docs/PRESENTATION.md`.
- [ ] **Step G.2:** Copy the 12 slides into PowerPoint, Google Slides, or Canva using your college's official template.
- [ ] **Step G.3:** Assign speaking segments across the 6 team members:
  - *Member 1 (Aditya):* Slides 1–2 (Title, Business Problem, Context)
  - *Member 2 (Aman):* Slides 3–4 (Solution, Overall Architecture)
  - *Member 3 (Hardik):* Slides 5–6 (10-Agent Swarm, Agentic RAG)
  - *Member 4 (Rohit):* Slides 7–8 (Input Normalization, Scenario Simulator)
  - *Member 5 (Shouvik):* Slides 9–10 (Quality Governance, Human-in-the-Loop, n8n)
  - *Member 6 (Satyam):* Slides 11–12 (Testing, Production Verification, Q&A)
- [ ] **Step G.4:** Rehearse the 5-minute live demonstration using `docs/DEMO_SCRIPT.md`.

---

## Part H: I NEED TO DO — VIVA PREPARATION

- [ ] **Step H.1:** Review `docs/VIVA_QUESTIONS.md` (all 120 questions).
- [ ] **Step H.2:** Ensure every group member can explain the difference between deterministic math (`pandas`/`numpy`) and LLM reasoning.
- [ ] **Step H.3:** Be prepared to explain how the Quality Governance Agent prevents budget violations ($\sum x_i \le B$).
- [ ] **Step H.4:** Be prepared to demonstrate the n8n webhook payload schema and how Google Workspace is triggered.
- [ ] **Step H.5:** Confirm that every member knows all 69 automated tests passed with 100% success.
