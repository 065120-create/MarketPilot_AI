"""Tests for Data Quality Validation and Audit Engine."""
import pytest
import pandas as pd
import numpy as np
from app.tools.validator import (
    detect_dataset_type,
    check_data_quality_score,
    validate_dataset,
    auto_fix_issues,
    validate_columns,
    suggest_column_mapping,
)

def test_detect_campaign_performance_type(sample_campaign_performance_df):
    dataset_type = detect_dataset_type(sample_campaign_performance_df)
    assert dataset_type == "campaign_performance"

def test_detect_customer_feedback_type(sample_customer_feedback_df):
    dataset_type = detect_dataset_type(sample_customer_feedback_df)
    assert dataset_type == "customer_feedback"

def test_detect_customer_data_type(sample_customer_data_df):
    dataset_type = detect_dataset_type(sample_customer_data_df)
    assert dataset_type == "customer_data"

def test_detect_customer_journey_type(sample_journey_df):
    dataset_type = detect_dataset_type(sample_journey_df)
    assert dataset_type == "customer_journey"

def test_detect_unknown_type():
    df = pd.DataFrame({"random_foo": [1, 2], "random_bar": [3, 4]})
    assert detect_dataset_type(df) == "unknown"

def test_data_quality_score_clean_data(sample_campaign_performance_df):
    score = check_data_quality_score(sample_campaign_performance_df)
    assert 90 <= score <= 100

def test_validate_dataset_with_anomalies(sample_campaign_performance_df):
    df_dirty = sample_campaign_performance_df.copy()
    # Add a duplicate row
    df_dirty = pd.concat([df_dirty, df_dirty.iloc[[0]]], ignore_index=True)
    # Add negative spend
    df_dirty.loc[1, 'spend'] = -500.0
    # Add missing value
    df_dirty.loc[2, 'clicks'] = np.nan

    report = validate_dataset(df_dirty)
    assert report.score < 100
    assert len(report.issues) >= 3
    issues_str = " ".join(report.issues)
    assert "duplicate" in issues_str
    assert "negative" in issues_str
    assert "missing" in issues_str

def test_auto_fix_issues(sample_campaign_performance_df):
    df_dirty = sample_campaign_performance_df.copy()
    df_dirty = pd.concat([df_dirty, df_dirty.iloc[[0]]], ignore_index=True)
    df_dirty.loc[1, 'spend'] = -250.0
    df_dirty.loc[2, 'conversions'] = np.nan

    report = validate_dataset(df_dirty)
    fixed_df, fixes = auto_fix_issues(df_dirty, report.issues)
    
    assert len(fixes) > 0
    # Duplicates should be dropped
    assert not fixed_df.duplicated().any()
    # Negative spend should be clipped to 0
    assert (fixed_df['spend'] >= 0).all()
    # Missing numeric should be filled
    assert not fixed_df['conversions'].isnull().any()

def test_validate_columns():
    df = pd.DataFrame({"channel": ["FB"], "spend": [100]})
    res = validate_columns(df, ["channel", "spend", "conversions", "impressions"])
    assert res["is_valid"] is False
    assert "conversions" in res["missing_columns"]
    assert "impressions" in res["missing_columns"]

def test_suggest_column_mapping():
    df_cols = ["ad_spend", "num_clicks", "user_impressions"]
    target_schema = ["spend", "clicks", "impressions", "revenue"]
    suggestions = suggest_column_mapping(df_cols, target_schema)
    assert len(suggestions) == len(target_schema)
    mapped_targets = {s["target"]: s["source"] for s in suggestions}
    assert mapped_targets["spend"] == "ad_spend"
    assert mapped_targets["clicks"] == "num_clicks"
    assert mapped_targets["impressions"] == "user_impressions"
    assert mapped_targets["revenue"] is None
