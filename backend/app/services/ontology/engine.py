import uuid
import re
from typing import List, Dict, Any, Optional
from app.models.project import RequirementNode
from app.schemas.project import RequirementNodeCreate

# Comprehensive domain templates ensuring deterministic, high quality schemas
DOMAIN_TEMPLATES: Dict[str, List[Dict[str, Any]]] = {
    "scholarship": [
        {
            "key": "eligibility",
            "name": "Applicant Eligibility Criteria",
            "description": "Who qualifies to apply (citizenship, domicile, age limits, academic qualifications, category)?",
            "mandatory": True,
            "importance": 5
        },
        {
            "key": "income_threshold",
            "name": "Family Income Threshold",
            "description": "What is the maximum permitted annual gross family income limit?",
            "mandatory": True,
            "importance": 5
        },
        {
            "key": "scholarship_amount",
            "name": "Scholarship Amount & Benefits",
            "description": "What is the total financial benefit, tuition fee waiver, maintenance allowance, or disbursement frequency?",
            "mandatory": True,
            "importance": 4
        },
        {
            "key": "required_documents",
            "name": "Mandatory Submission Documents",
            "description": "Which documents must applicants submit (income certificate, marksheets, caste certificate, bank details)?",
            "mandatory": True,
            "importance": 5
        },
        {
            "key": "application_deadline",
            "name": "Application Window & Deadline",
            "description": "When does the application open and close for the applicable academic year?",
            "mandatory": True,
            "importance": 5
        },
        {
            "key": "renewal_policy",
            "name": "Renewal Policy & Continuation Rules",
            "description": "What are the continuation or renewal conditions (minimum CGPA, annual re-verification, attendance)?",
            "mandatory": True,
            "importance": 4
        },
        {
            "key": "official_portal",
            "name": "Official Application Portal & Mode",
            "description": "Where must applications be submitted (official URL, nodal officer, physical submission)?",
            "mandatory": True,
            "importance": 4
        }
    ],
    "visa": [
        {
            "key": "eligibility",
            "name": "Visa Eligibility Criteria",
            "description": "Primary qualification, passport validity, nationality restrictions, and travel purpose.",
            "mandatory": True,
            "importance": 5
        },
        {
            "key": "financial_proof",
            "name": "Financial Capacity & Bank Statement",
            "description": "Minimum bank balance, sponsorship declaration, and proof of funds required.",
            "mandatory": True,
            "importance": 5
        },
        {
            "key": "processing_time",
            "name": "Processing Time & Fee",
            "description": "Government fee, consular processing time, and expedited options.",
            "mandatory": True,
            "importance": 4
        },
        {
            "key": "required_documents",
            "name": "Required Documents & Biometrics",
            "description": "Invitation letter, health insurance, criminal background check, biometrics appointment.",
            "mandatory": True,
            "importance": 5
        },
        {
            "key": "duration_and_entry",
            "name": "Duration of Stay & Entry Conditions",
            "description": "Validity period, single or multiple entry, and conditions of stay.",
            "mandatory": True,
            "importance": 4
        }
    ],
    "procurement": [
        {
            "key": "technical_eligibility",
            "name": "Technical Qualification Criteria",
            "description": "Minimum years in business, prior contract execution, and certifications required.",
            "mandatory": True,
            "importance": 5
        },
        {
            "key": "financial_turnover",
            "name": "Annual Financial Turnover Requirement",
            "description": "Minimum average annual turnover for the past 3 fiscal years.",
            "mandatory": True,
            "importance": 5
        },
        {
            "key": "emd_and_security",
            "name": "Earnest Money Deposit (EMD) & Performance Guarantee",
            "description": "EMD amount, exemption for MSME/startups, and performance bank guarantee percentage.",
            "mandatory": True,
            "importance": 4
        },
        {
            "key": "bid_submission_deadline",
            "name": "Bid Submission Closing Date & Time",
            "description": "Exact deadline for electronic or physical bid submission.",
            "mandatory": True,
            "importance": 5
        },
        {
            "key": "evaluation_method",
            "name": "Evaluation & Scoring Methodology",
            "description": "QCBS or L1 criteria, technical weightage, and scoring matrix.",
            "mandatory": True,
            "importance": 4
        }
    ],
    "admissions": [
        {
            "key": "academic_prerequisites",
            "name": "Academic Prerequisites & Minimum Marks",
            "description": "Qualifying degree, percentage or grade thresholds, and subject requirements.",
            "mandatory": True,
            "importance": 5
        },
        {
            "key": "entrance_exam",
            "name": "Entrance Exam or Standardized Test Scores",
            "description": "Accepted exams, minimum cutoffs, and percentile thresholds.",
            "mandatory": True,
            "importance": 5
        },
        {
            "key": "application_fee_deadline",
            "name": "Application Fee & Deadline",
            "description": "Submission cut-off date and non-refundable application fee.",
            "mandatory": True,
            "importance": 4
        },
        {
            "key": "selection_process",
            "name": "Interview & Selection Stages",
            "description": "Group discussions, personal interviews, or portfolio evaluations.",
            "mandatory": True,
            "importance": 4
        }
    ]
}

def detect_domain(objective: str, user_domain: Optional[str] = None) -> str:
    if user_domain and user_domain.lower() in DOMAIN_TEMPLATES:
        return user_domain.lower()
    
    text = objective.lower()
    if any(k in text for k in ["scholarship", "stipend", "fellowship", "financial aid", "bursary", "grant"]):
        return "scholarship"
    elif any(k in text for k in ["visa", "immigration", "permit", "consulate", "passport", "entry clearance"]):
        return "visa"
    elif any(k in text for k in ["procurement", "tender", "bid", "contract", "rfp", "vendor", "emds"]):
        return "procurement"
    elif any(k in text for k in ["admission", "university", "college", "degree", "course", "entrance"]):
        return "admissions"
    
    return "general"

def generate_counterfactual_ontology(objective: str, user_domain: Optional[str] = None) -> List[RequirementNodeCreate]:
    """
    CRITICAL: Generates decision requirement graph BEFORE scraping/fetching any sources.
    Uses domain knowledge templates or synthesizes counterfactual criteria based on objective semantics.
    """
    domain = detect_domain(objective, user_domain)
    if domain in DOMAIN_TEMPLATES:
        nodes = []
        for item in DOMAIN_TEMPLATES[domain]:
            nodes.append(RequirementNodeCreate(
                key=item["key"],
                name=item["name"],
                description=item["description"],
                mandatory=item["mandatory"],
                importance=item["importance"]
            ))
        return nodes
    
    # Generic schema derived from goal analysis
    return [
        RequirementNodeCreate(
            key="primary_eligibility",
            name="Primary Eligibility Criteria",
            description=f"Who qualifies or is subject to '{objective}'?",
            mandatory=True,
            importance=5
        ),
        RequirementNodeCreate(
            key="mandatory_prerequisites",
            name="Mandatory Prerequisites & Conditions",
            description="What baseline prerequisites, financial thresholds, or certifications are required?",
            mandatory=True,
            importance=5
        ),
        RequirementNodeCreate(
            key="documentation",
            name="Required Documentation & Evidence",
            description="What official documents, filings, or proofs must be presented?",
            mandatory=True,
            importance=5
        ),
        RequirementNodeCreate(
            key="deadlines_and_timeline",
            name="Deadlines, Validity & Application Window",
            description="What is the active application window, submission deadline, or expiration date?",
            mandatory=True,
            importance=5
        ),
        RequirementNodeCreate(
            key="governing_authority",
            name="Official Portal & Governing Authority",
            description="What official entity, portal, or contact handles this process?",
            mandatory=True,
            importance=4
        ),
        RequirementNodeCreate(
            key="exceptions_and_penalties",
            name="Exemptions, Disqualifications & Appeals",
            description="What causes disqualification, forfeiture, or non-compliance?",
            mandatory=False,
            importance=3
        )
    ]

