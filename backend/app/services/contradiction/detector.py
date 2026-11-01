import re
import uuid
from typing import List, Dict, Any, Tuple
from app.models.project import ExtractedClaim, RequirementNode

class ContradictionDetector:
    @staticmethod
    def extract_numbers_and_currency(text: str) -> List[Tuple[str, float]]:
        """
        Extracts monetary and numerical values for comparison.
        E.g., "Rs. 3 lakh" -> 300000, "4 lakh" -> 400000, "Rs 2,00,000" -> 200000, "50%" -> 50
        """
        results = []
        text_lower = text.lower()
        
        # Pattern for lakh/crore
        lakh_matches = re.finditer(r'(?:rs\.?|inr)?\s*([0-9]+(?:\.[0-9]+)?)\s*(?:lakh|lac)', text_lower)
        for m in lakh_matches:
            val = float(m.group(1)) * 100000
            results.append((m.group(0).strip(), val))

        # Standard numbers with commas: e.g. 3,00,000 or 50,000
        comma_matches = re.finditer(r'(?:rs\.?|inr)?\s*([0-9]{1,3}(?:,[0-9]{2,3})+)', text_lower)
        for m in comma_matches:
            clean_str = m.group(1).replace(",", "")
            results.append((m.group(0).strip(), float(clean_str)))

        # Plain numbers with Rs
        rs_matches = re.finditer(r'(?:rs\.?|inr)\s*([0-9]+(?:\.[0-9]+)?)', text_lower)
        for m in rs_matches:
            raw_str = m.group(0).strip()
            # If not already captured in lakh
            if not any(raw_str in r[0] for r in results):
                results.append((raw_str, float(m.group(1))))

        return results

    @classmethod
    def evaluate_claim_pair(cls, claim_a: ExtractedClaim, claim_b: ExtractedClaim, req_name: str) -> Tuple[str, float, str]:
        text_a = claim_a.claim_text.lower()
        text_b = claim_b.claim_text.lower()

        # 1. Check numeric / threshold contradiction
        nums_a = cls.extract_numbers_and_currency(text_a)
        nums_b = cls.extract_numbers_and_currency(text_b)

        if nums_a and nums_b:
            # Compare extracted numeric values
            vals_a = [v[1] for v in nums_a]
            vals_b = [v[1] for v in nums_b]
            if set(vals_a) != set(vals_b):
                repr_a = ", ".join([v[0] for v in nums_a])
                repr_b = ", ".join([v[0] for v in nums_b])
                return (
                    "contradiction",
                    0.96,
                    f"Direct numeric conflict on '{req_name}': Claim A states ({repr_a}) while Claim B states ({repr_b})."
                )
            else:
                return (
                    "agreement",
                    0.90,
                    f"Consistent numeric threshold on '{req_name}': both sources specify identical values ({nums_a[0][0]})."
                )

        # 2. Check policy negation contradiction (e.g. renewal required vs not required)
        negation_terms = ["not required", "no renewal", "exempt", "never required", "without renewal", "optional"]
        affirmation_terms = ["annual renewal", "must renew", "renewal required", "mandatory renewal", "re-apply annually"]

        a_has_neg = any(term in text_a for term in negation_terms)
        b_has_neg = any(term in text_b for term in negation_terms)
        a_has_aff = any(term in text_a for term in affirmation_terms)
        b_has_aff = any(term in text_b for term in affirmation_terms)

        if (a_has_neg and b_has_aff) or (b_has_neg and a_has_aff):
            return (
                "contradiction",
                0.94,
                f"Direct policy opposition on '{req_name}': one source asserts renewal/condition is mandatory, while another asserts it is not required."
            )

        # 3. Check document requirement conflicts (e.g. marksheet vs bank statement)
        docs_a = set(re.findall(r'\b(marksheet|mark sheet|bank statement|income certificate|ration card|aadhaar|affidavit|caste certificate)\b', text_a))
        docs_b = set(re.findall(r'\b(marksheet|mark sheet|bank statement|income certificate|ration card|aadhaar|affidavit|caste certificate)\b', text_b))

        if docs_a and docs_b:
            if docs_a == docs_b:
                return (
                    "agreement",
                    0.88,
                    f"Document lists corroborate on '{req_name}': both specify {', '.join(docs_a)}."
                )
            elif not docs_a.intersection(docs_b):
                return (
                    "contradiction",
                    0.85,
                    f"Incompatible documentation requirements on '{req_name}': Claim A mandates ({', '.join(docs_a)}) whereas Claim B mandates ({', '.join(docs_b)})."
                )
            else:
                diff_a = docs_a - docs_b
                diff_b = docs_b - docs_a
                return (
                    "contradiction",
                    0.78,
                    f"Discrepancy in required documentation on '{req_name}': Claim A adds [{', '.join(diff_a) or 'none'}], Claim B adds [{', '.join(diff_b) or 'none'}]."
                )

        # 4. Default: Semantic overlap without direct conflict
        return (
            "neutral",
            0.60,
            f"Sources discuss distinct facets of '{req_name}' without evident factual opposition."
        )

    @classmethod
    def detect_conflicts_for_research(
        cls, 
        claims_by_req: Dict[str, List[ExtractedClaim]], 
        requirements_map: Dict[str, RequirementNode],
        research_id: str
    ) -> List[Dict[str, Any]]:
        """
        Executes pairwise claim comparison across all claims mapped to the same requirement.
        """
        conflicts = []
        for req_id, claims in claims_by_req.items():
            req = requirements_map.get(req_id)
            req_name = req.name if req else req_id

            # Pairwise compare claims from different sources
            n = len(claims)
            for i in range(n):
                for j in range(i + 1, n):
                    claim_a = claims[i]
                    claim_b = claims[j]

                    # Only compare claims from distinct sources or materially distinct texts
                    if claim_a.source_id == claim_b.source_id and claim_a.claim_text == claim_b.claim_text:
                        continue

                    rel_type, conf, explanation = cls.evaluate_claim_pair(claim_a, claim_b, req_name)

                    if rel_type in ("contradiction", "uncertain"):
                        conflicts.append({
                            "id": f"conflict_{uuid.uuid4().hex[:10]}",
                            "research_id": research_id,
                            "requirement_id": req_id,
                            "claim_a_id": claim_a.id,
                            "claim_b_id": claim_b.id,
                            "relationship_type": rel_type,
                            "confidence": conf,
                            "explanation": explanation,
                            "status": "requires_review" if rel_type == "uncertain" else "confirmed",
                            "user_notes": None
                        })

        return conflicts

