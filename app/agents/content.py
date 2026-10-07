import logging
import time
import json
from typing import Dict, Any, Optional
from .llm_provider import get_llm

logger = logging.getLogger("marketpilot.content")

class ContentRecommendationAgent:
    def __init__(self):
        self.llm = get_llm()
        
    async def analyze(self, campaign: Dict[str, Any], datasets: Dict[str, Any], previous_results: Dict[str, Any], retry_feedback: str = None) -> Dict[str, Any]:
        """Generate content and creative recommendations."""
        logger.info("Starting Content Recommendation Analysis")
        start_time = time.time()
        
        try:
            # Gather context
            segments = previous_results.get("segmentation", {}).get("insights", {}).get("segments", [])
            voice = previous_results.get("customer_voice", {}).get("insights", {})
            performance = previous_results.get("campaign_performance", {}).get("insights", {})
            
            prompt = f"""
            Generate content, creative, and messaging recommendations based on customer segments, feedback, and performance.
            
            Target Segments: {json.dumps(segments)}
            Customer Feedback Insights: {json.dumps(voice)}
            Performance Insights: {json.dumps(performance)}
            
            Retry Feedback (if any): {retry_feedback}
            
            Provide a structured JSON output with:
            - 'core_themes': 3-4 overarching content themes that will resonate across segments
            - 'segment_strategies': Array mapping segments to specific messaging angles and recommended formats
            - 'channel_adaptations': How to adapt the core themes for top performing channels
            - 'cta_recommendations': Recommended Calls to Action
            """
            
            llm_insights = await self.llm.generate_json(
                prompt=prompt,
                system_prompt="You are an expert creative director and copywriter."
            )
            
            result = {
                "status": "success",
                "insights": llm_insights,
                "execution_time_ms": int((time.time() - start_time) * 1000)
            }
            return result
            
        except Exception as e:
            logger.error(f"Error in ContentRecommendationAgent: {e}")
            return {"status": "error", "message": str(e)}
