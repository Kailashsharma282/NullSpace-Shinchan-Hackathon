import datetime
from sqlalchemy import (
    Column, String, Integer, Float, Boolean, Text, DateTime, ForeignKey
)
from sqlalchemy.orm import relationship
from app.database.session import Base

class ResearchProject(Base):
    __tablename__ = "research_projects"

    id = Column(String(36), primary_key=True, index=True)
    title = Column(String(255), nullable=False)
    domain = Column(String(100), default="general")
    objective = Column(Text, nullable=False)
    created_at = Column(DateTime, default=datetime.datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.datetime.utcnow, onupdate=datetime.datetime.utcnow)

    requirements = relationship("RequirementNode", back_populates="project", cascade="all, delete-orphan")
    sources = relationship("SourceDocument", back_populates="project", cascade="all, delete-orphan")
    claims = relationship("ExtractedClaim", back_populates="project", cascade="all, delete-orphan")
    mappings = relationship("ClaimRequirementMapping", back_populates="project", cascade="all, delete-orphan")
    conflicts = relationship("ConflictRecord", back_populates="project", cascade="all, delete-orphan")
    temporal_audits = relationship("TemporalAudit", back_populates="project", cascade="all, delete-orphan")
    checklist_items = relationship("ChecklistItem", back_populates="project", cascade="all, delete-orphan")


class RequirementNode(Base):
    __tablename__ = "requirement_nodes"

    id = Column(String(64), primary_key=True, index=True)
    research_id = Column(String(36), ForeignKey("research_projects.id", ondelete="CASCADE"), nullable=False, index=True)
    key = Column(String(64), nullable=False)
    name = Column(String(255), nullable=False)
    description = Column(Text, nullable=False)
    mandatory = Column(Boolean, default=True)
    importance = Column(Integer, default=5)  # 1 to 5
    order_index = Column(Integer, default=0)

    project = relationship("ResearchProject", back_populates="requirements")


class SourceDocument(Base):
    __tablename__ = "source_documents"

    id = Column(String(64), primary_key=True, index=True)
    research_id = Column(String(36), ForeignKey("research_projects.id", ondelete="CASCADE"), nullable=False, index=True)
    url = Column(Text, nullable=False)
    domain = Column(String(255), nullable=False)
    title = Column(String(255), nullable=False)
    content_hash = Column(String(64), nullable=False)
    raw_text = Column(Text, nullable=False)
    published_date = Column(String(64), nullable=True)
    retrieved_at = Column(DateTime, default=datetime.datetime.utcnow)
    status = Column(String(32), default="ingested")  # ingested, failed, pending
    error_message = Column(Text, nullable=True)
    is_fixture = Column(Boolean, default=False)

    project = relationship("ResearchProject", back_populates="sources")
    claims = relationship("ExtractedClaim", back_populates="source", cascade="all, delete-orphan")
    temporal_audit = relationship("TemporalAudit", back_populates="source", uselist=False, cascade="all, delete-orphan")


class ExtractedClaim(Base):
    __tablename__ = "extracted_claims"

    id = Column(String(64), primary_key=True, index=True)
    research_id = Column(String(36), ForeignKey("research_projects.id", ondelete="CASCADE"), nullable=False, index=True)
    source_id = Column(String(64), ForeignKey("source_documents.id", ondelete="CASCADE"), nullable=False, index=True)
    requirement_id = Column(String(64), nullable=True)
    claim_text = Column(Text, nullable=False)
    exact_quote = Column(Text, nullable=False)
    char_start = Column(Integer, nullable=False)
    char_end = Column(Integer, nullable=False)
    is_grounded = Column(Boolean, default=True)
    confidence = Column(Float, default=1.0)
    extraction_method = Column(String(32), default="deterministic")

    project = relationship("ResearchProject", back_populates="claims")
    source = relationship("SourceDocument", back_populates="claims")


class ClaimRequirementMapping(Base):
    __tablename__ = "claim_requirement_mappings"

    id = Column(String(64), primary_key=True, index=True)
    research_id = Column(String(36), ForeignKey("research_projects.id", ondelete="CASCADE"), nullable=False, index=True)
    claim_id = Column(String(64), ForeignKey("extracted_claims.id", ondelete="CASCADE"), nullable=False)
    requirement_id = Column(String(64), ForeignKey("requirement_nodes.id", ondelete="CASCADE"), nullable=False)
    confidence = Column(Float, default=1.0)
    mapping_method = Column(String(32), default="semantic")
    explanation = Column(Text, nullable=False)

    project = relationship("ResearchProject", back_populates="mappings")


class ConflictRecord(Base):
    __tablename__ = "conflict_records"

    id = Column(String(64), primary_key=True, index=True)
    research_id = Column(String(36), ForeignKey("research_projects.id", ondelete="CASCADE"), nullable=False, index=True)
    requirement_id = Column(String(64), ForeignKey("requirement_nodes.id", ondelete="CASCADE"), nullable=False)
    claim_a_id = Column(String(64), ForeignKey("extracted_claims.id", ondelete="CASCADE"), nullable=False)
    claim_b_id = Column(String(64), ForeignKey("extracted_claims.id", ondelete="CASCADE"), nullable=False)
    relationship_type = Column(String(32), default="contradiction")  # contradiction, agreement, neutral, uncertain
    confidence = Column(Float, default=1.0)
    explanation = Column(Text, nullable=False)
    status = Column(String(32), default="requires_review")  # confirmed, resolved, false_positive, requires_review
    user_notes = Column(Text, nullable=True)

    project = relationship("ResearchProject", back_populates="conflicts")


class TemporalAudit(Base):
    __tablename__ = "temporal_audits"

    id = Column(String(64), primary_key=True, index=True)
    research_id = Column(String(36), ForeignKey("research_projects.id", ondelete="CASCADE"), nullable=False, index=True)
    source_id = Column(String(64), ForeignKey("source_documents.id", ondelete="CASCADE"), nullable=False)
    detected_years = Column(Text, default="[]")  # JSON encoded list of strings
    detected_cycles = Column(Text, default="[]")  # JSON encoded list of strings
    calendar_deadlines = Column(Text, default="[]")
    temporal_status = Column(String(32), default="current")  # current, potentially_outdated, outdated, date_unknown, conflicting
    staleness_reason = Column(Text, nullable=True)

    project = relationship("ResearchProject", back_populates="temporal_audits")
    source = relationship("SourceDocument", back_populates="temporal_audit")


class ChecklistItem(Base):
    __tablename__ = "checklist_items"

    id = Column(String(64), primary_key=True, index=True)
    research_id = Column(String(36), ForeignKey("research_projects.id", ondelete="CASCADE"), nullable=False, index=True)
    requirement_id = Column(String(64), nullable=False)
    priority_score = Column(Float, default=50.0)  # 0 to 100
    risk_category = Column(String(32), default="Medium")  # Critical, High, Medium, Low
    entropy = Column(Float, default=0.0)
    title = Column(String(255), nullable=False)
    reason = Column(Text, nullable=False)
    recommended_action = Column(Text, nullable=False)
    search_dork = Column(Text, nullable=False)
    is_resolved = Column(Boolean, default=False)

    project = relationship("ResearchProject", back_populates="checklist_items")

