import logging
import time
import pandas as pd
from typing import Dict, Any, Optional
from .llm_provider import get_llm

logger = logging.getLogger("marketpilot.budget")

class BudgetAllocationAgent:
    def __init__(self):
        self.llm = get_llm()
        
    async def analyze(self, campaign: Dict[str, Any], datasets: Dict[str, Any], previous_results: Optional[Dict[str, Any]] = None, retry_feedback: Optional[str] = None) -> Dict[str, Any]:
        """Calculate optimal budget allocation."""
        logger.info("Starting Budget Allocation Analysis")
        start_time = time.time()
        
        try:
            raw_data = datasets.get("performance") if datasets else None
            if raw_data is None:
                # Baseline channel allocation fallback from campaign definition
                channels = campaign.get("channels", ["Instagram", "Google Ads", "YouTube"])
                if isinstance(channels, str):
                    channels = [c.strip() for c in channels.split(",") if c.strip()]
                if not channels:
                    channels = ["Instagram", "Google Ads", "YouTube"]
                total_budget = float(campaign.get("total_budget") or campaign.get("budget") or 1000000)
                even_split = round(total_budget / len(channels), 2)
                current_allocation = {ch: even_split for ch in channels}
                recommended_allocation = {ch: even_split for ch in channels}
                performance_metrics = {ch: {'roas': 3.0, 'cpa': 50.0, 'current_spend': even_split} for ch in channels}
            else:
                df = pd.DataFrame(raw_data) if isinstance(raw_data, (list, dict)) else raw_data.copy()
                if df.empty or 'channel' not in df.columns or 'spend' not in df.columns:
                    channels = campaign.get("channels", ["Instagram", "Google Ads", "YouTube"])
                    total_budget = float(campaign.get("total_budget") or campaign.get("budget") or 1000000)
                    even_split = round(total_budget / len(channels), 2)
                    current_allocation = {ch: even_split for ch in channels}
                    recommended_allocation = {ch: even_split for ch in channels}
                    performance_metrics = {ch: {'roas': 3.0, 'cpa': 50.0, 'current_spend': even_split} for ch in channels}
                else:
                    total_budget = campaign.get("total_budget") or campaign.get("budget") or df['spend'].sum()
                    channel_group = df.groupby('channel').sum(numeric_only=True)
                    current_allocation = {}
                    performance_metrics = {}
                    for channel, row in channel_group.iterrows():
                        spend = row['spend']
                        current_allocation[channel] = spend
                        roas = row['revenue'] / spend if 'revenue' in row and spend > 0 else 0
                        cpa = spend / row['conversions'] if 'conversions' in row and row['conversions'] > 0 else float('inf')
                        performance_metrics[channel] = {'roas': float(roas), 'cpa': float(cpa), 'current_spend': float(spend)}
                    total_roas = sum(metrics['roas'] for metrics in performance_metrics.values())
                    recommended_allocation = {}
                    if total_roas > 0:
                        for channel, metrics in performance_metrics.items():
                            recommended_spend = total_budget * (metrics['roas'] / total_roas)
                            recommended_allocation[channel] = round(float(recommended_spend), 2)
                    else:
                        even_split = total_budget / len(performance_metrics)
                        recommended_allocation = {ch: round(float(even_split), 2) for ch in performance_metrics.keys()}
            
            prompt = f"""
            Analyze the budget allocation and provide recommendations.
            
            Total Budget Constraint: {total_budget}
            
            Current Allocation and Performance:
            {performance_metrics}
            
            Mathematically Optimized Allocation (based on ROAS):
            {recommended_allocation}
            
            Retry Feedback (if any): {retry_feedback}
            
            Provide a structured JSON output with:
            - 'allocation_strategy': Overall strategy description
            - 'channel_recommendations': Array of objects with:
                - 'channel': Channel name
                - 'recommended_spend': Amount
                - 'change_percentage': % increase/decrease
                - 'reasoning': Why this allocation is recommended
            - 'budget_warnings': Any warnings about hitting constraints or diminishing returns
            """
            
            llm_insights = await self.llm.generate_json(
                prompt=prompt,
                system_prompt="You are an expert media buyer and budget optimization specialist."
            )
            
            result = {
                "status": "success",
                "current_allocation": current_allocation,
                "mathematical_recommendation": recommended_allocation,
                "total_budget": float(total_budget),
                "insights": llm_insights,
                "execution_time_ms": int((time.time() - start_time) * 1000)
            }
            return result
            
        except Exception as e:
            logger.error(f"Error in BudgetAllocationAgent: {e}")
            return {"status": "error", "message": str(e)}
