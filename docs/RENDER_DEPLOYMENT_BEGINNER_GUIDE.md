# MarketPilot AI — Step-by-Step Render Deployment Guide

This guide provides a comprehensive deployment walkthrough to deploy the final MarketPilot AI repository to **Render (render.com)** as a production Web Service.

---

## 1. Deployment Method Comparison & Recommendation

| Criteria | Option A: Native Python (Recommended for Speed & Simplicity) | Option B: Docker Web Service (Recommended for Isolation) |
|---|---|---|
| **Build Time** | ~2–3 minutes | ~4–6 minutes |
| **Setup Complexity** | Very Low (Standard Git push) | Low (Uses repository `Dockerfile`) |
| **Port Binding** | Automatically binds via `$PORT` | Uses `${PORT:-8000}` CMD in Dockerfile |
| **System Dependencies**| Managed by Render standard Python runtime | Managed inside container |
| **Recommendation** | **PRIMARY CHOICE:** Native Python is faster and simplest for MBA/PGDM project evaluations. | **FALLBACK:** Choose if any native C-compiler libraries conflict. |

---

## 2. Step-by-Step Deployment Walkthrough

### Step 1: Push Final Code to Your GitHub Account
1. Open GitHub in your browser (`github.com`) and create a new repository:
   - Name: `MarketPilot_AI`
   - Visibility: `Public` (or `Private`)
   - Leave "Initialize with README" **unchecked**.
2. On your computer, open Terminal and push the final folder:
   ```bash
   cd ~/Desktop/MarketPilot_AI_GitHub_Final
   git init
   git add .
   git commit -m "Initial production release of MarketPilot AI"
   git branch -M main
   git remote add origin https://github.com/<your-username>/MarketPilot_AI.git
   git push -u origin main
   ```

---

### Step 2: Create a Render Account
1. Visit [https://render.com](https://render.com) and sign up using your **GitHub account**.
2. Authorize Render to access your GitHub repositories.

---

### Step 3: Create a New Web Service
1. In the Render Dashboard, click the **"New +"** button in the top right.
2. Select **"Web Service"**.
3. Under "Connect a repository", search for `MarketPilot_AI` and click **"Connect"**.

---

### Step 4: Configure Service Parameters (Option A: Native Python)

Enter the exact settings below:

- **Name:** `marketpilot-ai` *(or any unique name, e.g. `marketpilot-group6`)*
- **Region:** `Singapore` (or `Oregon / Frankfurt` depending on your location)
- **Branch:** `main`
- **Root Directory:** *(leave blank — defaults to repository root)*
- **Runtime:** `Python 3`
- **Build Command:**
  ```bash
  pip install -r requirements.txt
  ```
- **Start Command:**
  ```bash
  uvicorn app.main:app --host 0.0.0.0 --port $PORT
  ```
  *(Render automatically injects the `$PORT` environment variable.)*
- **Instance Type:** `Free` (or `Starter` $7/mo for zero sleep latency)

---

### Step 5: Configure Environment Variables

Scroll down to the **"Environment Variables"** section and click **"Add Environment Variable"** for each entry:

| Key | Value | Notes |
|---|---|---|
| `PYTHON_VERSION` | `3.11.9` | Ensures Python 3.11 compatibility on Render |
| `LLM_PROVIDER` | `gemini` | Generative reasoning provider |
| `GOOGLE_API_KEY` | *(Your Gemini API key)* | Optional for demo; unlocks live LLM |
| `GEMINI_MODEL` | `gemini-2.0-flash` | Fast, high-accuracy flash model |
| `DEBUG` | `false` | Production mode |
| `LOG_LEVEL` | `INFO` | Clean server logs |
| `N8N_ENABLED` | `true` *(or `false`)* | Set to `true` once n8n is active |
| `N8N_WEBHOOK_URL`| `https://<subdomain>.app.n8n.cloud/webhook/marketpilot-webhook` | Production webhook from n8n Cloud |

---

### Step 6: Deploy and Monitor Build Logs
1. Click **"Create Web Service"**.
2. Render will clone the repository, run `pip install -r requirements.txt`, index the RAG knowledge base markdown files, and launch Uvicorn.
3. Look for the following green confirmation lines in the Render deploy log:
   ```
   INFO: 🚀 Starting MarketPilot AI v1.0.0
   INFO: 📚 RAG Knowledge Base: Ingestion complete
   INFO: ✅ MarketPilot AI ready at http://0.0.0.0:10000
   INFO: Application startup complete.
   ```
4. Render displays your live URL at the top left (e.g., `https://marketpilot-ai.onrender.com`).

---

## 3. Post-Deployment Verification Checklist

Test every core capability on your live Render URL:

1. **Health Check:** Open `https://<your-render-url>/health` &rarr; Returns `{"status":"healthy","app":"MarketPilot AI",...}`.
2. **Interactive API Docs:** Open `https://<your-render-url>/docs` &rarr; Swagger UI renders with all 22 endpoints.
3. **Landing Page:** Open `https://<your-render-url>/` &rarr; Homepage loads smoothly.
4. **Launch Demo:** Click **"Launch Academic Demo"** &rarr; Navigates to `/dashboard.html` with real ROAS, CPA, and channel allocations.
5. **New Campaign Workflow:** Create a campaign on `/campaign.html` (e.g. `Nike`), test spelling normalization, click **"Run Multi-Agent Analysis"**, and verify the live swarm trace.
6. **Scenario Simulator:** Open `/scenarios.html`, adjust channel spend sliders, and confirm dynamic revenue lift calculation.
7. **Executive Report:** Open `/reports.html` &rarr; Iframe loads the styled, printable executive brief.
8. **Downstream Approval to n8n:** Go to `/recommendations.html`, click **"Approve & Dispatch to n8n"**, and check your Google Sheet for the appended row.

---

## 4. Alternative: Option B — Docker Web Service Deployment

If you prefer deploying with Docker:
1. When creating the Web Service on Render, choose **Runtime:** `Docker`.
2. Leave Build Command and Start Command blank (Render will automatically read `Dockerfile`).
3. Render runs the multi-stage build, starts the container, and automatically routes external traffic to `${PORT:-8000}`.
