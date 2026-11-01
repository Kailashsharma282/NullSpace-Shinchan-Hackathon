from pydantic import BaseModel, Field, HttpUrl, ConfigDict
from typing import List, Optional, Any, Dict
from datetime import datetime

# --- Requirement Schemas ---
class RequirementNodeBase(BaseModel):
    name: str = Field(..., min_length=1, max_length=255)
    description: str = Field(..., min_length=1)
    mandatory: bool = True
    importance: int = Field(5, ge=1, le=5)

class RequirementNodeCreate(RequirementNodeBase):
    key: Optional[str] = None

class RequirementNodeUpdate(BaseModel):
    name: Optional[str] = None
    description: Optional[str] = None
    mandatory: Optional[bool] = None
    importance: Optional[int] = Field(None, ge=1, le=5)

class RequirementNodeResponse(RequirementNodeBase):
    model_config = ConfigDict(from_attributes=True)
    id: str
    research_id: str
    key: str
    order_index: int


# --- Source Schemas ---
class SourceUrlAdd(BaseModel):
    url: str

class SourceManualCreate(BaseModel):
    title: str = Field(..., min_length=1)
    text: str = Field(..., min_length=10)
    url: Optional[str] = "manual://user-input"
    published_date: Optional[str] = None

class SourceDocumentResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: str
    research_id: str
    url: str
    domain: str
    title: str
    content_hash: str
    published_date: Optional[str] = None
    retrieved_at: datetime
    status: str
    error_message: Optional[str] = None
    is_fixture: bool
    text_length: Optional[int] = 0

class SourceDocumentDetailResponse(SourceDocumentResponse):
    raw_text: str


# --- Claim Schemas ---
class ExtractedClaimResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: str
    research_id: str
    source_id: str
    requirement_id: Optional[str] = None
    claim_text: str
    exact_quote: str
    char_start: int
    char_end: int
    is_grounded: bool
    confidence: float
    extraction_method: str
    source_title: Optional[str] = None
    source_url: Optional[str] = None
    source_domain: Optional[str] = None
    published_date: Optional[str] = None


# --- Mapping Schemas ---
class ClaimRequirementMappingResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: str
    research_id: str
    claim_id: str
    requirement_id: str
    confidence: float
    mapping_method: str
    explanation: str
    claim: Optional[ExtractedClaimResponse] = None


# --- Conflict Schemas ---
class ConflictRecordResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: str
    research_id: str
    requirement_id: str
    requirement_name: Optional[str] = None
    claim_a_id: str
    claim_b_id: str
    claim_a: Optional[ExtractedClaimResponse] = None
    claim_b: Optional[ExtractedClaimResponse] = None
    relationship_type: str  # contradiction, agreement, neutral, uncertain
    confidence: float
    explanation: str
    status: str  # confirmed, resolved, false_positive, requires_review
    user_notes: Optional[str] = None

class ConflictStatusUpdate(BaseModel):
    status: str = Field(..., pattern="^(confirmed|resolved|false_positive|requires_review)$")
    user_notes: Optional[str] = None


# --- Temporal Schemas ---
class TemporalAuditResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: str
    research_id: str
    source_id: str
    source_title: Optional[str] = None
    source_url: Optional[str] = None
    detected_years: List[str] = []
    detected_cycles: List[str] = []
    calendar_deadlines: List[str] = []
    temporal_status: str
    staleness_reason: Optional[str] = None
    published_date: Optional[str] = None


# --- Checklist Schemas ---
class ChecklistItemResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: str
    research_id: str
    requirement_id: str
    requirement_name: Optional[str] = None
    priority_score: float
    risk_category: str
    entropy: float
    title: str
    reason: str
    recommended_action: str
    search_dork: str
    is_resolved: bool

class ChecklistItemUpdate(BaseModel):
    is_resolved: bool


# --- Epistemic Matrix & Dashboard KPI Schemas ---
class EpistemicMatrixItem(BaseModel):
    requirement_id: str
    requirement_name: str
    mandatory: bool
    importance: int
    status: str  # "verified", "conflict", "stale", "dark_spot", "review_required"
    mapped_claims_count: int
    has_conflict: bool
    has_temporal_issue: bool
    is_dark_spot: bool
    claims: List[ExtractedClaimResponse] = []
    recommended_dork: Optional[str] = None

class DashboardKPIs(BaseModel):
    total_requirements: int
    evidence_coverage_pct: float
    dark_spots_count: int
    detected_conflicts_count: int
    stale_claims_count: int
    overall_risk_score: float

class AnalysisResultsResponse(BaseModel):
    research_id: str
    kpis: DashboardKPIs
    matrix: List[EpistemicMatrixItem]
    dark_spots: List[EpistemicMatrixItem]
    conflicts: List[ConflictRecordResponse]
    temporal_audits: List[TemporalAuditResponse]
    checklist: List[ChecklistItemResponse]


# --- Project Schemas ---
class ResearchProjectCreate(BaseModel):
    title: str = Field(..., min_length=2, max_length=255)
    objective: str = Field(..., min_length=5)
    domain: Optional[str] = "general"

class ResearchProjectResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: str
    title: str
    domain: str
    objective: str
    created_at: datetime
    updated_at: datetime
    requirements_count: Optional[int] = 0
    sources_count: Optional[int] = 0

class ResearchProjectDetailResponse(ResearchProjectResponse):
    requirements: List[RequirementNodeResponse] = []
    sources: List[SourceDocumentResponse] = []
