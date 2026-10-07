"""End-to-End Workflow and Dynamic Multi-Brand Pipeline Tests."""
import pytest
from app.agents.orchestrator import OrchestratorAgent
from app.state import job_store

@pytest.mark.anyio
async def test_full_demo_workflow(sample_campaign, sample_campaign_performance_df, sample_customer_feedback_df):
    orchestrator = OrchestratorAgent()
    datasets = {
        "performance": sample_campaign_performance_df.to_dict(orient="records"),
        "feedback": sample_customer_feedback_df.to_dict(orient="records")
    }
    job_id = job_store.create_job(sample_campaign)
    job_store.update_status(job_id, "analyzing")
    
    results = await orchestrator.execute(sample_campaign, datasets, job_id=job_id)
    
    assert "status" in results
    assert results["status"] in ["completed", "approved", "success"]
    assert "campaign_performance" in results
    assert "customer_voice" in results
    assert "budget" in results
    assert "quality" in results
    assert "synthesis" in results
    
    # Verify budget constraint respected in final output
    budget_alloc = results["budget"]["mathematical_recommendation"]
    assert abs(sum(budget_alloc.values()) - sample_campaign["budget"]) <= 10.0

@pytest.mark.anyio
async def test_custom_brand_workflow(sample_campaign_performance_df):
    """Test that pipeline works for ANY brand (e.g., Nike, Zomato, or unknown brand)."""
    custom_campaign = {
        "brand": "Nike",
        "campaign_name": "Air Max Next-Gen Launch",
        "industry": "Athletic Footwear & Apparel",
        "objective": "Drive D2C e-commerce sneaker pre-orders",
        "target_audience": "Streetwear enthusiasts and marathon runners",
        "geography": "Global Metros",
        "budget": 2500000,
        "channels": ["Instagram", "YouTube", "Influencer", "Google Ads"],
        "duration": "1 month"
    }
    
    orchestrator = OrchestratorAgent()
    datasets = {
        "performance": sample_campaign_performance_df.to_dict(orient="records")
    }
    
    job_id = job_store.create_job(custom_campaign)
    results = await orchestrator.execute(custom_campaign, datasets, job_id=job_id)
    
    assert results["status"] in ["completed", "approved", "success"]
    assert "budget" in results
    # Verify the budget matches Nike's 2,500,000 budget, NOT Coca-Cola's 1,000,000
    nike_budget = sum(results["budget"]["mathematical_recommendation"].values())
    assert abs(nike_budget - custom_campaign["budget"]) <= 10.0
