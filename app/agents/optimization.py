import logging
import time
import json
from typing import Dict, Any, Optional
from .llm_provider import get_llm

logger = logging.getLogger("marketpilot.optimization")

class CampaignOptimizationAgent:
    def __init__(self):
        self.llm = get_llm()
        
    async def analyze(self, campaign: Dict[str, Any], datasets: Dict[str, Any], previous_results: Dict[str, Any], retry_feedback: str = None) -> Dict[str, Any]:
        """Synthesize previous findings to generate optimization recommendations."""
        logger.info("Starting Campaign Optimization")
        start_time = time.time()
        
        try:
            # Extract key insights from previous agents
            context = {
                "performance": previous_results.get("campaign_performance", {}).get("insights"),
                "voice": previous_results.get("customer_voice", {}).get("insights"),
                "segments": previous_results.get("segmentation", {}).get("insights"),
                "journey": previous_results.get("journey", {}).get("insights")
            }
            
            prompt = f"""
            Based on the analysis from specialized agents, provide comprehensive campaign optimization recommendations.
            
            Context Data:
            {json.dumps(context, indent=2)}
            
            Campaign Goals:
            {campaign.get('goals', 'Maximize ROI and customer acquisition')}
            
            Retry Feedback (if any): {retry_feedback}
            
            Provide a structured JSON output with:
            - 'opportunities': An array of optimization opportunities. Each must include:
                - 'what': What to do
                - 'why': Why do it (evidence based on context)
                - 'expected_impact': Expected positive outcome
                - 'risk': Potential risks or downsides
                - 'confidence': High/Medium/Low
            - 'prioritization': A prioritized list of which opportunities to tackle first (by index or short name)
            """
            
            llm_insights = await self.llm.generate_json(
                prompt=prompt,
                system_prompt="You are an expert performance marketing optimizer who synthesis data into actionable strategies."
            )
            
            result = {
                "status": "success",
                "insights": llm_insights,
                "execution_time_ms": int((time.time() - start_time) * 1000)
            }
            return result
            
        except Exception as e:
            logger.error(f"Error in CampaignOptimizationAgent: {e}")
            return {"status": "error", "message": str(e)}
