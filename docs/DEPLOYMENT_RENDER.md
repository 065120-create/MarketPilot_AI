# Step-by-Step Render Deployment

This guide covers deploying the MarketPilot AI backend (FastAPI) and frontend to Render.com.

## Prerequisites
- A GitHub account with the MarketPilot AI repository pushed.
- A Render.com account.
- OpenAI API Key.

## GitHub Repository Setup
Ensure your repository has a `requirements.txt` for the backend and `package.json` for the frontend.
The root should contain a `render.yaml` if using infrastructure-as-code, or you can configure it manually via the dashboard.

## Render Account Creation
1. Go to [Render.com](https://render.com) and sign up using GitHub.
2. Grant Render access to your MarketPilot AI repository.

## Web Service Configuration (Backend)
1. Click **New** -> **Web Service**.
2. Select your repository.
3. Configure settings:
   - **Name:** marketpilot-api
   - **Environment:** Python
   - **Build Command:** `pip install -r requirements.txt`
   - **Start Command:** `uvicorn app.main:app --host 0.0.0.0 --port 10000`
4. Select the instance type (Starter is recommended for AI workloads).

## Environment Variables
Under the **Environment** tab in Render, add the following variables:
- `OPENAI_API_KEY`: Your key.
- `N8N_WEBHOOK_URL`: Your n8n workflow URL.
- `ENVIRONMENT`: `production`
- `CORS_ORIGINS`: `https://your-frontend-url.onrender.com`

## Build and Deploy
Click **Create Web Service**. Render will clone the repo, run the build command, and deploy. Monitor the logs to ensure successful startup.

## Web Service Configuration (Frontend/Streamlit or Next.js)
If using Streamlit:
1. Create another **Web Service**.
2. **Build Command:** `pip install -r frontend/requirements.txt`
3. **Start Command:** `streamlit run frontend/app.py --server.port 10000 --server.address 0.0.0.0`
4. Set `API_BASE_URL` in environment variables pointing to the backend Render URL.

## Custom Domain (Optional)
1. Go to the **Settings** tab of your deployed service.
2. Scroll to **Custom Domains** and click **Add Custom Domain**.
3. Point your DNS A/CNAME records to Render as instructed.

## Monitoring
- Render provides built-in logs in the dashboard.
- For AI-specific monitoring (token usage, agent traces), integrate LangSmith or view the execution traces in the MarketPilot UI.

## Troubleshooting
- **Deploy fails on ChromaDB:** ChromaDB requires SQLite. Ensure the Python environment on Render has compatible SQLite libraries. You may need to use `pysqlite3-binary`.
- **Memory Limits:** Multi-agent workflows can consume memory. If you see "OOM (Out of Memory)" errors, upgrade to a higher tier instance on Render.
- **Timeouts:** Render drops connections after 100s. For long-running agent tasks, ensure the API uses asynchronous background tasks and websockets/polling for status updates.
