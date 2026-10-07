import logging
import time
import json
from typing import Dict, Any, Optional
from .llm_provider import get_llm

logger = logging.getLogger("marketpilot.quality")

class QualityGovernanceAgent:
    def __init__(self):
        self.llm = get_llm()
        
    async def analyze(self, campaign: Dict[str, Any], datasets: Dict[str, Any], previous_results: Dict[str, Any]) -> Dict[str, Any]:
        """Validate all other agent outputs for accuracy and consistency."""
        logger.info("Starting Quality Governance Check")
        start_time = time.time()
        
        try:
            # 1. Hard constraints check: Budget
            budget_result = previous_results.get("budget", {})
            total_budget = budget_result.get("total_budget", 0)
            recommended_allocs = budget_result.get("mathematical_recommendation", {})
            
            budget_passed = True
            budget_error = ""
            if recommended_allocs:
                allocated_total = sum(recommended_allocs.values())
                # Allow minor floating point drift
                if allocated_total > total_budget * 1.01:
                    budget_passed = False
                    budget_error = f"Total allocated budget ({allocated_total}) exceeds constraint ({total_budget})"
            
            # 2. LLM validation for logical consistency
            prompt = f"""
            You are a Quality Governance AI. Review the outputs of other agents for logic, consistency, and grounding.
            
            Budget Result Status: {'Passed' if budget_passed else 'Failed: ' + budget_error}
            
            Optimization Insights: {json.dumps(previous_results.get('optimization', {}).get('insights', {}))}
            Content Insights: {json.dumps(previous_results.get('content', {}).get('insights', {}))}
            
            Validate the following:
            1. Are the optimization recommendations grounded in reality?
            2. Do content recommendations contradict the tone needed for optimization?
            3. Are there unsupported claims?
            
            Provide a structured JSON output with:
            - 'passed': boolean (true if overall acceptable, false if rejection required)
            - 'failed_agents': list of agent names that failed validation (e.g., ["budget", "optimization"]) - empty if passed
            - 'feedback': dict mapping failed agent names to specific feedback on why they failed and what to fix
            - 'validation_notes': general notes on the review
            """
            
            llm_insights = await self.llm.generate_json(
                prompt=prompt,
                system_prompt="You are a strict, detail-oriented Quality Assurance and Governance reviewer."
            )
            
            # Override LLM if hard budget constraint failed
            if not budget_passed:
                llm_insights["passed"] = False
                if "budget" not in llm_insights.get("failed_agents", []):
                    agents = set(llm_insights.get("failed_agents", []))
                    agents.add("budget")
                    llm_insights["failed_agents"] = list(agents)
                
                feedback = llm_insights.get("feedback", {})
                feedback["budget"] = budget_error
                llm_insights["feedback"] = feedback
                
            result = {
                "status": "success",
                "passed": llm_insights.get("passed", False),
                "failed_agents": llm_insights.get("failed_agents", []),
                "feedback": llm_insights.get("feedback", {}),
                "validation_notes": llm_insights.get("validation_notes", ""),
                "execution_time_ms": int((time.time() - start_time) * 1000)
            }
            return result
            
        except Exception as e:
            logger.error(f"Error in QualityGovernanceAgent: {e}")
            return {"status": "error", "message": str(e), "passed": False, "failed_agents": ["quality"]}
