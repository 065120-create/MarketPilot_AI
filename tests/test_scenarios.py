"""Tests for What-If Scenario Simulation and Channel Sensitivity Analysis."""
import pytest
from app.tools.budget_optimizer import simulate_reallocation, optimize_budget

def test_scenario_comparison_lift():
    current_allocation = {
        "Instagram": 200000,
        "YouTube": 200000,
        "Facebook": 200000,
    }
    # Shifting spend from low ROAS (Facebook) to high ROAS (Instagram)
    proposed_allocation = {
        "Instagram": 400000,
        "YouTube": 150000,
        "Facebook": 50000,
    }
    performance_roas = {
        "Instagram": 4.2,
        "YouTube": 2.5,
        "Facebook": 1.4,
    }
    
    sim = simulate_reallocation(current_allocation, proposed_allocation, performance_roas)
    
    # Current: 200k*4.2 + 200k*2.5 + 200k*1.4 = 840k + 500k + 280k = 1,620,000
    assert sim["current_estimated_return"] == 1620000
    # Proposed: 400k*4.2 + 150k*2.5 + 50k*1.4 = 1680k + 375k + 70k = 2,125,000
    assert sim["proposed_estimated_return"] == 2125000
    assert sim["lift"] == 505000
    assert sim["lift_percentage"] > 30.0

def test_scenario_budget_conservation():
    total_budget = 500000
    allocations = {"Google Ads": 250000, "Instagram": 250000}
    performance = {"Google Ads": 3.8, "Instagram": 4.5}
    
    optimized = optimize_budget(allocations, total_budget, performance)
    # Total sum of reallocation must strictly match total_budget
    assert abs(sum(optimized.values()) - total_budget) < 1.0

def test_scenario_channel_sensitivity():
    # If a channel drops in ROAS, optimizer shifts capital away from it
    total_budget = 300000
    allocations = {"Channel_A": 150000, "Channel_B": 150000}
    
    perf_scenario_1 = {"Channel_A": 5.0, "Channel_B": 1.0}
    opt_1 = optimize_budget(allocations, total_budget, perf_scenario_1)
    
    perf_scenario_2 = {"Channel_A": 1.0, "Channel_B": 5.0}
    opt_2 = optimize_budget(allocations, total_budget, perf_scenario_2)
    
    assert opt_1["Channel_A"] > opt_1["Channel_B"]
    assert opt_2["Channel_B"] > opt_2["Channel_A"]
