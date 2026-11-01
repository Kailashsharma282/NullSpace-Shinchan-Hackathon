import re
import uuid
from typing import List, Dict, Any, Tuple
from app.models.project import RequirementNode, ExtractedClaim

# Semantic keyword associations for robust domain mapping
REQUIREMENT_KEYWORD_MAP: Dict[str, List[str]] = {
    "income_threshold": ["income", "annual", "family income", "gross", "lakh", "threshold", "rs.", "inr", "salary", "poverty", "earning"],
    "eligibility": ["eligible", "eligibility", "citizen", "domicile", "qualification", "qualify", "age limit", "residence", "marks", "percentage", "cgpa", "criteria"],
    "required_documents": ["document", "documents", "certificate", "marksheet", "mark sheet", "submission", "submit", "affidavit", "ration card", "aadhaar", "bank statement"],
    "application_deadline": ["deadline", "last date", "closing date", "apply before", "window", "dates", "schedule", "december", "january", "timeline"],
    "renewal_policy": ["renewal", "renew", "continuation", "subsequent years", "maintain", "progress", "renewed annually", "re-apply"],
    "official_portal": ["portal", "website", "apply online", "official link", "url", "gov.in", "nic.in", "mode", "address"],
    "scholarship_amount": ["amount", "benefit", "stipend", "tuition", "allowance", "waiver", "concession", "financial aid", "grant"]
}

class AlignmentEngine:
    @classmethod
    def calculate_match_score(cls, claim_text: str, req: RequirementNode) -> Tuple[float, str]:
        text_lower = claim_text.lower()
        req_key = req.key.lower()
        req_name = req.name.lower()
        req_desc = req.description.lower()

        matched_terms = []
        score = 0.0

        # Check explicit keywords from map if available
        domain_keywords = REQUIREMENT_KEYWORD_MAP.get(req_key, [])
        for kw in domain_keywords:
            if re.search(r'\b' + re.escape(kw) + r'\b', text_lower):
                score += 0.35
                matched_terms.append(kw)

        # Check requirement name tokens
        name_tokens = [t for t in re.findall(r'\w+', req_name) if len(t) > 3 and t not in ("criteria", "policy", "mandatory")]
        for token in name_tokens:
            if token in text_lower:
                score += 0.25
                matched_terms.append(token)

        # Check description tokens
        desc_tokens = [t for t in re.findall(r'\w+', req_desc) if len(t) > 4]
        for token in set(desc_tokens):
            if token in text_lower:
                score += 0.15
                if token not in matched_terms:
                    matched_terms.append(token)

        # Normalize score to max 0.98
        final_confidence = min(0.98, max(0.0, score))
        if final_confidence >= 0.35:
            explanation = f"Matched requirement '{req.name}' via salient indicators: {', '.join(set(matched_terms))[:120]}."
        else:
            explanation = "Insufficient semantic correlation."

        return final_confidence, explanation

    @classmethod
    def align_claims_to_requirements(
        cls, 
        claims: List[ExtractedClaim], 
        requirements: List[RequirementNode], 
        research_id: str
    ) -> List[Dict[str, Any]]:
        """
        Bipartite graph alignment: Maps claims to best-matching requirement nodes.
        """
        mappings = []
        for claim in claims:
            best_req = None
            best_score = 0.0
            best_explanation = ""

            for req in requirements:
                score, explanation = cls.calculate_match_score(claim.claim_text, req)
                if score > best_score:
                    best_score = score
                    best_req = req
                    best_explanation = explanation

            # If confidence passes threshold, create bipartite edge
            if best_req and best_score >= 0.35:
                # Update claim's primary requirement_id
                claim.requirement_id = best_req.id
                mappings.append({
                    "id": f"map_{uuid.uuid4().hex[:10]}",
                    "research_id": research_id,
                    "claim_id": claim.id,
                    "requirement_id": best_req.id,
                    "confidence": round(best_score, 2),
                    "mapping_method": "semantic_heuristic",
                    "explanation": best_explanation
                })

        return mappings

