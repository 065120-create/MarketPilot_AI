import pandas as pd
import numpy as np
from typing import Dict, Any, List

def calculate_current_allocation(df: pd.DataFrame, channel_col: str, spend_col: str) -> dict:
    if channel_col not in df.columns or spend_col not in df.columns:
        return {"error": "Required columns not found"}
        
    total_spend = df[spend_col].sum()
    allocation = df.groupby(channel_col)[spend_col].sum().reset_index()
    allocation['percentage'] = (allocation[spend_col] / total_spend) * 100 if total_spend > 0 else 0
    
    return allocation.to_dict('records')

def calculate_marginal_returns(channel_data: List[Dict[str, float]]) -> dict:
    # Expects list of dicts with 'channel', 'spend', 'return' (e.g., revenue or conversions)
    returns = {}
    for data in channel_data:
        channel = data.get('channel')
        spend = data.get('spend', 0)
        ret = data.get('return', 0)
        roi = (ret / spend) if spend > 0 else 0
        returns[channel] = roi
    return returns

def optimize_budget(allocations: dict, total_budget: float, performance_data: dict, constraints: dict = None) -> dict:
    """
    Real mathematical optimization (heuristic approach using performance-weighted allocation)
    allocations: dict mapping channel to current spend
    performance_data: dict mapping channel to ROI or ROAS
    constraints: dict with 'min_spend' and 'max_spend' dicts mapping channel to limits
    """
    channels = list(allocations.keys())
    if not channels:
        return {}
        
    if constraints is None:
        constraints = {"min_spend": {}, "max_spend": {}}
        
    min_spend = constraints.get("min_spend", {})
    max_spend = constraints.get("max_spend", {})
    
    # Ensure min spends are met
    optimized = {}
    remaining_budget = total_budget
    
    for ch in channels:
        min_s = min_spend.get(ch, 0)
        optimized[ch] = min_s
        remaining_budget -= min_s
        
    if remaining_budget < 0:
        return {"error": "Total budget is less than sum of minimum constraints"}
        
    # Calculate performance weights for remaining budget
    # Shift performance data to be strictly positive for weighting
    min_perf = min([performance_data.get(ch, 0) for ch in channels] + [0])
    shift = abs(min_perf) + 1 # Ensure strictly positive
    
    weights = {ch: performance_data.get(ch, 0) + shift for ch in channels}
    total_weight = sum(weights.values())
    
    # Distribute remaining budget proportionally to weights, respecting max constraints
    distributable_channels = list(channels)
    
    while remaining_budget > 0.01 and distributable_channels:
        total_w = sum(weights[ch] for ch in distributable_channels)
        if total_w == 0:
            # Distribute evenly if all weights are 0
            even_share = remaining_budget / len(distributable_channels)
            for ch in distributable_channels:
                optimized[ch] += even_share
            remaining_budget = 0
            break
            
        allocation_step = remaining_budget
        for ch in distributable_channels[:]:
            share = allocation_step * (weights[ch] / total_w)
            proposed = optimized[ch] + share
            max_s = max_spend.get(ch, float('inf'))
            
            if proposed > max_s:
                optimized[ch] = max_s
                remaining_budget -= (max_s - (proposed - share))
                distributable_channels.remove(ch)
            else:
                optimized[ch] = proposed
                remaining_budget -= share
                
        # If no constraints were hit, remaining_budget should be effectively 0
        
    # Total must equal available budget exactly (due to float math, fix rounding)
    current_total = sum(optimized.values())
    diff = total_budget - current_total
    if abs(diff) > 0.001 and distributable_channels:
        optimized[distributable_channels[0]] += diff
        
    return optimized

def simulate_reallocation(current: dict, proposed: dict, performance_data: dict) -> dict:
    current_return = sum(current.get(ch, 0) * performance_data.get(ch, 0) for ch in current)
    proposed_return = sum(proposed.get(ch, 0) * performance_data.get(ch, 0) for ch in proposed)
    
    return {
        "current_estimated_return": current_return,
        "proposed_estimated_return": proposed_return,
        "lift": proposed_return - current_return,
        "lift_percentage": ((proposed_return - current_return) / current_return * 100) if current_return > 0 else 0
    }

def validate_budget_constraints(allocation: dict, total_budget: float, constraints: dict) -> dict:
    total_allocated = sum(allocation.values())
    issues = []
    
    if abs(total_allocated - total_budget) > 0.01:
        issues.append(f"Total allocated ({total_allocated}) does not match budget ({total_budget})")
        
    min_spend = constraints.get("min_spend", {})
    max_spend = constraints.get("max_spend", {})
    
    for ch, spend in allocation.items():
        if ch in min_spend and spend < min_spend[ch] - 0.01:
            issues.append(f"Channel {ch} spend ({spend}) is below minimum ({min_spend[ch]})")
        if ch in max_spend and spend > max_spend[ch] + 0.01:
            issues.append(f"Channel {ch} spend ({spend}) is above maximum ({max_spend[ch]})")
            
    return {
        "is_valid": len(issues) == 0,
        "issues": issues
    }
