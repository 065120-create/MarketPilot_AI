"""
Tests for New Campaign Workflow State Machine, Normalization & Swarm Execution Separation.
"""
import pytest
from fastapi.testclient import TestClient
from app.main import app
from app.state import job_store
from app.tools.normalization import (
    normalize_brand,
    normalize_channel,
    normalize_campaign,
    normalize_geography,
    batch_normalize
)

client = TestClient(app)

def test_high_confidence_spelling_corrections():
    """Verify core required spelling normalization test cases."""
    # 1. Brand: cocacola -> Coca-Cola
    brand_res = normalize_brand("cocacola")
    assert brand_res["original"] == "cocacola"
    assert brand_res["corrected"] == "Coca-Cola"
    assert brand_res["confidence"] >= 0.90
    assert brand_res["requires_action"] is True

    # 2. Channel: Instagarm -> Instagram
    ch_res = normalize_channel("Instagarm")
    assert ch_res["original"] == "Instagarm"
    assert ch_res["corrected"] == "Instagram"
    assert ch_res["confidence"] >= 0.90
    assert ch_res["requires_action"] is True

    # 3. Campaign: Share a cok -> Share a Coke
    camp_res = normalize_campaign("Share a cok")
    assert camp_res["original"] == "Share a cok"
    assert camp_res["corrected"] == "Share a Coke"
    assert camp_res["confidence"] >= 0.90
    assert camp_res["requires_action"] is True

    # 4. Geography: delhi ncr -> Delhi NCR
    geo_res = normalize_geography("delhi ncr")
    assert geo_res["original"] == "delhi ncr"
    assert geo_res["corrected"] == "Delhi NCR"
    assert geo_res["confidence"] >= 0.90
    assert geo_res["requires_action"] is True

def test_ambiguous_normalization_behavior():
    """Verify ambiguous or unknown entities do not produce fake 0% confidence accepted events."""
    # Unknown brand
    res = normalize_brand("BrandXYZArbitraryCorp")
    assert res["requires_action"] is False
    assert res["status"] == "unresolved"
    assert res["confidence"] < 0.60
    assert "Could not confidently normalize" in res.get("message", "")

def test_multi_location_geography():
    """Verify comma-separated locations normalize each component with high confidence."""
    geo_res = normalize_geography("delhi ncr, mumbai, bangalore")
    assert geo_res["corrected"] == "Delhi NCR, Mumbai, Bangalore"
    assert geo_res["confidence"] >= 0.85
    assert geo_res["requires_action"] is True

def test_swarm_does_not_start_during_campaign_creation():
    """Campaign creation and agent execution must be separate stages."""
    payload = {
        "brand": "cocacola",
        "campaign_name": "Share a cok — Gen Z Digital",
        "industry": "FMCG / Beverages",
        "budget": 1000000,
        "geography": "delhi ncr, mumbai, bangalore",
        "channels": ["Instagarm", "YouTube", "FB", "Google Ads", "Snapchat"],
        "objective": "Increase Engagement & Conversion"
    }

    # Step 1: Create campaign
    resp = client.post("/api/campaigns", json=payload)
    assert resp.status_code == 200
    data = resp.json()
    job_id = data["job_id"]
    assert job_id is not None
    assert data["status"] == "created"

    # Verify swarm has NOT started yet
    job = job_store.get_job(job_id)
    assert job["status"] == "created"
    assert "results" not in job or not job.get("results")

def test_swarm_starts_after_explicit_trigger():
    """Swarm must run only when explicitly triggered via /api/analyze."""
    payload = {
        "brand": "Nike",
        "campaign_name": "Summer Running Fast",
        "industry": "Athletic Footwear",
        "budget": 2000000,
        "geography": "Mumbai, Bangalore",
        "channels": ["Instagram", "Google Ads", "YouTube"],
        "objective": "Customer Acquisition & ROAS"
    }

    # Create campaign
    create_resp = client.post("/api/campaigns", json=payload)
    job_id = create_resp.json()["job_id"]

    # Explicit trigger: Run Multi-Agent Analysis
    analyze_resp = client.post("/api/analyze", json={"job_id": job_id})
    assert analyze_resp.status_code == 200
    assert analyze_resp.json()["status"] == "analysis_started"

    # Status check
    status_resp = client.get(f"/api/jobs/{job_id}/status")
    assert status_resp.status_code == 200

def test_custom_nike_campaign_normalization_and_workflow():
    """Test custom Nike campaign with typos (nike, Instagarm, YT)."""
    norm_resp = client.post("/api/normalize", json={
        "brand": "nike",
        "channels": ["Instagarm", "YT", "Google Ads"],
        "geography": "mumbai, blr"
    })
    assert norm_resp.status_code == 200
    corrections = norm_resp.json()["corrections"]
    
    orig_to_corr = {c["original"]: c["corrected"] for c in corrections}
    assert orig_to_corr.get("nike") == "Nike"
    assert orig_to_corr.get("Instagarm") == "Instagram"
    assert orig_to_corr.get("YT") == "YouTube"

def test_full_coca_cola_demo_workflow():
    """Verify full demo mode operates reliably through complete multi-agent lifecycle."""
    demo_resp = client.post("/api/demo")
    assert demo_resp.status_code == 200
    data = demo_resp.json()
    job_id = data["job_id"]
    assert data["status"] == "started"
    assert data["mode"] == "demo"
    assert "performance" in data["datasets_loaded"]
