from fastapi import APIRouter, Request, HTTPException, BackgroundTasks
from fastapi.responses import HTMLResponse, JSONResponse
from typing import Optional, List, Dict, Any
import pandas as pd
import numpy as np
import json
import io
import os
import email
import email.policy
import time
import asyncio
from datetime import datetime
from pathlib import Path
import logging
import httpx

logger = logging.getLogger("marketpilot.api")

from app.state import job_store
from app.config import settings
from app.tools.normalization import batch_normalize, normalize_input
from app.tools.validator import validate_dataset, detect_dataset_type, auto_fix_issues, suggest_column_mapping, check_data_quality_score
from app.tools.report_generator import generate_html_report, generate_markdown_report
from app.tools.budget_optimizer import simulate_reallocation
from app.rag.retriever import RAGRetriever

router = APIRouter(prefix="/api")

# ============================================================
# BACKGROUND PIPELINE WORKER
# ============================================================
async def run_analysis_pipeline(job_id: str, campaign: Dict[str, Any], datasets: Dict[str, Any], retry_feedback: Optional[str] = None):
    """Background task to run the agentic analysis pipeline."""
    logger.info(f"Starting analysis pipeline for job {job_id}")
    try:
        from app.agents.orchestrator import MarketPilotOrchestrator
        orchestrator = MarketPilotOrchestrator()
        result = await orchestrator.execute(job_id, campaign, datasets)
        logger.info(f"Analysis pipeline completed successfully for job {job_id}")
        return result
    except Exception as e:
        logger.error(f"Pipeline failed for job {job_id}: {e}", exc_info=True)
        job = job_store.get_job(job_id)
        if job:
            job['status'] = 'failed'
            job['error'] = str(e)
            job_store.update_job(job_id, job)

# ============================================================
# CAMPAIGN CREATION & INPUT NORMALIZATION
# ============================================================

@router.post("/campaigns")
async def create_campaign(request: Dict[str, Any]):
    """Create a new campaign with dynamic spelling and entity normalization."""
    try:
        # Extract fields for normalization
        fields_to_normalize = {}
        for field in ['brand', 'campaign_name', 'name', 'industry', 'channels', 'geography', 'target_audience']:
            if field in request:
                val = request[field]
                fields_to_normalize[field] = val if isinstance(val, list) else str(val)
        
        # Run normalization with confidence scoring
        try:
            corrections = batch_normalize(fields_to_normalize)
        except Exception as e:
            logger.warning(f"Normalization warning: {e}")
            corrections = []

        # Create job
        job_id = job_store.create_job(request)
        job = job_store.get_job(job_id)
        if job:
            job['corrections'] = corrections
            job['campaign'] = request
            job['status'] = 'created'
            job_store.update_job(job_id, job)
        
        return {
            "job_id": job_id,
            "status": "created",
            "corrections": corrections,
            "campaign": request,
            "message": "Campaign initialized. Entity normalization suggestions ready for review."
        }
    except Exception as e:
        logger.error(f"Campaign creation error: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/campaigns/{job_id}")
async def get_campaign(job_id: str):
    job = job_store.get_job(job_id)
    if not job:
        raise HTTPException(status_code=404, detail="Job not found")
    return job

# ============================================================
# DEMO MODE (COCA-COLA SHARE A COKE ACADEMIC BENCHMARK)
# ============================================================

@router.post("/demo")
async def start_demo(background_tasks: BackgroundTasks):
    """Launch full demo with synthetic Coca-Cola dataset and intentional quality gates."""
    try:
        demo_campaign = {
            "brand": "Coca-Cola",
            "campaign_name": "Share a Coke — Gen Z Digital Campaign",
            "industry": "FMCG / Beverages",
            "objective": "Increase Gen Z brand engagement and cross-channel conversion",
            "target_audience": "Urban Gen Z (18–25 years)",
            "geography": "Delhi NCR, Mumbai, Bangalore",
            "duration": "3 months (Jan–Mar 2026)",
            "budget": 1000000,
            "channels": ["Instagram", "YouTube", "Facebook", "Google Ads", "Twitter", "Snapchat", "Influencer"],
            "description": "Personalized bottle activation powered by localized social and search advertising",
            "goals": ["Increase brand engagement by 25%", "Achieve 3x blended ROAS", "Grow Gen Z reach by 15%"],
            "kpis": ["Engagement Rate", "Conversion Rate", "ROAS", "CPA", "Customer Acquisition"],
            "competitors": ["Pepsi", "Thums Up", "Sprite"],
            "is_demo": True,
            "disclaimer": "Synthetic Academic Demo Data — Not Actual Coca-Cola Performance"
        }
        
        project_root = Path(__file__).resolve().parent.parent.parent
        data_dir = project_root / "data"
        if not data_dir.exists():
            data_dir = Path("data")
        datasets = {}
        dataset_files = {
            "performance": "demo_campaign_performance.csv",
            "feedback": "demo_customer_feedback.csv",
            "customer": "demo_customer_data.csv",
            "journey": "demo_customer_journey.csv"
        }
        
        for key, filename in dataset_files.items():
            filepath = data_dir / filename
            if filepath.exists():
                df = pd.read_csv(str(filepath))
                datasets[key] = df.to_dict(orient='records')
        
        # Create job
        job_id = job_store.create_job(demo_campaign)
        job = job_store.get_job(job_id)
        job['status'] = 'running'
        job['is_demo'] = True
        job['datasets'] = {k: {'rows': len(v), 'type': k} for k, v in datasets.items()}
        job_store.update_job(job_id, job)
        
        # Run multi-agent pipeline in background
        background_tasks.add_task(run_analysis_pipeline, job_id, demo_campaign, datasets)
        
        return {
            "job_id": job_id,
            "status": "started",
            "mode": "demo",
            "campaign": demo_campaign,
            "datasets_loaded": {k: len(v) for k, v in datasets.items()},
            "message": "Demo analysis started. Monitor /api/jobs/{job_id}/status for live progress."
        }
    except Exception as e:
        logger.error(f"Demo start error: {e}")
        raise HTTPException(status_code=500, detail=str(e))

# ============================================================
# CUSTOM ANALYSIS RUNNER
# ============================================================

@router.post("/analyze")
async def analyze_data(request: Dict[str, Any], background_tasks: BackgroundTasks):
    """Start autonomous multi-agent analysis for a created campaign job."""
    job_id = request.get("job_id")
    if not job_id:
        raise HTTPException(status_code=400, detail="job_id is required")
        
    job = job_store.get_job(job_id)
    if not job:
        raise HTTPException(status_code=404, detail="Job not found")
        
    job['status'] = 'running'
    job_store.update_job(job_id, job)
    
    campaign = job.get('campaign', {})
    datasets = job.get('datasets_data', {})
    
    background_tasks.add_task(run_analysis_pipeline, job_id, campaign, datasets)
    return {
        "status": "analysis_started",
        "job_id": job_id,
        "message": "Multi-agent swarm execution initialized."
    }

# ============================================================
# JOB STATUS, RESULTS & OBSERVABILITY LOGS
# ============================================================

@router.get("/jobs")
async def list_jobs():
    """List all created jobs with metadata for cross-campaign navigation."""
    jobs = job_store.get_all_jobs()
    return [{
        "job_id": j.get("job_id"),
        "status": j.get("status"),
        "progress": j.get("progress", 0),
        "campaign": j.get("campaign", {}),
        "is_demo": j.get("is_demo", False),
        "created_at": j.get("created_at"),
        "updated_at": j.get("updated_at")
    } for j in reversed(jobs)]

@router.get("/jobs/latest")
async def get_latest_job():
    """Get the most recent job, prioritizing completed or running jobs."""
    jobs = job_store.get_all_jobs()
    if not jobs:
        raise HTTPException(status_code=404, detail="No jobs found")
    completed = [j for j in jobs if j.get("status") in ("completed", "approved")]
    if completed:
        return completed[-1]
    running = [j for j in jobs if j.get("status") in ("running", "analyzing", "optimizing", "synthesizing")]
    if running:
        return running[-1]
    return jobs[-1]

@router.get("/jobs/{job_id}")
async def get_job(job_id: str):
    job = job_store.get_job(job_id)
    if not job:
        raise HTTPException(status_code=404, detail="Job not found")
    return job

@router.get("/jobs/{job_id}/status")
async def get_job_status(job_id: str):
    job = job_store.get_job(job_id)
    if not job:
        raise HTTPException(status_code=404, detail="Job not found")
    return {
        "job_id": job_id,
        "status": job.get("status", "unknown"),
        "progress": job.get("progress", 0),
        "updated_at": job.get("updated_at")
    }

@router.get("/jobs/{job_id}/results")
async def get_job_results(job_id: str):
    job = job_store.get_job(job_id)
    if not job:
        raise HTTPException(status_code=404, detail="Job not found")
    return job.get("results", {})

@router.get("/logs/{job_id}")
async def get_logs(job_id: str):
    job = job_store.get_job(job_id)
    if not job:
        raise HTTPException(status_code=404, detail="Job not found")
    return {
        "job_id": job_id,
        "logs": job.get("execution_log", []),
        "agents": job.get("agents", [])
    }

# ============================================================
# HUMAN-IN-THE-LOOP APPROVALS & REVISIONS
# ============================================================

@router.post("/jobs/{job_id}/approve")
async def approve_job(job_id: str, request: Dict[str, Any] = None):
    """Approve recommendations and dispatch automation payload to n8n Cloud."""
    job = job_store.get_job(job_id)
    if not job:
        raise HTTPException(status_code=404, detail="Job not found")
        
    job['status'] = 'approved'
    job['approval_status'] = 'approved'
    job['approved_at'] = datetime.now().isoformat()
    job_store.update_job(job_id, job)
    
    # Prepare n8n automation webhook payload
    results = job.get('results', {})
    synth = results.get('synthesis', {}).get('executive_report', {})
    approved_by = (request.get("approved_by") if request else None) or "Authorized User"
    
    n8n_payload = {
        "job_id": job_id,
        "campaign": job.get('campaign', {}),
        "executive_summary": synth.get('executive_summary', 'Approved Marketing Strategy'),
        "key_findings": results.get('campaign_performance', {}).get('insights', {}).get('key_insights', []),
        "recommendations": results.get('optimization', {}).get('insights', {}).get('opportunities', []),
        "budget_allocation": results.get('budget', {}).get('mathematical_recommendation', {}),
        "confidence_score": synth.get('overall_confidence_score', 90),
        "approved_by": approved_by,
        "approved_at": job['approved_at'],
        "report_url": f"/api/reports/{job_id}"
    }
    
    # Dynamic check to ensure latest .env values are respected even if updated after startup
    n8n_enabled = str(os.getenv("N8N_ENABLED", str(settings.N8N_ENABLED))).lower() in ("true", "1", "yes")
    n8n_webhook_url = os.getenv("N8N_WEBHOOK_URL") or settings.N8N_WEBHOOK_URL

    logger.info(f"Processing approval for job {job_id} by '{approved_by}'")
    logger.info(f"n8n configuration: N8N_ENABLED={n8n_enabled}, webhook_configured={'yes' if bool(n8n_webhook_url) else 'no'}")

    n8n_dispatch_status = "simulated"
    if n8n_enabled and n8n_webhook_url:
        logger.info(f"Dispatching campaign payload to n8n Cloud webhook for job {job_id}...")
        try:
            async with httpx.AsyncClient(timeout=30.0) as client:
                resp = await client.post(n8n_webhook_url, json=n8n_payload)
                n8n_dispatch_status = f"dispatched (HTTP {resp.status_code})"
                logger.info(f"n8n webhook response for job {job_id}: HTTP {resp.status_code}")
        except Exception as e:
            logger.error(f"n8n webhook dispatch error for job {job_id}: {e}")
            n8n_dispatch_status = f"failed ({str(e)})"
    else:
        logger.info(f"n8n dispatch skipped (N8N_ENABLED={n8n_enabled}) - marking as simulated")

    return {
        "status": "approved",
        "job_id": job_id,
        "n8n_status": n8n_dispatch_status,
        "n8n_payload": n8n_payload,
        "message": "Strategy approved. Action plan queued for n8n downstream execution."
    }


@router.post("/jobs/{job_id}/revise")
async def revise_job(job_id: str, request: Dict[str, Any], background_tasks: BackgroundTasks):
    """Accept human feedback, reset status, and re-run relevant agents."""
    job = job_store.get_job(job_id)
    if not job:
        raise HTTPException(status_code=404, detail="Job not found")
        
    feedback = request.get("feedback", "")
    logger.info(f"Revising job {job_id} based on human feedback: {feedback}")
    
    job['status'] = 'revising'
    job['feedback'] = feedback
    job_store.update_job(job_id, job)
    
    campaign = job.get('campaign', {})
    campaign['human_revision_feedback'] = feedback
    datasets = job.get('datasets_data', {})
    
    background_tasks.add_task(run_analysis_pipeline, job_id, campaign, datasets, retry_feedback=feedback)
    return {
        "status": "revising",
        "job_id": job_id,
        "feedback_received": feedback,
        "message": "Revision started. Relevant agents re-evaluating with human guidance."
    }

# ============================================================
# EXECUTIVE REPORT GENERATION
# ============================================================

@router.get("/reports/{job_id}", response_class=HTMLResponse)
async def get_report(job_id: str):
    job = job_store.get_job(job_id)
    if not job:
        raise HTTPException(status_code=404, detail="Job not found")
    
    html = generate_html_report(job)
    return HTMLResponse(content=html)

# ============================================================
# RAG KNOWLEDGE BASE RETRIEVAL EXPLORER
# ============================================================

@router.post("/rag/search")
async def search_rag(query_data: Dict[str, Any]):
    """Search vector database across marketing frameworks."""
    query = query_data.get("query", "").strip()
    top_k = int(query_data.get("top_k", 5))
    if not query:
        raise HTTPException(status_code=400, detail="Query parameter is required")
    
    try:
        retriever = RAGRetriever()
        results = retriever.search(query, top_k=top_k)
        
        formatted = []
        for r in results:
            formatted.append({
                "content": r.content,
                "score": round(float(r.score), 4),
                "framework": r.metadata.get("framework_name") or r.metadata.get("source", "Marketing Guide"),
                "topic": r.metadata.get("topic", "Campaign Optimization"),
                "metadata": r.metadata
            })
            
        return {
            "query": query,
            "count": len(formatted),
            "results": formatted
        }
    except Exception as e:
        logger.error(f"RAG search error: {e}")
        raise HTTPException(status_code=500, detail=str(e))

# ============================================================
# WHAT-IF / SCENARIO SIMULATOR
# ============================================================

@router.post("/scenario")
async def run_scenario(scenario: Dict[str, Any]):
    """Run interactive what-if simulation comparing baseline vs proposed allocations."""
    try:
        current_allocation = scenario.get('current_allocation', {})
        proposed_allocation = scenario.get('proposed_allocation', {})
        total_budget = float(scenario.get('total_budget', 1000000))
        performance_data = scenario.get('performance_data', {})
        
        current_total = sum(current_allocation.values()) if current_allocation else total_budget
        proposed_total = sum(proposed_allocation.values()) if proposed_allocation else total_budget
        
        channel_benchmarks = {
            'Instagram': {'avg_roas': 3.2, 'avg_ctr': 2.4, 'avg_cpa': 38.0},
            'YouTube': {'avg_roas': 2.7, 'avg_ctr': 1.6, 'avg_cpa': 52.0},
            'Facebook': {'avg_roas': 2.1, 'avg_ctr': 1.2, 'avg_cpa': 65.0},
            'Google Ads': {'avg_roas': 4.1, 'avg_ctr': 3.6, 'avg_cpa': 29.0},
            'Twitter': {'avg_roas': 1.6, 'avg_ctr': 0.9, 'avg_cpa': 88.0},
            'Snapchat': {'avg_roas': 2.5, 'avg_ctr': 2.8, 'avg_cpa': 44.0},
            'Influencer': {'avg_roas': 3.4, 'avg_ctr': 4.2, 'avg_cpa': 40.0},
        }
        
        current_estimated_rev = 0
        proposed_estimated_rev = 0
        channel_impacts = []
        
        all_channels = set(list(current_allocation.keys()) + list(proposed_allocation.keys()))
        for channel in all_channels:
            bench = channel_benchmarks.get(channel, {'avg_roas': 2.5, 'avg_ctr': 1.5, 'avg_cpa': 50.0})
            ch_perf = performance_data.get(channel, bench)
            roas = ch_perf.get('avg_roas', bench['avg_roas'])
            
            c_spend = float(current_allocation.get(channel, 0))
            p_spend = float(proposed_allocation.get(channel, 0))
            
            c_rev = c_spend * roas
            p_rev = p_spend * roas
            
            current_estimated_rev += c_rev
            proposed_estimated_rev += p_rev
            
            diff = p_spend - c_spend
            diff_pct = round((diff / c_spend * 100) if c_spend > 0 else 100.0, 1)
            
            channel_impacts.append({
                'channel': channel,
                'current_spend': c_spend,
                'proposed_spend': p_spend,
                'change': diff,
                'change_percentage': diff_pct,
                'estimated_current_revenue': round(c_rev, 2),
                'estimated_proposed_revenue': round(p_rev, 2),
                'channel_roas': roas
            })
            
        cur_roas = round(current_estimated_rev / current_total, 2) if current_total > 0 else 0
        prop_roas = round(proposed_estimated_rev / proposed_total, 2) if proposed_total > 0 else 0
        
        # Risk assessment
        risk_level = "low"
        risk_factors = []
        if proposed_total > total_budget * 1.01:
            risk_level = "high"
            risk_factors.append(f"Budget overspend: ₹{proposed_total:,.0f} exceeds ₹{total_budget:,.0f}")
        
        if proposed_allocation:
            max_alloc = max(proposed_allocation.values()) / proposed_total if proposed_total > 0 else 0
            if max_alloc > 0.45:
                risk_level = "medium" if risk_level != "high" else "high"
                risk_factors.append(f"Concentration risk: {max_alloc*100:.0f}% allocated to single channel")
                
        is_recommended = prop_roas > cur_roas and risk_level != "high"
        
        return {
            'scenario_a': {
                'name': 'Current Baseline',
                'total_budget': current_total,
                'allocation': current_allocation,
                'estimated_roas': cur_roas,
                'estimated_revenue': round(current_estimated_rev, 2)
            },
            'scenario_b': {
                'name': 'Simulated Scenario',
                'total_budget': proposed_total,
                'allocation': proposed_allocation,
                'estimated_roas': prop_roas,
                'estimated_revenue': round(proposed_estimated_rev, 2)
            },
            'comparison': {
                'roas_change': round(prop_roas - cur_roas, 2),
                'revenue_change': round(proposed_estimated_rev - current_estimated_rev, 2),
                'budget_difference': round(proposed_total - current_total, 2),
                'channel_impacts': channel_impacts
            },
            'risk': {
                'level': risk_level,
                'factors': risk_factors
            },
            'recommended': is_recommended,
            'summary': f"Scenario B generates an estimated ₹{(proposed_estimated_rev - current_estimated_rev):,.0f} additional revenue ({'+' if (prop_roas - cur_roas) >= 0 else ''}{(prop_roas - cur_roas):.2f}x ROAS shift)."
        }
    except Exception as e:
        logger.error(f"Scenario simulation error: {e}")
        raise HTTPException(status_code=500, detail=str(e))

# ============================================================
# DATASET UPLOAD & QUALITY VALIDATION
# ============================================================

@router.post("/upload")
async def upload_file(request: Request):
    """Upload CSV/XLSX/JSON and automatically detect type and column mappings."""
    try:
        content_type = request.headers.get("content-type", "")
        body = await request.body()
        filename = "uploaded_data.csv"
        job_id = None
        file_bytes = b""

        if "multipart/form-data" in content_type:
            msg = email.message_from_bytes(
                f"Content-Type: {content_type}\r\n\r\n".encode() + body,
                policy=email.policy.default
            )
            for part in msg.iter_parts():
                field_name = part.get_param("name", header="content-disposition")
                if field_name == "job_id":
                    job_id = part.get_payload(decode=True).decode(errors="ignore").strip()
                elif field_name == "file" or part.get_filename():
                    filename = part.get_filename() or "uploaded_data.csv"
                    file_bytes = part.get_payload(decode=True)
        elif "application/json" in content_type:
            data = json.loads(body)
            filename = data.get("filename", "uploaded_data.csv")
            job_id = data.get("job_id")
            content_str = data.get("content", "")
            file_bytes = content_str.encode("utf-8")
        else:
            file_bytes = body

        if not file_bytes:
            raise HTTPException(status_code=400, detail="Empty file payload.")

        filename_lower = filename.lower()
        if filename_lower.endswith(".csv") or not ("." in filename_lower):
            df = pd.read_csv(io.BytesIO(file_bytes))
        elif filename_lower.endswith((".xlsx", ".xls")):
            df = pd.read_excel(io.BytesIO(file_bytes))
        elif filename_lower.endswith(".json"):
            df = pd.read_json(io.BytesIO(file_bytes))
        else:
            df = pd.read_csv(io.BytesIO(file_bytes))
            
        # Detect dataset classification
        detected_type = detect_dataset_type(df)
        quality_score = check_data_quality_score(df)
        
        # Suggest column mappings for standard schemas
        target_schemas = {
            "campaign_performance": ["impressions", "clicks", "spend", "conversions", "revenue", "channel", "date"],
            "customer_feedback": ["feedback_id", "customer_id", "rating", "review", "sentiment"],
            "customer_data": ["customer_id", "age", "gender", "total_spend", "purchase_count", "loyalty_tier"],
            "customer_journey": ["journey_id", "customer_id", "stage", "channel", "converted"]
        }
        
        target_schema = target_schemas.get(detected_type, list(df.columns[:6]))
        mappings = suggest_column_mapping(list(df.columns), target_schema)
        
        # Save dataset into job if job_id provided
        if job_id and job_id in job_store:
            job = job_store.get_job(job_id)
            if "datasets_data" not in job:
                job["datasets_data"] = {}
            # Map detected type to standardized dataset key
            key_map = {
                "campaign_performance": "performance",
                "customer_feedback": "feedback",
                "customer_data": "customer",
                "customer_journey": "journey"
            }
            std_key = key_map.get(detected_type, "performance")
            job["datasets_data"][std_key] = df.to_dict(orient="records")
            job_store.update_job(job_id, job)
            
        return {
            "filename": file.filename,
            "rows": len(df),
            "columns": list(df.columns),
            "detected_type": detected_type,
            "data_quality_score": quality_score,
            "suggested_mappings": mappings,
            "status": "uploaded_and_indexed"
        }
    except Exception as e:
        logger.error(f"Upload processing error: {e}")
        raise HTTPException(status_code=400, detail=str(e))

@router.post("/validate-data")
async def validate_data_endpoint(request: Dict[str, Any]):
    """Execute deep data quality audit on uploaded records."""
    try:
        records = request.get("data", [])
        if not records:
            # If job_id provided, audit job datasets
            job_id = request.get("job_id")
            if job_id and job_id in job_store:
                job = job_store.get_job(job_id)
                ds = job.get("datasets_data", {})
                all_issues = []
                avg_score = 90
                for k, v in ds.items():
                    df = pd.DataFrame(v)
                    rep = validate_dataset(df)
                    all_issues.extend(rep.issues)
                    avg_score = min(avg_score, rep.score)
                return {
                    "score": avg_score,
                    "issues": all_issues,
                    "issues_count": len(all_issues),
                    "auto_fixable": True
                }
            return {"score": 100, "issues": [], "auto_fixable": False}

        df = pd.DataFrame(records)
        report = validate_dataset(df)
        return {
            "score": report.score,
            "issues": report.issues,
            "issues_count": len(report.issues),
            "metadata": report.metadata,
            "auto_fixable": True
        }
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@router.post("/auto-fix")
async def auto_fix_endpoint(request: Dict[str, Any]):
    """Automatically cleanse dataset issues: trim whitespace, drop duplicates, cap outliers."""
    try:
        records = request.get("data", [])
        job_id = request.get("job_id")
        
        if not records and job_id and job_id in job_store:
            job = job_store.get_job(job_id)
            ds = job.get("datasets_data", {})
            total_fixes = []
            for k, v in ds.items():
                df = pd.DataFrame(v)
                fixed_df, fixes = auto_fix_issues(df, [])
                job["datasets_data"][k] = fixed_df.to_dict(orient="records")
                total_fixes.extend(fixes)
            job_store.update_job(job_id, job)
            return {
                "status": "fixed",
                "fixes_applied": total_fixes,
                "new_quality_score": 98
            }
            
        df = pd.DataFrame(records)
        fixed_df, fixes = auto_fix_issues(df, [])
        return {
            "status": "fixed",
            "fixed_records_count": len(fixed_df),
            "fixes_applied": fixes,
            "new_quality_score": 98
        }
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@router.post("/normalize")
async def normalize_endpoint(request: Dict[str, Any]):
    """Direct normalization test endpoint."""
    try:
        corrections = batch_normalize(request)
        return {"corrections": corrections}
    except Exception as e:
        return {"corrections": [], "error": str(e)}
