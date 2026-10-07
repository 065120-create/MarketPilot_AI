"""Tests for Input Normalization and Entity Resolution Tools."""
import pytest
from app.tools.normalization import (
    normalize_brand,
    normalize_campaign,
    normalize_channel,
    normalize_geography,
    normalize_input,
    batch_normalize,
)

# Core brand normalization tests
def test_normalize_brand_cocacola():
    result = normalize_brand("cocacola")
    assert result["original"] == "cocacola"
    assert result["corrected"] == "Coca-Cola"
    assert result["confidence"] >= 0.90
    assert result["requires_action"] is True
    assert result["status"] == "suggested"

def test_normalize_brand_nike():
    result = normalize_brand("nike")
    assert result["original"] == "nike"
    assert result["corrected"] == "Nike"
    assert result["confidence"] >= 0.90

def test_normalize_brand_starbucks():
    result = normalize_brand("starbuks")
    assert result["original"] == "starbuks"
    assert result["corrected"] == "Starbucks"
    assert result["confidence"] >= 0.90
    assert result["status"] == "suggested"

# Channel normalization tests
def test_normalize_channel_instagram():
    result = normalize_channel("Instagarm")
    assert result["original"] == "Instagarm"
    assert result["corrected"] == "Instagram"
    assert result["confidence"] >= 0.90
    assert result["requires_action"] is True
    assert result["status"] == "suggested"

def test_normalize_channel_youtube():
    result = normalize_channel("YouTube")
    assert result["corrected"] == "YouTube"
    assert result["confidence"] == 1.0
    assert result["requires_action"] is False
    assert result["status"] == "exact"

# Geography normalization tests
def test_normalize_geography_delhi_ncr():
    result = normalize_geography("delhi ncr")
    assert result["original"] == "delhi ncr"
    assert result["corrected"] == "Delhi NCR"
    assert result["confidence"] >= 0.90
    assert result["requires_action"] is True
    assert result["status"] == "suggested"

def test_normalize_geography_multi_cities():
    result = normalize_geography("delhi ncr, mumbai, bangalore")
    assert result["original"] == "delhi ncr, mumbai, bangalore"
    assert result["corrected"] == "Delhi NCR, Mumbai, Bangalore"
    assert result["confidence"] >= 0.90
    assert result["requires_action"] is True

def test_normalize_geography_clean():
    result = normalize_geography("Delhi")
    assert result["original"] == "Delhi"
    assert result["corrected"] == "Delhi"
    assert result["confidence"] == 1.0
    assert result["requires_action"] is False
    assert result["status"] == "exact"

# Campaign title normalization tests
def test_normalize_campaign_share_a_cok():
    result = normalize_campaign("Share a cok")
    assert result["original"] == "Share a cok"
    assert result["corrected"] == "Share a Coke"
    assert result["confidence"] >= 0.90
    assert result["requires_action"] is True
    assert result["status"] == "suggested"

def test_normalize_campaign_clean():
    result = normalize_campaign("Summer Festival Blast")
    assert result["original"] == "Summer Festival Blast"
    assert result["corrected"] == "Summer Festival Blast"
    assert result["requires_action"] is False
    assert result["status"] == "exact"

# Unknown/Ambiguous brand handling (no fake accepted 0% confidence)
def test_normalize_unknown_brand():
    result = normalize_brand("ZyxOmega123NonExistent")
    assert result["original"] == "ZyxOmega123NonExistent"
    assert result["confidence"] < 0.5
    assert result["requires_action"] is False
    assert result["status"] == "unresolved"
    assert "Could not confidently normalize" in result.get("message", "")

# Batch normalization tests
def test_batch_normalize_comprehensive():
    inputs = {
        "brand": "cocacola",
        "channel": "Instagarm",
        "campaign_name": "Share a cok",
        "geography": "delhi ncr"
    }
    results = batch_normalize(inputs)
    assert len(results) == 4
    by_field = {r["field"]: r for r in results}
    assert by_field["brand"]["corrected"] == "Coca-Cola"
    assert by_field["channel"]["corrected"] == "Instagram"
    assert by_field["campaign_name"]["corrected"] == "Share a Coke"
    assert by_field["geography"]["corrected"] == "Delhi NCR"

def test_batch_normalize_channels_list():
    inputs = {
        "channels": ["Instagarm", "YouTube", "FB"]
    }
    results = batch_normalize(inputs)
    assert len(results) == 3
    corrections = {r["original"]: r["corrected"] for r in results}
    assert corrections["Instagarm"] == "Instagram"
    assert corrections["YouTube"] == "YouTube"
    assert corrections["FB"] == "Facebook"
