import io
import json
from typing import Dict, Any
from sqlalchemy.orm import Session
from app.models.project import (
    ResearchProject, RequirementNode, SourceDocument, ExtractedClaim, 
    ClaimRequirementMapping, ConflictRecord, TemporalAudit, ChecklistItem
)
from reportlab.lib.pagesizes import letter
from reportlab.lib import colors
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, PageBreak, HRFlowable

def generate_research_json_export(db: Session, research_id: str) -> Dict[str, Any]:
    project = db.query(ResearchProject).filter(ResearchProject.id == research_id).first()
    if not project:
        return {}

    reqs = db.query(RequirementNode).filter(RequirementNode.research_id == research_id).order_by(RequirementNode.order_index).all()
    sources = db.query(SourceDocument).filter(SourceDocument.research_id == research_id).all()
    claims = db.query(ExtractedClaim).filter(ExtractedClaim.research_id == research_id).all()
    conflicts = db.query(ConflictRecord).filter(ConflictRecord.research_id == research_id).all()
    temporals = db.query(TemporalAudit).filter(TemporalAudit.research_id == research_id).all()
    checklist = db.query(ChecklistItem).filter(ChecklistItem.research_id == research_id).all()

    return {
        "engine": "NullSpace Epistemic Audit Engine",
        "version": "1.0.0",
        "exported_at": str(project.updated_at),
        "project": {
            "id": project.id,
            "title": project.title,
            "domain": project.domain,
            "objective": project.objective,
            "created_at": str(project.created_at)
        },
        "requirements": [
            {
                "id": r.id,
                "key": r.key,
                "name": r.name,
                "description": r.description,
                "mandatory": r.mandatory,
                "importance": r.importance
            } for r in reqs
        ],
        "sources": [
            {
                "id": s.id,
                "title": s.title,
                "url": s.url,
                "domain": s.domain,
                "content_hash": s.content_hash,
                "published_date": s.published_date,
                "status": s.status,
                "is_fixture": s.is_fixture
            } for s in sources
        ],
        "claims": [
            {
                "id": c.id,
                "requirement_id": c.requirement_id,
                "source_id": c.source_id,
                "claim_text": c.claim_text,
                "exact_quote": c.exact_quote,
                "char_start": c.char_start,
                "char_end": c.char_end,
                "is_grounded": c.is_grounded,
                "confidence": c.confidence,
                "extraction_method": c.extraction_method
            } for c in claims
        ],
        "conflicts": [
            {
                "id": cf.id,
                "requirement_id": cf.requirement_id,
                "claim_a_id": cf.claim_a_id,
                "claim_b_id": cf.claim_b_id,
                "relationship_type": cf.relationship_type,
                "confidence": cf.confidence,
                "explanation": cf.explanation,
                "status": cf.status,
                "user_notes": cf.user_notes
            } for cf in conflicts
        ],
        "temporal_audits": [
            {
                "id": t.id,
                "source_id": t.source_id,
                "detected_years": json.loads(t.detected_years or "[]"),
                "detected_cycles": json.loads(t.detected_cycles or "[]"),
                "temporal_status": t.temporal_status,
                "staleness_reason": t.staleness_reason
            } for t in temporals
        ],
        "verification_checklist": [
            {
                "id": ch.id,
                "requirement_id": ch.requirement_id,
                "priority_score": ch.priority_score,
                "risk_category": ch.risk_category,
                "entropy": ch.entropy,
                "title": ch.title,
                "reason": ch.reason,
                "recommended_action": ch.recommended_action,
                "search_dork": ch.search_dork,
                "is_resolved": ch.is_resolved
            } for ch in checklist
        ]
    }

def generate_research_pdf_export(db: Session, research_id: str) -> bytes:
    data = generate_research_json_export(db, research_id)
    if not data:
        return b""

    buffer = io.BytesIO()
    doc = SimpleDocTemplate(
        buffer,
        pagesize=letter,
        rightMargin=40, leftMargin=40,
        topMargin=40, bottomMargin=40
    )

    styles = getSampleStyleSheet()
    
    # Custom styles
    header_style = ParagraphStyle(
        'DocHeader',
        parent=styles['Heading1'],
        fontSize=20,
        leading=24,
        textColor=colors.HexColor('#0F172A')
    )
    sub_style = ParagraphStyle(
        'SubHeader',
        parent=styles['Normal'],
        fontSize=10,
        leading=14,
        textColor=colors.HexColor('#64748B')
    )
    h2_style = ParagraphStyle(
        'SectionH2',
        parent=styles['Heading2'],
        fontSize=13,
        leading=17,
        textColor=colors.HexColor('#1E293B'),
        spaceBefore=14,
        spaceAfter=6
    )
    body_style = ParagraphStyle(
        'BodyDark',
        parent=styles['Normal'],
        fontSize=9,
        leading=13,
        textColor=colors.HexColor('#334155')
    )
    badge_crit = ParagraphStyle('BadgeCrit', parent=body_style, textColor=colors.HexColor('#DC2626'), fontName="Helvetica-Bold")
    badge_warn = ParagraphStyle('BadgeWarn', parent=body_style, textColor=colors.HexColor('#D97706'), fontName="Helvetica-Bold")
    badge_info = ParagraphStyle('BadgeInfo', parent=body_style, textColor=colors.HexColor('#2563EB'))

    elements = []

    # Title Banner
    elements.append(Paragraph("<b>NULLSPACE</b> — Epistemic Audit Report", header_style))
    elements.append(Paragraph(f"Project: <b>{data['project']['title']}</b> | Domain: <i>{data['project']['domain']}</i>", sub_style))
    elements.append(Paragraph(f"Research Goal: {data['project']['objective']}", body_style))
    elements.append(Spacer(1, 10))
    elements.append(HRFlowable(width="100%", thickness=1, color=colors.HexColor('#CBD5E1'), spaceBefore=5, spaceAfter=15))

    # 1. Executive Summary Table
    total_reqs = len(data["requirements"])
    total_claims = len(data["claims"])
    total_conflicts = len([c for c in data["conflicts"] if c["relationship_type"] == "contradiction"])
    total_sources = len(data["sources"])
    
    # Identify Dark Spots
    mapped_req_ids = {c["requirement_id"] for c in data["claims"] if c["requirement_id"]}
    dark_spots = [r for r in data["requirements"] if r["mandatory"] and r["id"] not in mapped_req_ids]

    summary_data = [
        ["Total Requirements", str(total_reqs), "Total Ingested Sources", str(total_sources)],
        ["Grounded Atomic Claims", str(total_claims), "Active Contradictions", str(total_conflicts)],
        ["Digital Dark Spots (InDegree=0)", str(len(dark_spots)), "Audit Status", "COMPLETED"]
    ]
    sum_table = Table(summary_data, colWidths=[160, 100, 160, 110])
    sum_table.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,-1), colors.HexColor('#F8FAFC')),
        ('TEXTCOLOR', (0,0), (-1,-1), colors.HexColor('#1E293B')),
        ('FONTNAME', (0,0), (-1,-1), 'Helvetica'),
        ('FONTSIZE', (0,0), (-1,-1), 9),
        ('GRID', (0,0), (-1,-1), 0.5, colors.HexColor('#E2E8F0')),
        ('TOPPADDING', (0,0), (-1,-1), 5),
        ('BOTTOMPADDING', (0,0), (-1,-1), 5),
    ]))
    elements.append(sum_table)
    elements.append(Spacer(1, 15))

    # 2. Digital Dark Spots (If any)
    elements.append(Paragraph("<b>1. DIGITAL DARK SPOTS (MANDATORY REQUIREMENTS WITH ZERO EVIDENCE)</b>", h2_style))
    if dark_spots:
        for ds in dark_spots:
            elements.append(Paragraph(f"• <b>{ds['name']}</b> (Importance: {ds['importance']}/5) — [InDegree = 0]", badge_crit))
            elements.append(Paragraph(f"  <i>Description:</i> {ds['description']}", body_style))
            elements.append(Paragraph(f"  <i>Risk:</i> Mandatory requirement completely omitted by reviewed sources.", body_style))
            elements.append(Spacer(1, 4))
    else:
        elements.append(Paragraph("None detected. All mandatory requirements have at least one mapped claim.", body_style))
    elements.append(Spacer(1, 10))

    # 3. Cross-Source Contradictions
    elements.append(Paragraph("<b>2. CROSS-SOURCE CONTRADICTION MATRIX</b>", h2_style))
    if data["conflicts"]:
        conf_rows = [["Requirement", "Conflict Finding", "Status"]]
        for cf in data["conflicts"][:6]:
            conf_rows.append([
                Paragraph(cf["requirement_id"], body_style),
                Paragraph(cf["explanation"], body_style),
                Paragraph(cf["status"].upper(), badge_crit if cf["status"] == "confirmed" else badge_warn)
            ])
        c_table = Table(conf_rows, colWidths=[120, 330, 80])
        c_table.setStyle(TableStyle([
            ('BACKGROUND', (0,0), (-1,0), colors.HexColor('#F1F5F9')),
            ('GRID', (0,0), (-1,-1), 0.5, colors.HexColor('#CBD5E1')),
            ('TOPPADDING', (0,0), (-1,-1), 4),
            ('BOTTOMPADDING', (0,0), (-1,-1), 4),
        ]))
        elements.append(c_table)
    else:
        elements.append(Paragraph("No contradictory claim pairs detected.", body_style))
    elements.append(Spacer(1, 10))

    # 4. Prioritized Verification Checklist
    elements.append(Paragraph("<b>3. ENTROPY-RANKED VERIFICATION CHECKLIST</b>", h2_style))
    if data["verification_checklist"]:
        chk_rows = [["Risk", "Score", "Verification Item & Action", "Target Dork"]]
        for chk in data["verification_checklist"][:6]:
            r_style = badge_crit if chk["risk_category"] == "Critical" else (badge_warn if chk["risk_category"] == "High" else badge_info)
            chk_rows.append([
                Paragraph(chk["risk_category"], r_style),
                Paragraph(f"{chk['priority_score']}", body_style),
                Paragraph(f"<b>{chk['title']}</b><br/>{chk['recommended_action']}", body_style),
                Paragraph(chk["search_dork"][:70] + "...", body_style)
            ])
        chk_table = Table(chk_rows, colWidths=[60, 45, 275, 150])
        chk_table.setStyle(TableStyle([
            ('BACKGROUND', (0,0), (-1,0), colors.HexColor('#F1F5F9')),
            ('GRID', (0,0), (-1,-1), 0.5, colors.HexColor('#CBD5E1')),
            ('TOPPADDING', (0,0), (-1,-1), 4),
            ('BOTTOMPADDING', (0,0), (-1,-1), 4),
        ]))
        elements.append(chk_table)

    elements.append(Spacer(1, 15))
    elements.append(HRFlowable(width="100%", thickness=0.5, color=colors.HexColor('#94A3B8'), spaceBefore=10, spaceAfter=10))
    elements.append(Paragraph("<b>DISCLAIMER:</b> Generated automatically by NullSpace Epistemic Engine. Evidence status reflects coverage consistency across reviewed sources and does not constitute independent legal or government proof. Verify with primary gazette notifications.", sub_style))

    doc.build(elements)
    buffer.seek(0)
    return buffer.getvalue()
