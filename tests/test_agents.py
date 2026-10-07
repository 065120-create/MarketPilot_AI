"""Comprehensive Tests for Multi-Agent Swarm and Governance Guardians."""
import pytest
import asyncio
from app.agents.campaign_performance import CampaignPerformanceAgent
from app.agents.customer_voice import CustomerVoiceAgent
from app.agents.segmentation import SegmentationAgent
from app.agents.journey import CustomerJourneyAgent
from app.agents.budget import BudgetAllocationAgent
from app.agents.quality import QualityGovernanceAgent
from app.agents.orchestrator import OrchestratorAgent

@pytest.mark.anyio
async def test_campaign_performance_agent(sample_campaign, sample_campaign_performance_df):
    agent = CampaignPerformanceAgent()
    datasets = {"performance": sample_campaign_performance_df.to_dict(orient="records")}
    result = await agent.analyze(sample_campaign, datasets)
    
    assert result["status"] == "success"
    assert "channel_performance" in result
    assert "raw_metrics" in result
    assert "total_spend" in result["raw_metrics"]
    assert result["raw_metrics"]["total_spend"] > 0

@pytest.mark.anyio
async def test_customer_voice_agent(sample_campaign, sample_customer_feedback_df):
    agent = CustomerVoiceAgent()
    datasets = {"feedback": sample_customer_feedback_df.to_dict(orient="records")}
    result = await agent.analyze(sample_campaign, datasets)
    
    assert result["status"] == "success"
    assert "sentiment_distribution" in result
    assert "positive" in result["sentiment_distribution"]
    assert "negative" in result["sentiment_distribution"]
    assert len(result.get("top_themes", [])) > 0

@pytest.mark.anyio
async def test_customer_segmentation_agent(sample_campaign, sample_customer_data_df):
    agent = SegmentationAgent()
    datasets = {"customer": sample_customer_data_df.to_dict(orient="records")}
    result = await agent.analyze(sample_campaign, datasets)
    
    assert result["status"] == "success"
    assert "raw_profiles" in result
    assert "insights" in result
    assert len(result["raw_profiles"]) > 0

@pytest.mark.anyio
async def test_customer_journey_agent(sample_campaign, sample_journey_df):
    agent = CustomerJourneyAgent()
    datasets = {"journey": sample_journey_df.to_dict(orient="records")}
    result = await agent.analyze(sample_campaign, datasets)
    
    assert result["status"] == "success"
    assert "funnel_data" in result
    assert len(result["funnel_data"]) > 0

@pytest.mark.anyio
async def test_budget_allocation_agent(sample_campaign, sample_campaign_performance_df):
    agent = BudgetAllocationAgent()
    datasets = {"performance": sample_campaign_performance_df.to_dict(orient="records")}
    result = await agent.analyze(sample_campaign, datasets)
    
    assert result["status"] == "success"
    assert "mathematical_recommendation" in result
    recom = result["mathematical_recommendation"]
    total = sum(recom.values())
    budget = sample_campaign["budget"]
    assert abs(total - budget) <= 10.0  # Floating point tolerance

@pytest.mark.anyio
async def test_quality_governance_budget_violation(sample_campaign):
    agent = QualityGovernanceAgent()
    # Construct a previous result where budget was maliciously/erroneously exceeded
    previous_results = {
        "budget": {
            "total_budget": 1000000,
            "mathematical_recommendation": {
                "Instagram": 600000,
                "YouTube": 600000,  # Sum = 1,200,000 > 1,000,000!
            }
        },
        "optimization": {"insights": {"summary": "Shift spend"}},
        "content": {"insights": {"summary": "Gen Z reels"}}
    }
    
    result = await agent.analyze(sample_campaign, {}, previous_results)
    assert result["status"] == "success"
    assert result["passed"] is False
    assert "budget" in result["failed_agents"]
    assert "budget" in result["feedback"]

@pytest.mark.anyio
async def test_quality_governance_valid_budget(sample_campaign):
    agent = QualityGovernanceAgent()
    previous_results = {
        "budget": {
            "total_budget": 1000000,
            "mathematical_recommendation": {
                "Instagram": 500000,
                "YouTube": 500000,  # Exact sum
            }
        },
        "optimization": {"insights": {"summary": "Shift spend"}},
        "content": {"insights": {"summary": "Gen Z reels"}}
    }
    
    result = await agent.analyze(sample_campaign, {}, previous_results)
    assert result["status"] == "success"
    # Even in fallback without LLM, budget constraint alone passes
    assert "budget" not in result["failed_agents"]

def test_orchestrator_planning(sample_campaign):
    orchestrator = OrchestratorAgent()
    # With only performance dataset
    plan_perf = orchestrator.plan_execution(sample_campaign, {"performance": []})
    assert "campaign_performance" in plan_perf
    assert "customer_voice" not in plan_perf
    assert "budget" in plan_perf
    assert "quality" in plan_perf

    # With full datasets
    plan_full = orchestrator.plan_execution(sample_campaign, {
        "performance": [],
        "feedback": [],
        "customer": [],
        "journey": []
    })
    assert "campaign_performance" in plan_full
    assert "customer_voice" in plan_full
    assert "segmentation" in plan_full
    assert "journey" in plan_full
    assert "quality" in plan_full
    assert "synthesis" in plan_full
