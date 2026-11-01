import uuid
import datetime
from typing import Dict, Any, List
from app.models.project import (
    ResearchProject, RequirementNode, SourceDocument, ExtractedClaim, 
    ClaimRequirementMapping, ConflictRecord, TemporalAudit, ChecklistItem
)
from app.services.extraction.claim_extractor import ClaimExtractor
from app.services.temporal.auditor import TemporalAuditor
from app.services.prioritization.entropy import EpistemicScorer
from app.services.dorks.generator import DorkGenerator
from app.core.config import settings

# 1. Mock Official Notice
FIXTURE_NOTICE_TEXT = (
    "GOVERNMENT OF BHARAT (SYNTHETIC SIMULATION)\n"
    "MINISTRY OF HIGHER EDUCATION & TALENT ADVANCEMENT\n"
    "OFFICIAL NOTIFICATION: NATIONAL PRERANA MERIT FELLOWSHIP (2026-27)\n\n"
    "1. PREAMBLE & OBJECTIVE\n"
    "The National Prerana Merit Fellowship provides full tuition grant and educational stipend for meritorious students "
    "pursuing undergraduate technical and liberal degrees across recognized national institutions.\n\n"
    "2. MANDATORY ELIGIBILITY CRITERIA\n"
    "Applicants must be bonafide citizens of India enrolled in a recognized full-time degree program with a minimum "
    "aggregate score of 80% marks in their preceding qualifying examinations.\n\n"
    "3. FAMILY INCOME THRESHOLD\n"
    "Annual gross family income must not exceed Rs. 3,00,000 from all certified sources to qualify for the scheme.\n\n"
    "4. MANDATORY APPLICATION DOCUMENTS\n"
    "Applicants must submit a verified income certificate and secondary school marksheet during online submission.\n\n"
    "5. SCHOLARSHIP DISBURSEMENT AMOUNT\n"
    "Selected scholars shall receive a non-refundable financial stipend of Rs. 60,000 per academic annum.\n\n"
    "6. IMPORTANT DATES & DEADLINE\n"
    "The final deadline for online application submission is 31 December 2026 at 11:59 PM IST.\n\n"
    "[Note: Submission mode, authorized application portal, and multi-year renewal rules have been deferred to a subsequent gazette notification.]"
)

# 2. Mock Educational Blog A
FIXTURE_BLOG_A_TEXT = (
    "CAMPUS PULSE EDUCATION FORUM — SCHOLARSHIP ANALYSIS (ACADEMIC YEAR 2025-26)\n"
    "Guide to the Prerana Merit Fellowship Rules and Eligibility Updates\n\n"
    "Thousands of undergraduate students apply every cycle for the prestigious National Prerana Fellowship. "
    "Here is our comprehensive summary based on the latest education department briefings:\n\n"
    "Eligibility and Income Limit:\n"
    "Under updated ministry circulars, the family income ceiling has been expanded to Rs. 4,00,000 for this academic cycle, "
    "allowing more middle-income applicants to qualify.\n\n"
    "Document Requirements:\n"
    "Applicants must upload their income certificate and secondary school marksheet with proper gazetted officer attestations.\n\n"
    "Renewal Policy and Retention Rules:\n"
    "Students must note that annual renewal is mandatory and requires maintaining a 7.5 CGPA with at least 75% attendance.\n\n"
    "Stay tuned as registration continues through the semester."
)

# 3. Mock Scholarship Blog B
FIXTURE_BLOG_B_TEXT = (
    "EDUCATION WATCH PORTAL — SCHOLARSHIP DESK ARCHIVE (REFERENCE YEAR 2024)\n"
    "What You Need to Know Before Applying for National Merit Fellowships\n\n"
    "Many scholarship portals report confusing requirements regarding the National Prerana Fellowship scheme. "
    "Here is the verified checklist compiled from regional nodal centers:\n\n"
    "Financial Criteria:\n"
    "Eligible family income must remain strictly under Rs. 2,00,000 per annum for priority merit allocation.\n\n"
    "Verification Documents:\n"
    "Candidates must provide an income certificate and recent 6-month bank statement to confirm domestic financial standing.\n\n"
    "Continuation Policy:\n"
    "Once granted, continuation is automatic; subsequent annual renewal is not required for the remainder of the degree.\n\n"
    "Please check with local district welfare offices for portal access forms."
)

def populate_scholarship_demo_fixture(db_session) -> ResearchProject:
    """
    Deterministically creates the complete Scholarship Demo dataset.
    Requires ZERO external API calls.
    """
    project_id = f"demo_proj_{uuid.uuid4().hex[:8]}"
    project = ResearchProject(
        id=project_id,
        title="National Prerana Merit Fellowship (Demo)",
        domain="scholarship",
        objective="Find all mandatory requirements, deadlines, eligibility limits, and documentation for applying for the National Prerana Merit Fellowship."
    )
    db_session.add(project)
    db_session.flush()

    # 1. Define Counterfactual Decision Requirement Graph
    req_specs = [
        ("req_eligibility", "eligibility", "Applicant Eligibility Criteria", "Who qualifies to apply (citizenship, domicile, age limits, academic qualifications)?", True, 5, 1),
        ("req_income_threshold", "income_threshold", "Family Income Threshold", "What is the maximum permitted annual gross family income limit?", True, 5, 2),
        ("req_scholarship_amount", "scholarship_amount", "Scholarship Amount & Benefits", "What is the total financial benefit, tuition fee waiver, or stipend amount?", True, 4, 3),
        ("req_required_documents", "required_documents", "Mandatory Submission Documents", "Which documents must applicants submit (income certificate, marksheet, bank statement)?", True, 5, 4),
        ("req_application_deadline", "application_deadline", "Application Window & Deadline", "When does the application open and close for the applicable academic year?", True, 5, 5),
        ("req_renewal_policy", "renewal_policy", "Renewal Policy & Continuation Rules", "What are the continuation or renewal conditions (minimum CGPA, annual re-verification)?", True, 5, 6),
        ("req_official_portal", "official_portal", "Official Application Portal & Mode", "Where must applications be submitted (official URL or physical portal)?", True, 4, 7),
    ]

    req_map = {}
    for r_id, key, name, desc, mand, imp, idx in req_specs:
        full_id = f"{project_id}_{r_id}"
        node = RequirementNode(
            id=full_id,
            research_id=project_id,
            key=key,
            name=name,
            description=desc,
            mandatory=mand,
            importance=imp,
            order_index=idx
        )
        db_session.add(node)
        req_map[key] = node

    db_session.flush()

    # 2. Add Sources
    sources_data = [
        {
            "id": f"{project_id}_src_notice",
            "url": "https://notice.meritfellowship-synthetic.org/gazette-2026",
            "domain": "notice.meritfellowship-synthetic.org",
            "title": "Official Gazette Notification: National Prerana Merit Fellowship (AY 2026-27)",
            "raw_text": FIXTURE_NOTICE_TEXT,
            "pub_date": "2026-10-15"
        },
        {
            "id": f"{project_id}_src_blog_a",
            "url": "https://campuspulse-synthetic.edu/prerana-fellowship-guide-2025",
            "domain": "campuspulse-synthetic.edu",
            "title": "Campus Pulse Education Forum: Prerana Fellowship 2025-26 Analysis",
            "raw_text": FIXTURE_BLOG_A_TEXT,
            "pub_date": "2025-08-20"
        },
        {
            "id": f"{project_id}_src_blog_b",
            "url": "https://educationwatch-synthetic.in/archive/merit-fellowship-checklist-2024",
            "domain": "educationwatch-synthetic.in",
            "title": "Education Watch Desk Archive: Fellowship Criteria (2024 Reference)",
            "raw_text": FIXTURE_BLOG_B_TEXT,
            "pub_date": "2024-05-10"
        }
    ]

    source_objs = {}
    for s_info in sources_data:
        import hashlib
        c_hash = hashlib.sha256(s_info["raw_text"].encode("utf-8")).hexdigest()
        src = SourceDocument(
            id=s_info["id"],
            research_id=project_id,
            url=s_info["url"],
            domain=s_info["domain"],
            title=s_info["title"],
            content_hash=c_hash,
            raw_text=s_info["raw_text"],
            published_date=s_info["pub_date"],
            retrieved_at=datetime.datetime.utcnow(),
            status="ingested",
            is_fixture=True
        )
        db_session.add(src)
        source_objs[s_info["id"]] = src

    db_session.flush()

    # 3. Grounded Claims with verified exact offsets
    # Exact quotes to extract and verify
    claims_spec = [
        # From Notice
        (
            f"{project_id}_src_notice", "eligibility",
            "Applicants must be bonafide citizens of India enrolled in a recognized full-time degree program with a minimum aggregate score of 80% marks in their preceding qualifying examinations.",
            "Applicants must be bonafide citizens of India enrolled in a recognized full-time degree program with a minimum aggregate score of 80% marks in their preceding qualifying examinations."
        ),
        (
            f"{project_id}_src_notice", "income_threshold",
            "Annual gross family income must not exceed Rs. 3,00,000 from all certified sources to qualify for the scheme.",
            "Annual gross family income must not exceed Rs. 3,00,000 from all certified sources to qualify for the scheme."
        ),
        (
            f"{project_id}_src_notice", "required_documents",
            "Applicants must submit a verified income certificate and secondary school marksheet during online submission.",
            "Applicants must submit a verified income certificate and secondary school marksheet during online submission."
        ),
        (
            f"{project_id}_src_notice", "scholarship_amount",
            "Selected scholars shall receive a non-refundable financial stipend of Rs. 60,000 per academic annum.",
            "Selected scholars shall receive a non-refundable financial stipend of Rs. 60,000 per academic annum."
        ),
        (
            f"{project_id}_src_notice", "application_deadline",
            "The final deadline for online application submission is 31 December 2026 at 11:59 PM IST.",
            "The final deadline for online application submission is 31 December 2026 at 11:59 PM IST."
        ),
        # Notice intentionally omits official_portal and renewal_policy!
        # renewal_policy is discussed contradictorily by Blog A and Blog B.
        # official_portal is omitted across ALL 3 sources -> InDegree = 0 GUARANTEED DIGITAL DARK SPOT!

        # From Blog A
        (
            f"{project_id}_src_blog_a", "income_threshold",
            "Under updated ministry circulars, the family income ceiling has been expanded to Rs. 4,00,000 for this academic cycle, allowing more middle-income applicants to qualify.",
            "Under updated ministry circulars, the family income ceiling has been expanded to Rs. 4,00,000 for this academic cycle, allowing more middle-income applicants to qualify."
        ),
        (
            f"{project_id}_src_blog_a", "required_documents",
            "Applicants must upload their income certificate and secondary school marksheet with proper gazetted officer attestations.",
            "Applicants must upload their income certificate and secondary school marksheet with proper gazetted officer attestations."
        ),
        (
            f"{project_id}_src_blog_a", "renewal_policy",
            "Students must note that annual renewal is mandatory and requires maintaining a 7.5 CGPA with at least 75% attendance.",
            "Students must note that annual renewal is mandatory and requires maintaining a 7.5 CGPA with at least 75% attendance."
        ),

        # From Blog B
        (
            f"{project_id}_src_blog_b", "income_threshold",
            "Eligible family income must remain strictly under Rs. 2,00,000 per annum for priority merit allocation.",
            "Eligible family income must remain strictly under Rs. 2,00,000 per annum for priority merit allocation."
        ),
        (
            f"{project_id}_src_blog_b", "required_documents",
            "Candidates must provide an income certificate and recent 6-month bank statement to confirm domestic financial standing.",
            "Candidates must provide an income certificate and recent 6-month bank statement to confirm domestic financial standing."
        ),
        (
            f"{project_id}_src_blog_b", "renewal_policy",
            "Once granted, continuation is automatic; subsequent annual renewal is not required for the remainder of the degree.",
            "Once granted, continuation is automatic; subsequent annual renewal is not required for the remainder of the degree."
        )
    ]

    claim_objs = []
    claims_by_req = {}

    for s_id, req_key, claim_text, quote in claims_spec:
        src = source_objs[s_id]
        is_grounded, start, end = ClaimExtractor.verify_and_ground_quote(src.raw_text, quote)
        
        req_node = req_map.get(req_key)
        req_id = req_node.id if req_node else None

        claim = ExtractedClaim(
            id=f"claim_{uuid.uuid4().hex[:10]}",
            research_id=project_id,
            source_id=s_id,
            requirement_id=req_id,
            claim_text=claim_text,
            exact_quote=src.raw_text[start:end] if is_grounded else quote,
            char_start=start,
            char_end=end,
            is_grounded=is_grounded,
            confidence=0.98 if is_grounded else 0.5,
            extraction_method="deterministic_fixture"
        )
        db_session.add(claim)
        claim_objs.append(claim)

        if req_id not in claims_by_req:
            claims_by_req[req_id] = []
        claims_by_req[req_id].append(claim)

        # Mapping record
        if req_id:
            mapping = ClaimRequirementMapping(
                id=f"map_{uuid.uuid4().hex[:10]}",
                research_id=project_id,
                claim_id=claim.id,
                requirement_id=req_id,
                confidence=0.98,
                mapping_method="fixture_exact",
                explanation=f"Exact thematic correspondence to requirement '{req_node.name}'."
            )
            db_session.add(mapping)

    db_session.flush()

    # 4. Temporal Auditing
    temporal_audits = []
    for s_id, src in source_objs.items():
        t_data = TemporalAuditor.audit_source_temporality(
            source_id=src.id,
            raw_text=src.raw_text,
            published_date=src.published_date,
            research_id=project_id,
            current_year=2026
        )
        audit = TemporalAudit(**t_data)
        db_session.add(audit)
        temporal_audits.append(audit)

    db_session.flush()

    # 5. Contradiction Detection
    # Notice vs Blog A vs Blog B on Income Threshold (Rs 3L vs Rs 4L vs Rs 2L)
    # Notice vs Blog B on Required Documents (marksheet vs bank statement)
    # Blog A vs Blog B on Renewal Policy (mandatory renewal vs not required)
    inc_claims = claims_by_req[req_map["income_threshold"].id]
    c_notice_inc = next(c for c in inc_claims if c.source_id.endswith("notice"))
    c_blog_a_inc = next(c for c in inc_claims if c.source_id.endswith("blog_a"))
    c_blog_b_inc = next(c for c in inc_claims if c.source_id.endswith("blog_b"))

    conflict1 = ConflictRecord(
        id=f"conflict_{uuid.uuid4().hex[:10]}",
        research_id=project_id,
        requirement_id=req_map["income_threshold"].id,
        claim_a_id=c_notice_inc.id,
        claim_b_id=c_blog_a_inc.id,
        relationship_type="contradiction",
        confidence=0.96,
        explanation="Direct numeric conflict: Official Notice states income ceiling is Rs. 3,00,000, whereas Blog A states it was expanded to Rs. 4,00,000.",
        status="confirmed",
        user_notes="Synthetic fixture: Blog A claims ceiling was raised to 4 Lakh for 2025-26 cycle."
    )
    db_session.add(conflict1)

    conflict2 = ConflictRecord(
        id=f"conflict_{uuid.uuid4().hex[:10]}",
        research_id=project_id,
        requirement_id=req_map["income_threshold"].id,
        claim_a_id=c_notice_inc.id,
        claim_b_id=c_blog_b_inc.id,
        relationship_type="contradiction",
        confidence=0.96,
        explanation="Direct numeric conflict: Official Notice mandates Rs. 3,00,000 ceiling, while Blog B states income must be strictly under Rs. 2,00,000.",
        status="confirmed",
        user_notes="Synthetic fixture: Blog B references 2024 guidelines."
    )
    db_session.add(conflict2)

    # Renewal policy conflict between Blog A and Blog B
    ren_claims = claims_by_req[req_map["renewal_policy"].id]
    c_blog_a_ren = next(c for c in ren_claims if c.source_id.endswith("blog_a"))
    c_blog_b_ren = next(c for c in ren_claims if c.source_id.endswith("blog_b"))

    conflict3 = ConflictRecord(
        id=f"conflict_{uuid.uuid4().hex[:10]}",
        research_id=project_id,
        requirement_id=req_map["renewal_policy"].id,
        claim_a_id=c_blog_a_ren.id,
        claim_b_id=c_blog_b_ren.id,
        relationship_type="contradiction",
        confidence=0.94,
        explanation="Direct policy opposition: Blog A claims annual renewal is mandatory with 7.5 CGPA, whereas Blog B claims continuation is automatic and renewal is not required.",
        status="confirmed",
        user_notes="Official notice itself contains NO renewal guidance (Dark Spot in primary source)."
    )
    db_session.add(conflict3)

    # Documentation conflict: marksheet vs bank statement
    doc_claims = claims_by_req[req_map["required_documents"].id]
    c_notice_doc = next(c for c in doc_claims if c.source_id.endswith("notice"))
    c_blog_b_doc = next(c for c in doc_claims if c.source_id.endswith("blog_b"))

    conflict4 = ConflictRecord(
        id=f"conflict_{uuid.uuid4().hex[:10]}",
        research_id=project_id,
        requirement_id=req_map["required_documents"].id,
        claim_a_id=c_notice_doc.id,
        claim_b_id=c_blog_b_doc.id,
        relationship_type="contradiction",
        confidence=0.88,
        explanation="Documentation mismatch: Official Notice mandates secondary school marksheet, whereas Blog B mandates a 6-month bank statement.",
        status="requires_review",
        user_notes="Unclear whether bank statements are additional or substituted."
    )
    db_session.add(conflict4)

    db_session.flush()

    # 6. Prioritized Verification Checklist Items
    # High risk for Income Threshold (contradictions), Renewal Policy (contradictions + omission in official notice), etc.
    checklist_specs = [
        (
            req_map["official_portal"].id, 94.0, "Critical", 1.0,
            "Resolve Digital Dark Spot: Missing Official Submission Portal",
            "Mandatory requirement 'Official Application Portal' is completely omitted across all reviewed sources. Neither the gazette notice nor secondary portals identify where applications are submitted.",
            "Locate the official department portal or ministry web advisory for the authorized submission URL.",
            'site:gov.in "National Prerana Merit Fellowship" "application portal" OR "apply online" 2026'
        ),
        (
            req_map["income_threshold"].id, 92.5, "Critical", 0.85,
            "Arbitrate Tri-Source Income Threshold Discrepancy",
            "Severe numeric divergence across 3 sources: Rs. 3 Lakh (Official Gazette) vs Rs. 4 Lakh (Blog A) vs Rs. 2 Lakh (Blog B).",
            "Verify the official gazette PDF to confirm whether an amendment raised the cap to Rs. 4 Lakh for AY 2026-27.",
            'site:gov.in "National Prerana" "income threshold" "3,00,000" OR "4,00,000" 2026 filetype:pdf'
        ),
        (
            req_map["renewal_policy"].id, 88.0, "Critical", 0.90,
            "Investigate Deferred Renewal Policy & Conflicting Secondary Claims",
            "Primary Gazette explicitly deferred renewal rules to subsequent notice. Secondary blogs contradict: Blog A mandates annual renewal with 7.5 CGPA while Blog B claims renewal is not required.",
            "Locate subsequent amendment notification or search for the official scholarship renewal handbook.",
            'site:gov.in "National Prerana Merit Fellowship" "renewal policy" OR "CGPA" 2026'
        ),
        (
            req_map["required_documents"].id, 68.0, "High", 0.65,
            "Clarify Bank Statement vs Marksheet Requirement",
            "Blog B claims a 6-month bank statement is mandatory, whereas the Official Gazette specifies income certificate and secondary school marksheet.",
            "Inspect the online portal instructions page to see if bank statements are mandatory during initial upload.",
            '"National Prerana" "required documents" "bank statement" OR "marksheet" official notice'
        ),
        (
            req_map["application_deadline"].id, 35.0, "Medium", 0.15,
            "Confirm Active Portal Submission Window",
            "Official Gazette specifies 31 December 2026. Verify portal server uptime and closing timezone.",
            "Check live portal countdown or technical helpdesk announcement.",
            'site:meritfellowship-synthetic.org "deadline" OR "portal closing"'
        )
    ]

    for req_id, p_score, risk_cat, entropy, title, reason, action, dork in checklist_specs:
        chk = ChecklistItem(
            id=f"chk_{uuid.uuid4().hex[:10]}",
            research_id=project_id,
            requirement_id=req_id,
            priority_score=p_score,
            risk_category=risk_cat,
            entropy=entropy,
            title=title,
            reason=reason,
            recommended_action=action,
            search_dork=dork,
            is_resolved=False
        )
        db_session.add(chk)

    db_session.commit()
    return project
