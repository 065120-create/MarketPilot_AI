# Troubleshooting Guide

Common issues encountered when setting up or running MarketPilot AI, and their solutions.

## API Key Errors
- **Error:** `AuthenticationError: Incorrect API key provided.` or UI shows "Agent Failed."
- **Cause:** Missing or invalid OpenAI API key.
- **Solution:** Ensure `OPENAI_API_KEY` is correctly set in your `.env` file without quotes. Restart the backend.

## Port Conflicts
- **Error:** `Address already in use` (usually port 8000 for FastAPI or 8501 for Streamlit).
- **Cause:** Another service is running on the default ports.
- **Solution:** 
  - Kill the existing process: `lsof -i :8000` then `kill -9 <PID>`.
  - Or, change the port in `docker-compose.yml` or the start command (e.g., `uvicorn app.main:app --port 8001`).

## ChromaDB Issues
- **Error:** `RuntimeError: Your system has an unsupported version of sqlite3. Chroma requires sqlite3 >= 3.35.0.`
- **Cause:** Common on older Linux distros or Render.com deployments.
- **Solution:** 
  - Install `pysqlite3-binary` via pip.
  - Add the following to the top of your `main.py` before importing Chroma:
    ```python
    __import__('pysqlite3')
    import sys
    sys.modules['sqlite3'] = sys.modules.pop('pysqlite3')
    ```

## n8n Connection Failed
- **Error:** The UI says "Execution Approved" but nothing happens, or backend logs show a `500` error during webhook trigger.
- **Cause:** The `N8N_WEBHOOK_URL` is incorrect, or the n8n workflow is not activated.
- **Solution:** 
  - Ensure the workflow toggle is set to "Active" in the n8n dashboard.
  - Verify you are using the Production URL, not the Test URL (Test URLs require the n8n window to be actively "listening").

## Docker Issues
- **Error:** `docker-compose build` fails on installing requirements.
- **Cause:** Network issues, or incompatible library versions for your specific OS architecture (e.g., Apple Silicon M1/M2 vs Intel).
- **Solution:** Ensure you are using the correct base image in the Dockerfile. For Apple Silicon, you may need `--platform linux/amd64` in the compose file for specific ML libraries.

## Frontend Loading Indefinitely
- **Error:** The UI is visible but hangs on "Connecting to agents...".
- **Cause:** The frontend cannot communicate with the backend API.
- **Solution:** Check the browser console (F12). Ensure the `API_BASE_URL` in the frontend config points exactly to where FastAPI is running (e.g., `http://localhost:8000`). Check for CORS errors; if present, update `CORS_ORIGINS` in the backend `.env`.

## Data Format Problems
- **Error:** Agent trace says "Failed to parse CSV".
- **Cause:** The uploaded CSV has malformed rows, or uses semicolons instead of commas.
- **Solution:** Open the CSV in Excel/Numbers and re-export as standard Comma Separated Values. Ensure column headers have no trailing spaces.
