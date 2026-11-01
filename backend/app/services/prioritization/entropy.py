import math
import uuid
from typing import List, Dict, Any, Optional
from app.models.project import RequirementNode, ExtractedClaim, ConflictRecord, TemporalAudit
from app.core.config import settings

class EpistemicScorer:
    """
    Computes Shannon Entropy of evidence states and calculates the 0-100 Priority Risk Score.
    """
    K_STATES = 4  # 1: Valid Support, 2: Contradiction, 3: Stale, 4: Unverified/Ungrounded

    @classmethod
    def calculate_normalized_entropy(cls, state_counts: Dict[str, int]) -> float:
        total = sum(state_counts.values())
        if total <= 1:
            return 0.0

        entropy = 0.0
        for count in state_counts.values():
            if count > 0:
                p = count / total
                entropy -= p * math.log2(p)

        max_entropy = math.log2(cls.K_STATES)
        return min(1.0, max(0.0, entropy / max_entropy))

    @classmethod
    def score_requirement(
        cls,
        req: RequirementNode,
        mapped_claims: List[ExtractedClaim],
        conflicts: List[ConflictRecord],
        temporal_audits: List[TemporalAudit]
    ) -> Dict[str, Any]:
        """
        Calculates normalized entropy, priority score, and determines epistemic status.
        """
        n_claims = len(mapped_claims)
        is_dark_spot = (n_claims == 0 and req.mandatory)
        has_conflict = any(c.status in ("confirmed", "requires_review") for c in conflicts)
        
        # Check if mapped claims are associated with stale sources
        stale_source_ids = {
            t.source_id for t in temporal_audits 
            if t.temporal_status in ("potentially_outdated", "outdated")
        }
        has_temporal_issue = any(c.source_id in stale_source_ids for c in mapped_claims)

        # 1. Evidence state classification
        state_counts = {
            "support": 0,
            "contradiction": 0,
            "stale": 0,
            "unverified": 0
        }

        if n_claims == 0:
            # Dark spot condition: Maximum missingness uncertainty
            norm_entropy = 1.0
            u_missing = 1.0
            status = "dark_spot"
        else:
            u_missing = 0.0
            for claim in mapped_claims:
                if not claim.is_grounded or claim.confidence < 0.5:
                    state_counts["unverified"] += 1
                elif claim.source_id in stale_source_ids:
                    state_counts["stale"] += 1
                elif has_conflict:
                    state_counts["contradiction"] += 1
                else:
                    state_counts["support"] += 1

            norm_entropy = cls.calculate_normalized_entropy(state_counts)

            # Determine overall epistemic status
            if has_conflict:
                status = "conflict"
            elif has_temporal_issue:
                status = "stale"
            elif all(c.is_grounded and c.confidence >= 0.7 for c in mapped_claims):
                status = "verified"
            else:
                status = "review_required"

        # 2. Priority Risk Score calculation (0 - 100)
        # Weights: importance (35%), missingness (30%), contradiction (20%), temporal (15%)
        # plus entropy scaling
        importance_norm = req.importance / 5.0  # 0.2 to 1.0
        
        score_parts = {
            "importance": importance_norm * 35.0,
            "missingness": u_missing * 30.0,
            "contradiction": (20.0 if has_conflict else 0.0),
            "temporal": (15.0 if has_temporal_issue else 0.0),
            "entropy_boost": (norm_entropy * 10.0 if n_claims > 0 else 0.0)
        }

        raw_score = sum(score_parts.values())
        final_score = round(min(100.0, max(0.0, raw_score)), 1)

        # 3. Categorization
        if final_score >= 75.0:
            risk_category = "Critical"
        elif final_score >= 55.0:
            risk_category = "High"
        elif final_score >= 35.0:
            risk_category = "Medium"
        else:
            risk_category = "Low"

        # 4. Reason formulation
        reasons = []
        if is_dark_spot:
            reasons.append(f"Mandatory requirement with ZERO mapped claims ({req.name}). High epistemic omission risk.")
        if has_conflict:
            reasons.append(f"Material contradiction detected across sources for '{req.name}'.")
        if has_temporal_issue:
            reasons.append(f"Evidence relies on sources flagged as outdated or prior-cycle for '{req.name}'.")
        if not reasons:
            if status == "verified":
                reasons.append(f"Grounded evidence corroborated across sources with no detected conflicts.")
            else:
                reasons.append(f"Evidence present with moderate uncertainty.")

        return {
            "requirement_id": req.id,
            "requirement_name": req.name,
            "status": status,
            "is_dark_spot": is_dark_spot,
            "has_conflict": has_conflict,
            "has_temporal_issue": has_temporal_issue,
            "mapped_claims_count": n_claims,
            "entropy": round(norm_entropy, 3),
            "priority_score": final_score,
            "risk_category": risk_category,
            "reason": " ".join(reasons),
            "importance": req.importance,
            "mandatory": req.mandatory
        }

