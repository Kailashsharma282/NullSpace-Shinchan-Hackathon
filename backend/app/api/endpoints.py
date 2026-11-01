import uuid
import json
from typing import List, Dict, Any, Optional
from fastapi import APIRouter, Depends, HTTPException, status, Response
from fastapi.responses import JSONResponse
from sqlalchemy.orm import Session

from app.database.session import get_db
from app.models.project import (
    ResearchProject, RequirementNode, SourceDocument, ExtractedClaim, 
    ClaimRequirementMapping, ConflictRecord, TemporalAudit, ChecklistItem
)
from app.schemas.project import (
    ResearchProjectCreate, ResearchProjectResponse, ResearchProjectDetailResponse,
    RequirementNodeCreate, RequirementNodeUpdate, RequirementNodeResponse,
    SourceUrlAdd, SourceManualCreate, SourceDocumentResponse, SourceDocumentDetailResponse,
    ExtractedClaimResponse, ConflictRecordResponse, ConflictStatusUpdate,
    TemporalAuditResponse, ChecklistItemResponse, ChecklistItemUpdate,
    AnalysisResultsResponse, DashboardKPIs, EpistemicMatrixItem
)
from app.services.ontology.engine import generate_counterfactual_ontology
from app.services.ingestion.fetcher import fetch_and_clean_url, process_manual_text
from app.services.extraction.claim_extractor import ClaimExtractor
from app.services.alignment.matcher import AlignmentEngine
from app.services.contradiction.detector import ContradictionDetector
from app.services.temporal.auditor import TemporalAuditor
from app.services.prioritization.entropy import EpistemicScorer
from app.services.dorks.generator import DorkGenerator
from app.services.demo.scholarship_fixture import populate_scholarship_demo_fixture
from app.services.export.exporter import generate_research_json_export, generate_research_pdf_export

router = APIRouter()

# --- Health Check ---
@router.get("/health", tags=["System"])
def health_check():
    return {
        "status": "healthy",
        "service": "NullSpace Epistemic Audit Engine",
        "version": "1.0.0"
    }

# --- Demo Loader ---
@router.post("/demo/load", tags=["Demo"])
def load_scholarship_demo(db: Session = Depends(get_db)):
    """
    Loads synthetic demonstration fixtures deterministically.
    No external API keys or live web requests required.
    """
    project = populate_scholarship_demo_fixture(db)
    return {
        "message": "Scholarship demonstration fixture loaded successfully.",
        "research_id": project.id,
        "title": project.title,
        "is_synthetic_fixture": True,
        "disclaimer": "SYNTHETIC DEMO DATA — NOT FOR REAL-WORLD DECISIONS"
    }

# --- Research Projects ---
@router.post("/research", response_model=ResearchProjectResponse, tags=["Research"])
def create_research_project(payload: ResearchProjectCreate, db: Session = Depends(get_db)):
    """
    Stage 1 & 2: Initializes Research Project and generates the mandatory Decision Requirement Graph
    BEFORE any sources are fetched or ingested!
    """
    project_id = f"proj_{uuid.uuid4().hex[:10]}"
    project = ResearchProject(
        id=project_id,
        title=payload.title,
        domain=payload.domain or "general",
        objective=payload.objective
    )
    db.add(project)
    db.flush()

    # Counterfactual ontology generation BEFORE scraping
    generated_nodes = generate_counterfactual_ontology(payload.objective, payload.domain)
    for idx, node_data in enumerate(generated_nodes):
        node = RequirementNode(
            id=f"{project_id}_{node_data.key or f'req_{idx}'}",
            research_id=project_id,
            key=node_data.key or f"req_{idx}",
            name=node_data.name,
            description=node_data.description,
            mandatory=node_data.mandatory,
            importance=node_data.importance,
            order_index=idx
        )
        db.add(node)

    db.commit()
    db.refresh(project)
    
    return ResearchProjectResponse(
        id=project.id,
        title=project.title,
        domain=project.domain,
        objective=project.objective,
        created_at=project.created_at,
        updated_at=project.updated_at,
        requirements_count=len(generated_nodes),
        sources_count=0
    )

@router.get("/research", response_model=List[ResearchProjectResponse], tags=["Research"])
def list_research_projects(db: Session = Depends(get_db)):
    projects = db.query(ResearchProject).order_by(ResearchProject.created_at.desc()).all()
    results = []
    for p in projects:
        req_count = db.query(RequirementNode).filter(RequirementNode.research_id == p.id).count()
        src_count = db.query(SourceDocument).filter(SourceDocument.research_id == p.id).count()
        results.append(ResearchProjectResponse(
            id=p.id,
            title=p.title,
            domain=p.domain,
            objective=p.objective,
            created_at=p.created_at,
            updated_at=p.updated_at,
            requirements_count=req_count,
            sources_count=src_count
        ))
    return results

@router.get("/research/{research_id}", response_model=ResearchProjectDetailResponse, tags=["Research"])
def get_research_project(research_id: str, db: Session = Depends(get_db)):
    project = db.query(ResearchProject).filter(ResearchProject.id == research_id).first()
    if not project:
        raise HTTPException(status_code=404, detail="Research project not found.")

    reqs = db.query(RequirementNode).filter(RequirementNode.research_id == research_id).order_by(RequirementNode.order_index).all()
    sources = db.query(SourceDocument).filter(SourceDocument.research_id == research_id).all()
    
    src_responses = []
    for s in sources:
        src_responses.append(SourceDocumentResponse(
            id=s.id,
            research_id=s.research_id,
            url=s.url,
            domain=s.domain,
            title=s.title,
            content_hash=s.content_hash,
            published_date=s.published_date,
            retrieved_at=s.retrieved_at,
            status=s.status,
            error_message=s.error_message,
            is_fixture=s.is_fixture,
            text_length=len(s.raw_text) if s.raw_text else 0
        ))

    return ResearchProjectDetailResponse(
        id=project.id,
        title=project.title,
        domain=project.domain,
        objective=project.objective,
        created_at=project.created_at,
        updated_at=project.updated_at,
        requirements_count=len(reqs),
        sources_count=len(sources),
        requirements=[RequirementNodeResponse.model_validate(r) for r in reqs],
        sources=src_responses
    )

@router.delete("/research/{research_id}", tags=["Research"])
def delete_research_project(research_id: str, db: Session = Depends(get_db)):
    project = db.query(ResearchProject).filter(ResearchProject.id == research_id).first()
    if not project:
        raise HTTPException(status_code=404, detail="Research project not found.")
    db.delete(project)
    db.commit()
    return {"message": "Research project deleted successfully."}

# --- Requirement Nodes Management ---
@router.post("/research/{research_id}/requirements", response_model=RequirementNodeResponse, tags=["Ontology"])
def add_requirement_node(research_id: str, payload: RequirementNodeCreate, db: Session = Depends(get_db)):
    project = db.query(ResearchProject).filter(ResearchProject.id == research_id).first()
    if not project:
        raise HTTPException(status_code=404, detail="Research project not found.")

    key = payload.key or payload.name.lower().replace(" ", "_")[:32]
    node = RequirementNode(
        id=f"{research_id}_{uuid.uuid4().hex[:8]}",
        research_id=research_id,
        key=key,
        name=payload.name,
        description=payload.description,
        mandatory=payload.mandatory,
        importance=payload.importance,
        order_index=99
    )
    db.add(node)
    db.commit()
    db.refresh(node)
    return RequirementNodeResponse.model_validate(node)

@router.put("/research/{research_id}/requirements/{node_id}", response_model=RequirementNodeResponse, tags=["Ontology"])
def update_requirement_node(research_id: str, node_id: str, payload: RequirementNodeUpdate, db: Session = Depends(get_db)):
    node = db.query(RequirementNode).filter(RequirementNode.id == node_id, RequirementNode.research_id == research_id).first()
    if not node:
        raise HTTPException(status_code=404, detail="Requirement node not found.")

    if payload.name is not None:
        node.name = payload.name
    if payload.description is not None:
        node.description = payload.description
    if payload.mandatory is not None:
        node.mandatory = payload.mandatory
    if payload.importance is not None:
        node.importance = payload.importance

    db.commit()
    db.refresh(node)
    return RequirementNodeResponse.model_validate(node)

@router.delete("/research/{research_id}/requirements/{node_id}", tags=["Ontology"])
def delete_requirement_node(research_id: str, node_id: str, db: Session = Depends(get_db)):
    node = db.query(RequirementNode).filter(RequirementNode.id == node_id, RequirementNode.research_id == research_id).first()
    if not node:
        raise HTTPException(status_code=404, detail="Requirement node not found.")
    db.delete(node)
    db.commit()
    return {"message": "Requirement node deleted."}

# --- Source Management & Ingestion ---
@router.post("/research/{research_id}/sources", response_model=SourceDocumentResponse, tags=["Sources"])
async def add_source_document(research_id: str, payload: SourceUrlAdd, db: Session = Depends(get_db)):
    project = db.query(ResearchProject).filter(ResearchProject.id == research_id).first()
    if not project:
        raise HTTPException(status_code=404, detail="Research project not found.")

    # Check for duplicate URL in project
    existing = db.query(SourceDocument).filter(SourceDocument.research_id == research_id, SourceDocument.url == payload.url.strip()).first()
    if existing:
        return SourceDocumentResponse(
            id=existing.id,
            research_id=existing.research_id,
            url=existing.url,
            domain=existing.domain,
            title=existing.title,
            content_hash=existing.content_hash,
            published_date=existing.published_date,
            retrieved_at=existing.retrieved_at,
            status=existing.status,
            error_message=existing.error_message,
            is_fixture=existing.is_fixture,
            text_length=len(existing.raw_text) if existing.raw_text else 0
        )

    # Safe fetch and clean
    res = await fetch_and_clean_url(payload.url.strip())
    doc = SourceDocument(
        id=f"src_{uuid.uuid4().hex[:10]}",
        research_id=research_id,
        url=res["url"],
        domain=res["domain"],
        title=res["title"],
        content_hash=res["content_hash"],
        raw_text=res["raw_text"],
        published_date=res["published_date"],
        status=res["status"],
        error_message=res["error_message"],
        is_fixture=False
    )
    db.add(doc)
    db.commit()
    db.refresh(doc)
    
    return SourceDocumentResponse(
        id=doc.id,
        research_id=doc.research_id,
        url=doc.url,
        domain=doc.domain,
        title=doc.title,
        content_hash=doc.content_hash,
        published_date=doc.published_date,
        retrieved_at=doc.retrieved_at,
        status=doc.status,
        error_message=doc.error_message,
        is_fixture=doc.is_fixture,
        text_length=len(doc.raw_text) if doc.raw_text else 0
    )

@router.post("/research/{research_id}/sources/manual", response_model=SourceDocumentResponse, tags=["Sources"])
def add_manual_source(research_id: str, payload: SourceManualCreate, db: Session = Depends(get_db)):
    project = db.query(ResearchProject).filter(ResearchProject.id == research_id).first()
    if not project:
        raise HTTPException(status_code=404, detail="Research project not found.")

    res = process_manual_text(
        title=payload.title,
        text=payload.text,
        url=payload.url or "manual://user-input",
        published_date=payload.published_date
    )
    doc = SourceDocument(
        id=f"src_{uuid.uuid4().hex[:10]}",
        research_id=research_id,
        url=res["url"],
        domain=res["domain"],
        title=res["title"],
        content_hash=res["content_hash"],
        raw_text=res["raw_text"],
        published_date=res["published_date"],
        status=res["status"],
        error_message=None,
        is_fixture=False
    )
    db.add(doc)
    db.commit()
    db.refresh(doc)

    return SourceDocumentResponse(
        id=doc.id,
        research_id=doc.research_id,
        url=doc.url,
        domain=doc.domain,
        title=doc.title,
        content_hash=doc.content_hash,
        published_date=doc.published_date,
        retrieved_at=doc.retrieved_at,
        status=doc.status,
        error_message=doc.error_message,
        is_fixture=doc.is_fixture,
        text_length=len(doc.raw_text) if doc.raw_text else 0
    )

@router.get("/research/{research_id}/sources", response_model=List[SourceDocumentResponse], tags=["Sources"])
def list_sources(research_id: str, db: Session = Depends(get_db)):
    sources = db.query(SourceDocument).filter(SourceDocument.research_id == research_id).all()
    results = []
    for s in sources:
        results.append(SourceDocumentResponse(
            id=s.id,
            research_id=s.research_id,
            url=s.url,
            domain=s.domain,
            title=s.title,
            content_hash=s.content_hash,
            published_date=s.published_date,
            retrieved_at=s.retrieved_at,
            status=s.status,
            error_message=s.error_message,
            is_fixture=s.is_fixture,
            text_length=len(s.raw_text) if s.raw_text else 0
        ))
    return results

@router.delete("/research/{research_id}/sources/{source_id}", tags=["Sources"])
def delete_source(research_id: str, source_id: str, db: Session = Depends(get_db)):
    src = db.query(SourceDocument).filter(SourceDocument.id == source_id, SourceDocument.research_id == research_id).first()
    if not src:
        raise HTTPException(status_code=404, detail="Source document not found.")
    db.delete(src)
    db.commit()
    return {"message": "Source document deleted."}

# --- Core Epistemic Pipeline Analysis ---
@router.post("/research/{research_id}/analyze", response_model=AnalysisResultsResponse, tags=["Analysis"])
def run_analysis_pipeline(research_id: str, db: Session = Depends(get_db)):
    """
    Executes the full Epistemic Analysis Engine:
    1. Extract Grounded Atomic Claims (offsets validated against source_text)
    2. Bipartite Alignment (Maps claims to requirements)
    3. Digital Dark Spot Identification (InDegree(v) = 0 for mandatory requirements)
    4. Cross-Source Contradiction Detection (Pairwise claim comparison for same requirement)
    5. Temporal Staleness Audit (Cycle & Year analysis)
    6. Entropy & Priority Risk Scoring (Normalized Shannon Entropy + 0-100 Score)
    7. Targeted Search Dork Generation
    """
    project = db.query(ResearchProject).filter(ResearchProject.id == research_id).first()
    if not project:
        raise HTTPException(status_code=404, detail="Research project not found.")

    requirements = db.query(RequirementNode).filter(RequirementNode.research_id == research_id).all()
    sources = db.query(SourceDocument).filter(SourceDocument.research_id == research_id, SourceDocument.status == "ingested").all()

    # Clear previous derived analysis to maintain idempotency
    db.query(ExtractedClaim).filter(ExtractedClaim.research_id == research_id).delete()
    db.query(ClaimRequirementMapping).filter(ClaimRequirementMapping.research_id == research_id).delete()
    db.query(ConflictRecord).filter(ConflictRecord.research_id == research_id).delete()
    db.query(TemporalAudit).filter(TemporalAudit.research_id == research_id).delete()
    db.query(ChecklistItem).filter(ChecklistItem.research_id == research_id).delete()
    db.flush()

    # 1. Temporal Audits
    temporal_audits = []
    for s in sources:
        t_dict = TemporalAuditor.audit_source_temporality(
            source_id=s.id,
            raw_text=s.raw_text,
            published_date=s.published_date,
            research_id=research_id
        )
        audit_obj = TemporalAudit(**t_dict)
        db.add(audit_obj)
        temporal_audits.append(audit_obj)
    db.flush()

    # 2. Extract Atomic Claims
    all_claims = []
    for s in sources:
        extracted = ClaimExtractor.extract_deterministic_claims(
            source_id=s.id,
            raw_text=s.raw_text,
            research_id=research_id
        )
        for c_dict in extracted:
            claim_obj = ExtractedClaim(**c_dict)
            db.add(claim_obj)
            all_claims.append(claim_obj)
    db.flush()

    # 3. Bipartite Alignment
    mappings = AlignmentEngine.align_claims_to_requirements(all_claims, requirements, research_id)
    for m_dict in mappings:
        db.add(ClaimRequirementMapping(**m_dict))
    db.flush()

    # Group claims by requirement
    claims_by_req = {r.id: [] for r in requirements}
    for c in all_claims:
        if c.requirement_id and c.requirement_id in claims_by_req:
            claims_by_req[c.requirement_id].append(c)

    # 4. Pairwise Contradiction Detection
    req_map = {r.id: r for r in requirements}
    conflict_dicts = ContradictionDetector.detect_conflicts_for_research(claims_by_req, req_map, research_id)
    conflict_objs = []
    for cf in conflict_dicts:
        c_obj = ConflictRecord(**cf)
        db.add(c_obj)
        conflict_objs.append(c_obj)
    db.flush()

    # 5. Shannon Entropy & Priority Scoring
    matrix_items = []
    dark_spot_items = []
    checklist_items = []

    for req in requirements:
        req_claims = claims_by_req.get(req.id, [])
        req_conflicts = [cf for cf in conflict_objs if cf.requirement_id == req.id]

        score_res = EpistemicScorer.score_requirement(
            req=req,
            mapped_claims=req_claims,
            conflicts=req_conflicts,
            temporal_audits=temporal_audits
        )

        # Generate targeted search dork
        if score_res["is_dark_spot"]:
            dork_info = DorkGenerator.generate_dork_for_dark_spot(
                req_name=req.name,
                req_key=req.key,
                project_title=project.title,
                domain=project.domain
            )
        else:
            dork_info = DorkGenerator.generate_dork_for_conflict(
                req_name=req.name,
                claim_a_text=req_claims[0].claim_text if req_claims else "",
                claim_b_text=req_claims[1].claim_text if len(req_claims) > 1 else "",
                project_title=project.title
            )

        # Create checklist item if non-zero risk or dark spot
        if score_res["priority_score"] >= 35.0 or score_res["is_dark_spot"] or score_res["has_conflict"]:
            chk = ChecklistItem(
                id=f"chk_{uuid.uuid4().hex[:10]}",
                research_id=research_id,
                requirement_id=req.id,
                priority_score=score_res["priority_score"],
                risk_category=score_res["risk_category"],
                entropy=score_res["entropy"],
                title=f"Verify {req.name}" if not score_res["is_dark_spot"] else f"Resolve Dark Spot: {req.name}",
                reason=score_res["reason"],
                recommended_action=f"Consult official primary source regarding '{req.name}'. {dork_info['rationale']}",
                search_dork=dork_info["query"],
                is_resolved=False
            )
            db.add(chk)
            checklist_items.append(chk)

        # Matrix item
        source_map = {s.id: s for s in sources}
        claim_responses = [
            ExtractedClaimResponse(
                id=c.id,
                research_id=c.research_id,
                source_id=c.source_id,
                requirement_id=c.requirement_id,
                claim_text=c.claim_text,
                exact_quote=c.exact_quote,
                char_start=c.char_start,
                char_end=c.char_end,
                is_grounded=c.is_grounded,
                confidence=c.confidence,
                extraction_method=c.extraction_method,
                source_title=source_map[c.source_id].title if c.source_id in source_map else None,
                source_url=source_map[c.source_id].url if c.source_id in source_map else None,
                source_domain=source_map[c.source_id].domain if c.source_id in source_map else None,
                published_date=source_map[c.source_id].published_date if c.source_id in source_map else None,
            ) for c in req_claims
        ]

        m_item = EpistemicMatrixItem(
            requirement_id=req.id,
            requirement_name=req.name,
            mandatory=req.mandatory,
            importance=req.importance,
            status=score_res["status"],
            mapped_claims_count=len(req_claims),
            has_conflict=score_res["has_conflict"],
            has_temporal_issue=score_res["has_temporal_issue"],
            is_dark_spot=score_res["is_dark_spot"],
            claims=claim_responses,
            recommended_dork=dork_info["query"]
        )
        matrix_items.append(m_item)
        if score_res["is_dark_spot"]:
            dark_spot_items.append(m_item)

    db.commit()

    # Calculate KPIs
    total_reqs = len(requirements)
    covered_reqs = len([m for m in matrix_items if m.mapped_claims_count > 0])
    coverage_pct = round((covered_reqs / total_reqs * 100.0) if total_reqs > 0 else 0.0, 1)
    
    stale_count = len([m for m in matrix_items if m.has_temporal_issue])
    conflicts_count = len([cf for cf in conflict_objs if cf.relationship_type == "contradiction"])
    dark_spots_count = len(dark_spot_items)
    
    # Calculate overall risk score
    scores = [EpistemicScorer.score_requirement(r, claims_by_req.get(r.id, []), [cf for cf in conflict_objs if cf.requirement_id == r.id], temporal_audits)["priority_score"] for r in requirements]
    overall_risk = round(sum(scores) / len(scores) if scores else 0.0, 1)

    kpis = DashboardKPIs(
        total_requirements=total_reqs,
        evidence_coverage_pct=coverage_pct,
        dark_spots_count=dark_spots_count,
        detected_conflicts_count=conflicts_count,
        stale_claims_count=stale_count,
        overall_risk_score=overall_risk
    )

    # Prepare conflict responses with full claim details
    claims_lookup = {c.id: c for c in all_claims}
    conflict_responses = []
    for cf in conflict_objs:
        ca = claims_lookup.get(cf.claim_a_id)
        cb = claims_lookup.get(cf.claim_b_id)
        conflict_responses.append(ConflictRecordResponse(
            id=cf.id,
            research_id=cf.research_id,
            requirement_id=cf.requirement_id,
            requirement_name=req_map[cf.requirement_id].name if cf.requirement_id in req_map else None,
            claim_a_id=cf.claim_a_id,
            claim_b_id=cf.claim_b_id,
            claim_a=ExtractedClaimResponse.model_validate(ca) if ca else None,
            claim_b=ExtractedClaimResponse.model_validate(cb) if cb else None,
            relationship_type=cf.relationship_type,
            confidence=cf.confidence,
            explanation=cf.explanation,
            status=cf.status,
            user_notes=cf.user_notes
        ))

    source_map = {s.id: s for s in sources}
    temp_responses = [
        TemporalAuditResponse(
            id=t.id,
            research_id=t.research_id,
            source_id=t.source_id,
            source_title=source_map[t.source_id].title if t.source_id in source_map else None,
            source_url=source_map[t.source_id].url if t.source_id in source_map else None,
            detected_years=json.loads(t.detected_years or "[]"),
            detected_cycles=json.loads(t.detected_cycles or "[]"),
            calendar_deadlines=json.loads(t.calendar_deadlines or "[]"),
            temporal_status=t.temporal_status,
            staleness_reason=t.staleness_reason,
            published_date=source_map[t.source_id].published_date if t.source_id in source_map else None
        ) for t in temporal_audits
    ]

    chk_responses = [
        ChecklistItemResponse(
            id=ch.id,
            research_id=ch.research_id,
            requirement_id=ch.requirement_id,
            requirement_name=req_map[ch.requirement_id].name if ch.requirement_id in req_map else None,
            priority_score=ch.priority_score,
            risk_category=ch.risk_category,
            entropy=ch.entropy,
            title=ch.title,
            reason=ch.reason,
            recommended_action=ch.recommended_action,
            search_dork=ch.search_dork,
            is_resolved=ch.is_resolved
        ) for ch in checklist_items
    ]

    return AnalysisResultsResponse(
        research_id=research_id,
        kpis=kpis,
        matrix=matrix_items,
        dark_spots=dark_spot_items,
        conflicts=conflict_responses,
        temporal_audits=temp_responses,
        checklist=chk_responses
    )

@router.get("/research/{research_id}/results", response_model=AnalysisResultsResponse, tags=["Analysis"])
def get_analysis_results(research_id: str, db: Session = Depends(get_db)):
    """
    Returns stored analysis results or triggers on-demand pipeline if not yet executed.
    """
    claims_count = db.query(ExtractedClaim).filter(ExtractedClaim.research_id == research_id).count()
    if claims_count == 0:
        return run_analysis_pipeline(research_id, db)

    requirements = db.query(RequirementNode).filter(RequirementNode.research_id == research_id).order_by(RequirementNode.order_index).all()
    sources = db.query(SourceDocument).filter(SourceDocument.research_id == research_id).all()
    claims = db.query(ExtractedClaim).filter(ExtractedClaim.research_id == research_id).all()
    conflicts = db.query(ConflictRecord).filter(ConflictRecord.research_id == research_id).all()
    temporals = db.query(TemporalAudit).filter(TemporalAudit.research_id == research_id).all()
    checklist = db.query(ChecklistItem).filter(ChecklistItem.research_id == research_id).order_by(ChecklistItem.priority_score.desc()).all()

    req_map = {r.id: r for r in requirements}
    source_map = {s.id: s for s in sources}
    claims_by_req = {r.id: [] for r in requirements}
    for c in claims:
        if c.requirement_id and c.requirement_id in claims_by_req:
            claims_by_req[c.requirement_id].append(c)

    matrix_items = []
    dark_spot_items = []

    for req in requirements:
        req_claims = claims_by_req.get(req.id, [])
        req_conflicts = [cf for cf in conflicts if cf.requirement_id == req.id]
        score_res = EpistemicScorer.score_requirement(
            req=req,
            mapped_claims=req_claims,
            conflicts=req_conflicts,
            temporal_audits=temporals
        )

        dork = DorkGenerator.generate_dork_for_dark_spot(req.name, req.key, "", "scholarship")["query"]

        claim_responses = [
            ExtractedClaimResponse(
                id=c.id,
                research_id=c.research_id,
                source_id=c.source_id,
                requirement_id=c.requirement_id,
                claim_text=c.claim_text,
                exact_quote=c.exact_quote,
                char_start=c.char_start,
                char_end=c.char_end,
                is_grounded=c.is_grounded,
                confidence=c.confidence,
                extraction_method=c.extraction_method,
                source_title=source_map[c.source_id].title if c.source_id in source_map else None,
                source_url=source_map[c.source_id].url if c.source_id in source_map else None,
                source_domain=source_map[c.source_id].domain if c.source_id in source_map else None,
                published_date=source_map[c.source_id].published_date if c.source_id in source_map else None,
            ) for c in req_claims
        ]

        m_item = EpistemicMatrixItem(
            requirement_id=req.id,
            requirement_name=req.name,
            mandatory=req.mandatory,
            importance=req.importance,
            status=score_res["status"],
            mapped_claims_count=len(req_claims),
            has_conflict=score_res["has_conflict"],
            has_temporal_issue=score_res["has_temporal_issue"],
            is_dark_spot=score_res["is_dark_spot"],
            claims=claim_responses,
            recommended_dork=dork
        )
        matrix_items.append(m_item)
        if score_res["is_dark_spot"]:
            dark_spot_items.append(m_item)

    total_reqs = len(requirements)
    covered_reqs = len([m for m in matrix_items if m.mapped_claims_count > 0])
    coverage_pct = round((covered_reqs / total_reqs * 100.0) if total_reqs > 0 else 0.0, 1)

    scores = [EpistemicScorer.score_requirement(r, claims_by_req.get(r.id, []), [cf for cf in conflicts if cf.requirement_id == r.id], temporals)["priority_score"] for r in requirements]
    overall_risk = round(sum(scores) / len(scores) if scores else 0.0, 1)

    kpis = DashboardKPIs(
        total_requirements=total_reqs,
        evidence_coverage_pct=coverage_pct,
        dark_spots_count=len(dark_spot_items),
        detected_conflicts_count=len([cf for cf in conflicts if cf.relationship_type == "contradiction"]),
        stale_claims_count=len([m for m in matrix_items if m.has_temporal_issue]),
        overall_risk_score=overall_risk
    )

    claims_lookup = {c.id: c for c in claims}
    conflict_responses = []
    for cf in conflicts:
        ca = claims_lookup.get(cf.claim_a_id)
        cb = claims_lookup.get(cf.claim_b_id)
        conflict_responses.append(ConflictRecordResponse(
            id=cf.id,
            research_id=cf.research_id,
            requirement_id=cf.requirement_id,
            requirement_name=req_map[cf.requirement_id].name if cf.requirement_id in req_map else None,
            claim_a_id=cf.claim_a_id,
            claim_b_id=cf.claim_b_id,
            claim_a=ExtractedClaimResponse.model_validate(ca) if ca else None,
            claim_b=ExtractedClaimResponse.model_validate(cb) if cb else None,
            relationship_type=cf.relationship_type,
            confidence=cf.confidence,
            explanation=cf.explanation,
            status=cf.status,
            user_notes=cf.user_notes
        ))

    temp_responses = [
        TemporalAuditResponse(
            id=t.id,
            research_id=t.research_id,
            source_id=t.source_id,
            source_title=source_map[t.source_id].title if t.source_id in source_map else None,
            source_url=source_map[t.source_id].url if t.source_id in source_map else None,
            detected_years=json.loads(t.detected_years or "[]"),
            detected_cycles=json.loads(t.detected_cycles or "[]"),
            calendar_deadlines=json.loads(t.calendar_deadlines or "[]"),
            temporal_status=t.temporal_status,
            staleness_reason=t.staleness_reason,
            published_date=source_map[t.source_id].published_date if t.source_id in source_map else None
        ) for t in temporals
    ]

    chk_responses = [
        ChecklistItemResponse(
            id=ch.id,
            research_id=ch.research_id,
            requirement_id=ch.requirement_id,
            requirement_name=req_map[ch.requirement_id].name if ch.requirement_id in req_map else None,
            priority_score=ch.priority_score,
            risk_category=ch.risk_category,
            entropy=ch.entropy,
            title=ch.title,
            reason=ch.reason,
            recommended_action=ch.recommended_action,
            search_dork=ch.search_dork,
            is_resolved=ch.is_resolved
        ) for ch in checklist
    ]

    return AnalysisResultsResponse(
        research_id=research_id,
        kpis=kpis,
        matrix=matrix_items,
        dark_spots=dark_spot_items,
        conflicts=conflict_responses,
        temporal_audits=temp_responses,
        checklist=chk_responses
    )

# --- Granular Endpoints ---
@router.get("/research/{research_id}/dark-spots", tags=["Analysis"])
def get_dark_spots(research_id: str, db: Session = Depends(get_db)):
    results = get_analysis_results(research_id, db)
    return results.dark_spots

@router.get("/research/{research_id}/conflicts", tags=["Analysis"])
def get_conflicts(research_id: str, db: Session = Depends(get_db)):
    results = get_analysis_results(research_id, db)
    return results.conflicts

@router.get("/research/{research_id}/temporal", tags=["Analysis"])
def get_temporal_audits(research_id: str, db: Session = Depends(get_db)):
    results = get_analysis_results(research_id, db)
    return results.temporal_audits

@router.get("/research/{research_id}/checklist", tags=["Analysis"])
def get_checklist(research_id: str, db: Session = Depends(get_db)):
    results = get_analysis_results(research_id, db)
    return results.checklist

@router.patch("/conflicts/{conflict_id}", response_model=ConflictRecordResponse, tags=["Analysis"])
def update_conflict_status(conflict_id: str, payload: ConflictStatusUpdate, db: Session = Depends(get_db)):
    conflict = db.query(ConflictRecord).filter(ConflictRecord.id == conflict_id).first()
    if not conflict:
        raise HTTPException(status_code=404, detail="Conflict record not found.")

    conflict.status = payload.status
    if payload.user_notes is not None:
        conflict.user_notes = payload.user_notes

    db.commit()
    db.refresh(conflict)

    ca = db.query(ExtractedClaim).filter(ExtractedClaim.id == conflict.claim_a_id).first()
    cb = db.query(ExtractedClaim).filter(ExtractedClaim.id == conflict.claim_b_id).first()

    return ConflictRecordResponse(
        id=conflict.id,
        research_id=conflict.research_id,
        requirement_id=conflict.requirement_id,
        claim_a_id=conflict.claim_a_id,
        claim_b_id=conflict.claim_b_id,
        claim_a=ExtractedClaimResponse.model_validate(ca) if ca else None,
        claim_b=ExtractedClaimResponse.model_validate(cb) if cb else None,
        relationship_type=conflict.relationship_type,
        confidence=conflict.confidence,
        explanation=conflict.explanation,
        status=conflict.status,
        user_notes=conflict.user_notes
    )

@router.patch("/checklist/{item_id}", response_model=ChecklistItemResponse, tags=["Analysis"])
def update_checklist_status(item_id: str, payload: ChecklistItemUpdate, db: Session = Depends(get_db)):
    item = db.query(ChecklistItem).filter(ChecklistItem.id == item_id).first()
    if not item:
        raise HTTPException(status_code=404, detail="Checklist item not found.")

    item.is_resolved = payload.is_resolved
    db.commit()
    db.refresh(item)
    return ChecklistItemResponse.model_validate(item)

# --- Export Endpoints ---
@router.get("/research/{research_id}/export/json", tags=["Export"])
def export_research_json(research_id: str, db: Session = Depends(get_db)):
    data = generate_research_json_export(db, research_id)
    if not data:
        raise HTTPException(status_code=404, detail="Research project not found.")
    return JSONResponse(
        content=data,
        headers={"Content-Disposition": f"attachment; filename=nullspace_audit_{research_id}.json"}
    )

@router.get("/research/{research_id}/export/pdf", tags=["Export"])
def export_research_pdf(research_id: str, db: Session = Depends(get_db)):
    pdf_bytes = generate_research_pdf_export(db, research_id)
    if not pdf_bytes:
        raise HTTPException(status_code=404, detail="Research project not found.")
    return Response(
        content=pdf_bytes,
        media_type="application/pdf",
        headers={"Content-Disposition": f"attachment; filename=nullspace_report_{research_id}.pdf"}
    )

