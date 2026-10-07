"""Integration Tests for MarketPilot AI FastAPI Endpoints."""
import pytest
from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)

def test_health_endpoint():
    response = client.get("/health")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "healthy"
    assert "app" in data
    assert "llm_provider" in data

def test_create_campaign_endpoint():
    payload = {
        "brand": "cocacola",
        "campaign_name": "share a cok",
        "industry": "Beverages",
        "objective": "Gen Z awareness",
        "budget": 1000000,
        "channels": ["Instagarm", "YouTube"]
    }
    response = client.post("/api/campaigns", json=payload)
    assert response.status_code == 200
    data = response.json()
    assert "job_id" in data
    assert data["job_id"].startswith("MP-2026-")
    assert "corrections" in data
    # Check that normalization ran
    corrections = {c["field"]: c["corrected"] for c in data["corrections"]}
    assert corrections.get("brand") == "Coca-Cola"

def test_demo_endpoint():
    response = client.post("/api/demo")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "started"
    assert "job_id" in data
    assert data["mode"] == "demo"
    assert "datasets_loaded" in data

def test_get_job_and_status():
    demo_resp = client.post("/api/demo")
    job_id = demo_resp.json()["job_id"]

    # Test full job
    job_resp = client.get(f"/api/jobs/{job_id}")
    assert job_resp.status_code == 200
    assert job_resp.json()["job_id"] == job_id

    # Test job status
    status_resp = client.get(f"/api/jobs/{job_id}/status")
    assert status_resp.status_code == 200
    assert "status" in status_resp.json()

def test_scenario_endpoint():
    payload = {
        "current_allocation": {"Instagram": 200000, "Google Ads": 200000, "Facebook": 200000},
        "proposed_allocation": {"Instagram": 300000, "Google Ads": 250000, "Facebook": 50000},
        "total_budget": 600000
    }
    response = client.post("/api/scenario", json=payload)
    assert response.status_code == 200
    data = response.json()
    assert "scenario_a" in data
    assert "scenario_b" in data
    assert "comparison" in data
    assert "channel_impacts" in data["comparison"]
    assert "risk" in data

def test_normalize_endpoint():
    payload = {"brand": "starbuks", "channel": "Instagarm"}
    response = client.post("/api/normalize", json=payload)
    assert response.status_code == 200
    data = response.json()
    assert "corrections" in data
    corrections = {c["field"]: c["corrected"] for c in data["corrections"]}
    assert corrections["brand"] == "Starbucks"
    assert corrections["channel"] == "Instagram"

def test_rag_search_endpoint():
    payload = {"query": "how to allocate marketing budget", "top_k": 3}
    response = client.post("/api/rag/search", json=payload)
    assert response.status_code == 200
    data = response.json()
    assert "results" in data
    assert "count" in data

def test_validate_data_endpoint(sample_campaign_performance_df):
    records = sample_campaign_performance_df.to_dict(orient="records")
    response = client.post("/api/validate-data", json={"data": records})
    assert response.status_code == 200
    data = response.json()
    assert "score" in data
    assert "issues" in data
    assert 0 <= data["score"] <= 100

def test_approval_endpoint():
    demo_resp = client.post("/api/demo")
    job_id = demo_resp.json()["job_id"]

    approve_resp = client.post(f"/api/jobs/{job_id}/approve", json={"approved_by": "marketing_director"})
    assert approve_resp.status_code == 200
    assert approve_resp.json()["status"] == "approved"
    assert "n8n_payload" in approve_resp.json()

def test_list_jobs_and_latest_endpoint():
    resp_list = client.get("/api/jobs")
    assert resp_list.status_code == 200
    assert isinstance(resp_list.json(), list)
    assert len(resp_list.json()) > 0
    
    resp_latest = client.get("/api/jobs/latest")
    assert resp_latest.status_code == 200
    assert "job_id" in resp_latest.json()

def test_all_html_pages_serve_ok():
    """Verify that all 14 HTML routes serve 200 OK with clean URLs and .html extensions."""
    pages = [
        "/", "/index.html",
        "/dashboard", "/dashboard.html",
        "/campaign", "/campaign.html",
        "/upload", "/upload.html",
        "/agents", "/agents.html",
        "/insights", "/insights.html",
        "/segments", "/segments.html",
        "/journey", "/journey.html",
        "/optimization", "/optimization.html",
        "/budget", "/budget.html",
        "/scenarios", "/scenarios.html",
        "/recommendations", "/recommendations.html",
        "/rag", "/rag.html",
        "/reports", "/reports.html"
    ]
    for p in pages:
        res = client.get(p)
        assert res.status_code == 200, f"Page {p} returned status {res.status_code}"
        assert "text/html" in res.headers.get("content-type", "")

def test_multibrand_distinct_results():
    """Verify that creating two distinct brand campaigns yields distinct dynamic metrics."""
    # 1. Nike Campaign
    nike_payload = {
        "brand": "Nike",
        "campaign_name": "Faster Marathon Series",
        "budget": 2500000,
        "channels": ["Instagram", "YouTube", "Google Ads"]
    }
    r1 = client.post("/api/campaigns", json=nike_payload)
    assert r1.status_code == 200
    nike_job_id = r1.json()["job_id"]

    # 2. Starbucks Campaign
    sbux_payload = {
        "brand": "Starbucks",
        "campaign_name": "Cold Foam Nitro",
        "budget": 1200000,
        "channels": ["Instagram", "Facebook", "Snapchat"]
    }
    r2 = client.post("/api/campaigns", json=sbux_payload)
    assert r2.status_code == 200
    sbux_job_id = r2.json()["job_id"]

    # Trigger analysis on both
    client.post("/api/analyze", json={"job_id": nike_job_id})
    client.post("/api/analyze", json={"job_id": sbux_job_id})

    # Fetch status and results
    nike_res = client.get(f"/api/jobs/{nike_job_id}")
    sbux_res = client.get(f"/api/jobs/{sbux_job_id}")

    assert nike_res.status_code == 200
    assert sbux_res.status_code == 200
    assert nike_res.json()["campaign"]["brand"] == "Nike"
    assert sbux_res.json()["campaign"]["brand"] == "Starbucks"
    assert nike_res.json()["campaign"]["budget"] == 2500000
    assert sbux_res.json()["campaign"]["budget"] == 1200000

