"""Tests for MarketPilot Analytical and Optimization Tools."""
import pytest
import pandas as pd
from app.tools.data_analysis import (
    analyze_dataframe,
    calculate_metrics,
    compare_channels,
)
from app.tools.sentiment import (
    analyze_sentiment,
    batch_sentiment,
    extract_themes,
)
from app.tools.journey_analysis import (
    build_funnel,
    calculate_stage_conversion,
    identify_dropoffs,
)
from app.tools.budget_optimizer import (
    optimize_budget,
    simulate_reallocation,
    validate_budget_constraints,
)

def test_analyze_dataframe(sample_campaign_performance_df):
    summary = analyze_dataframe(sample_campaign_performance_df, "campaign_performance")
    assert summary["row_count"] == 7
    assert summary["column_count"] >= 8
    assert "numeric_summary" in summary
    assert "conversions" in summary["numeric_columns"]

def test_calculate_metrics(sample_campaign_performance_df):
    metrics = calculate_metrics(sample_campaign_performance_df)
    assert "total_impressions" in metrics
    assert "total_clicks" in metrics
    assert "total_spend" in metrics
    assert "total_conversions" in metrics
    assert "overall_ctr" in metrics
    assert metrics["total_spend"] > 0
    assert metrics["total_clicks"] > 0

def test_compare_channels(sample_campaign_performance_df):
    comparison = compare_channels(
        sample_campaign_performance_df,
        channel_col="channel",
        metric_cols=["spend", "conversions", "revenue"]
    )
    assert isinstance(comparison, (dict, list))

def test_analyze_sentiment():
    pos = analyze_sentiment("This campaign is fantastic, I loved the personalized bottle!")
    assert pos["sentiment"] == "positive"
    assert pos["score"] > 0

    neg = analyze_sentiment("Terrible experience, horrible service and disappointing delay.")
    assert neg["sentiment"] == "negative"
    assert neg["score"] < 0

    neu = analyze_sentiment("The item arrived on Tuesday.")
    assert neu["sentiment"] in ["neutral", "positive", "negative"]

def test_batch_sentiment():
    texts = [
        "Loved the concept, great work!",
        "Hated the ads, annoying and awful.",
        "Neutral statement."
    ]
    results = batch_sentiment(texts)
    assert len(results) == 3
    assert results[0]["sentiment"] == "positive"
    assert results[1]["sentiment"] == "negative"

def test_extract_themes():
    reviews = [
        "Loved the great product quality and personalized bottle",
        "Worst customer service and delayed delivery problem",
        "Fantastic experience with the super helpful team"
    ]
    themes = extract_themes(reviews, n_themes=3)
    assert len(themes) > 0
    assert "theme" in themes[0]
    assert "count" in themes[0]

def test_build_funnel_and_conversions(sample_journey_df):
    funnel = build_funnel(sample_journey_df, stage_col="stage", customer_col="customer_id")
    assert len(funnel) > 0
    conversions = calculate_stage_conversion(funnel)
    assert isinstance(conversions, list)
    dropoffs = identify_dropoffs(funnel)
    assert isinstance(dropoffs, list)

def test_optimize_budget_mathematical_guarantee():
    current_alloc = {
        "Instagram": 200000,
        "YouTube": 300000,
        "Google Ads": 300000,
        "Facebook": 200000,
    }
    performance = {
        "Instagram": 4.5,
        "YouTube": 2.8,
        "Google Ads": 5.2,
        "Facebook": 1.9,
    }
    total_budget = 1000000
    constraints = {
        "min_spend": {"Instagram": 50000, "Google Ads": 50000},
        "max_spend": {"Google Ads": 500000}
    }
    
    optimized = optimize_budget(current_alloc, total_budget, performance, constraints)
    
    # Must sum to total budget within float precision
    assert abs(sum(optimized.values()) - total_budget) < 1.0
    # Higher ROI channels must receive substantial allocation
    assert optimized["Google Ads"] > optimized["Facebook"]
    # Constraints respected
    assert optimized["Instagram"] >= 50000
    assert optimized["Google Ads"] <= 500000

def test_simulate_reallocation():
    current = {"Instagram": 100000, "Facebook": 100000}
    proposed = {"Instagram": 150000, "Facebook": 50000}
    perf = {"Instagram": 4.0, "Facebook": 2.0}
    
    sim = simulate_reallocation(current, proposed, perf)
    assert sim["proposed_estimated_return"] > sim["current_estimated_return"]
    assert sim["lift"] > 0
    assert sim["lift_percentage"] > 0

def test_validate_budget_constraints():
    valid_alloc = {"A": 500000, "B": 500000}
    validation = validate_budget_constraints(valid_alloc, 1000000, {})
    assert len(validation["issues"]) == 0
    
    invalid_alloc = {"A": 700000, "B": 500000}
    validation_err = validate_budget_constraints(invalid_alloc, 1000000, {})
    assert len(validation_err["issues"]) > 0
