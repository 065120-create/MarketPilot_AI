from pydantic import BaseModel, Field
from typing import List, Dict, Optional, Any
from enum import Enum
from datetime import datetime

class JobStatus(str, Enum):
    PENDING = "PENDING"
    VALIDATING = "VALIDATING"
    ANALYZING = "ANALYZING"
    OPTIMIZING = "OPTIMIZING"
    REVIEWING = "REVIEWING"
    APPROVED = "APPROVED"
    REJECTED = "REJECTED"
    COMPLETED = "COMPLETED"
    FAILED = "FAILED"

class CampaignInput(BaseModel):
    brand: str
    name: str
    industry: str
    objective: str
    audience: str
    geography: str
    duration: str
    budget: float
    channels: List[str]
    description: str
    goals: List[str]
    kpis: List[str]
    constraints: List[str]
    competitors: List[str]
    context: Optional[str] = None

class InputCorrection(BaseModel):
    original: str
    corrected: str
    confidence: float
    field: str
    accepted: bool = False

class DatasetUpload(BaseModel):
    filename: str
    dataset_type: str
    columns: List[str]
    row_count: int
    quality_score: float

class DataQualityIssue(BaseModel):
    field: str
    issue_type: str
    severity: str
    count: int
    description: str
    auto_fixable: bool
    fix_description: Optional[str] = None

class DataQualityReport(BaseModel):
    score: float
    issues: List[DataQualityIssue] = Field(default_factory=list)
    auto_fixable: bool = False
    warnings: List[str] = Field(default_factory=list)

class ColumnMapping(BaseModel):
    original_column: str
    suggested_column: str
    confidence: float
    accepted: bool = False

class AgentExecution(BaseModel):
    agent_name: str
    status: str
    input_summary: str
    output_summary: str
    tools_used: List[str] = Field(default_factory=list)
    rag_used: bool = False
    reasoning: str
    execution_time: float
    retries: int = 0
    confidence: float = 0.0
    errors: List[str] = Field(default_factory=list)

class CampaignPerformanceResult(BaseModel):
    roas: float
    conversion_rate: float
    cpa: float
    summary: str

class CustomerVoiceResult(BaseModel):
    sentiment_score: float
    key_themes: List[str]
    summary: str

class SegmentationResult(BaseModel):
    segments: List[Dict[str, Any]]
    summary: str

class JourneyResult(BaseModel):
    touchpoints: List[str]
    drop_off_points: List[str]
    summary: str

class OptimizationResult(BaseModel):
    recommendations: List[str]
    expected_uplift: float
    summary: str

class BudgetResult(BaseModel):
    allocation: Dict[str, float]
    total_budget: float
    summary: str

class ContentResult(BaseModel):
    themes: List[str]
    formats: List[str]
    summary: str

class ScenarioResult(BaseModel):
    scenarios: List[Dict[str, Any]]
    best_scenario: str

class QualityResult(BaseModel):
    score: float
    checks_passed: int
    total_checks: int
    summary: str

class SynthesisResult(BaseModel):
    executive_summary: str
    action_plan: List[str]

class AnalysisResults(BaseModel):
    campaign_performance: Optional[CampaignPerformanceResult] = None
    customer_voice: Optional[CustomerVoiceResult] = None
    segmentation: Optional[SegmentationResult] = None
    journey: Optional[JourneyResult] = None
    optimization: Optional[OptimizationResult] = None
    budget: Optional[BudgetResult] = None
    content: Optional[ContentResult] = None
    scenario: Optional[ScenarioResult] = None
    quality_validation: Optional[QualityResult] = None
    synthesis: Optional[SynthesisResult] = None

class RAGChunk(BaseModel):
    content: str
    source: str
    score: float

class RAGQuery(BaseModel):
    query: str
    top_k: int = 5

class RAGResult(BaseModel):
    query: str
    chunks: List[RAGChunk] = Field(default_factory=list)

class ScenarioInput(BaseModel):
    name: str
    budget_variance: float
    channel_focus: str

class ScenarioComparison(BaseModel):
    base_scenario: str
    comparisons: List[Dict[str, Any]]

class N8NPayload(BaseModel):
    workflow_id: str
    data: Dict[str, Any]

class ReportOutput(BaseModel):
    title: str
    content: str
    generated_at: datetime = Field(default_factory=datetime.utcnow)

class Job(BaseModel):
    job_id: str
    campaign: CampaignInput
    status: JobStatus = JobStatus.PENDING
    agents: List[AgentExecution] = Field(default_factory=list)
    results: Optional[AnalysisResults] = None
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)
    approval_status: str = "PENDING"
    quality_checks: List[Dict[str, Any]] = Field(default_factory=list)
    rag_retrievals: List[RAGResult] = Field(default_factory=list)
