import logging
import time
import json
from typing import Dict, Any, Optional
from .llm_provider import get_llm

logger = logging.getLogger("marketpilot.synthesis")

class FinalSynthesisAgent:
    def __init__(self):
        self.llm = get_llm()
        
    async def analyze(self, campaign: Dict[str, Any], datasets: Dict[str, Any], previous_results: Dict[str, Any], retry_feedback: str = None) -> Dict[str, Any]:
        """Synthesize all validated results into final executive report."""
        logger.info("Starting Final Synthesis")
        start_time = time.time()
        
        try:
            # Extract key info from all validated agents
            summary_context = {
                "performance_summary": previous_results.get("campaign_performance", {}).get("insights", {}).get("executive_summary"),
                "optimizations": previous_results.get("optimization", {}).get("insights", {}).get("opportunities"),
                "budget_strategy": previous_results.get("budget", {}).get("insights", {}).get("allocation_strategy"),
                "content_themes": previous_results.get("content", {}).get("insights", {}).get("core_themes"),
                "quality_validation": previous_results.get("quality", {}).get("validation_notes")
            }
            
            prompt = f"""
            You are the Lead Marketing Strategist. Synthesize the findings from all specialized agents into a cohesive executive report and action plan.
            
            Agent Findings:
            {json.dumps(summary_context, indent=2)}
            
            Provide a structured JSON output with:
            - 'executive_summary': A powerful 2-3 paragraph summary of the state of the campaign and the primary path forward.
            - 'action_plan_30_day': A timeline of specific actions to take over the next 30 days.
            - 'overall_confidence_score': 1-100 score based on data quality and validation results.
            - 'key_assumptions': List of assumptions made in these recommendations.
            - 'data_sources_used': List of datasets that were analyzed.
            """
            
            llm_insights = await self.llm.generate_json(
                prompt=prompt,
                system_prompt="You are an elite Chief Marketing Officer producing a final executive brief."
            )
            
            result = {
                "status": "success",
                "executive_report": llm_insights,
                "execution_time_ms": int((time.time() - start_time) * 1000)
            }
            return result
            
        except Exception as e:
            logger.error(f"Error in FinalSynthesisAgent: {e}")
            return {"status": "error", "message": str(e)}
