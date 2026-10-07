from pydantic import BaseModel
from typing import List, Optional
from app.models import CampaignInput, AnalysisResults, JobStatus, RAGChunk, ScenarioInput, ReportOutput

class CampaignCreateRequest(BaseModel):
    campaign: CampaignInput

class CampaignCreateResponse(BaseModel):
    job_id: str
    message: str
    status: JobStatus

class DataUploadResponse(BaseModel):
    filename: str
    message: str
    quality_score: float

class DataValidationResponse(BaseModel):
    job_id: str
    is_valid: bool
    errors: List[str]

class AnalysisRequest(BaseModel):
    job_id: str

class AnalysisResponse(BaseModel):
    job_id: str
    status: JobStatus
    message: str

class JobStatusResponse(BaseModel):
    job_id: str
    status: JobStatus
    updated_at: str

class JobResultsResponse(BaseModel):
    job_id: str
    status: JobStatus
    results: Optional[AnalysisResults]

class ApprovalRequest(BaseModel):
    job_id: str
    approved: bool
    feedback: Optional[str] = None

class ApprovalResponse(BaseModel):
    job_id: str
    status: str
    message: str

class RevisionRequest(BaseModel):
    job_id: str
    instructions: str

class RevisionResponse(BaseModel):
    job_id: str
    status: str
    message: str

class RAGSearchRequest(BaseModel):
    query: str
    top_k: int = 5

class RAGSearchResponse(BaseModel):
    query: str
    results: List[RAGChunk]

class ScenarioRequest(BaseModel):
    job_id: str
    scenarios: List[ScenarioInput]

class ScenarioResponse(BaseModel):
    job_id: str
    scenarios_analyzed: int
    message: str

class ReportResponse(BaseModel):
    job_id: str
    report: ReportOutput

class HealthResponse(BaseModel):
    status: str
    version: str

class ErrorResponse(BaseModel):
    error: str
    details: Optional[str] = None
