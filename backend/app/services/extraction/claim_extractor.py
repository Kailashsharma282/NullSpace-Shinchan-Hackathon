import re
import uuid
from typing import List, Dict, Any, Optional, Tuple

class ClaimExtractor:
    @staticmethod
    def verify_and_ground_quote(raw_text: str, exact_quote: str, char_start: Optional[int] = None, char_end: Optional[int] = None) -> Tuple[bool, int, int]:
        """
        Verifies whether exact_quote matches raw_text[char_start:char_end].
        If not provided or mismatched, performs a deterministic search to find the exact offset.
        """
        quote_clean = exact_quote.strip()
        if not quote_clean:
            return False, -1, -1

        # Check existing offsets if provided
        if char_start is not None and char_end is not None and 0 <= char_start < char_end <= len(raw_text):
            if raw_text[char_start:char_end] == exact_quote or raw_text[char_start:char_end].strip() == quote_clean:
                return True, char_start, char_end

        # Deterministic substring search
        idx = raw_text.find(exact_quote)
        if idx != -1:
            return True, idx, idx + len(exact_quote)

        # Fallback: search ignoring subtle whitespace differences
        idx = raw_text.find(quote_clean)
        if idx != -1:
            return True, idx, idx + len(quote_clean)

        # Case-insensitive search fallback
        lower_raw = raw_text.lower()
        lower_quote = quote_clean.lower()
        idx = lower_raw.find(lower_quote)
        if idx != -1:
            # Found exact case-insensitive span
            actual_span = raw_text[idx:idx + len(quote_clean)]
            return True, idx, idx + len(quote_clean)

        return False, -1, -1

    @classmethod
    def extract_deterministic_claims(cls, source_id: str, raw_text: str, research_id: str) -> List[Dict[str, Any]]:
        """
        Extracts salient atomic sentences/clauses from the source text and grounds them.
        Uses linguistic markers for:
        - Income / Financial thresholds (lakh, $, €, INR, Rs., income, threshold, salary, fee)
        - Deadlines & Dates (deadline, December, Jan, 2024, 2025, 2026, closing, window)
        - Eligibility (eligible, qualification, domicile, citizen, cgpa, percentage, marks)
        - Documentation (certificate, mark sheet, marksheet, passport, ration card, affidavit, statement)
        - Renewal & Continuation (renewal, renew, year, semester, attendance)
        - Portal / Mode (portal, online, submit, portal.gov, apply)
        """
        claims = []
        # Split into sentences while tracking offsets
        # Use regex to find sentences with their start positions
        sentence_regex = re.compile(r'([A-Z0-9][^.!?\n\r]+[.!?])', re.MULTILINE)
        
        # High value pattern detectors
        patterns = [
            re.compile(r'(?:income|annual|salary|family)\s+(?:must\s+not\s+exceed|under|up\s+to|below|limit|threshold|is)\s+[^.!?\n]+', re.IGNORECASE),
            re.compile(r'(?:deadline|last\s+date|closing\s+date|applications\s+close)\s+(?:is|by|on)?\s+[^.!?\n]+', re.IGNORECASE),
            re.compile(r'(?:required\s+documents?|must\s+submit|mandatory\s+documents?|enclose)\s+[^.!?\n]+', re.IGNORECASE),
            re.compile(r'(?:eligibility|eligible|who\s+can\s+apply|qualification)\s+[^.!?\n]+', re.IGNORECASE),
            re.compile(r'(?:renewal|continuation|renewed\s+annually|re-apply)\s+[^.!?\n]+', re.IGNORECASE),
            re.compile(r'(?:portal|website|apply\s+online\s+at|official\s+link)\s+[^.!?\n]+', re.IGNORECASE),
            re.compile(r'(?:amount|benefit|stipend|tuition\s+fee|allowance)\s+[^.!?\n]+', re.IGNORECASE),
        ]

        found_spans = set()

        for match in sentence_regex.finditer(raw_text):
            sentence = match.group(1).strip()
            start = match.start(1)
            end = match.end(1)

            # Check if sentence matches any important knowledge pattern
            is_relevant = False
            for pat in patterns:
                if pat.search(sentence):
                    is_relevant = True
                    break

            # Also catch sentences with currency / numbers and relevant keywords
            if not is_relevant:
                has_num = bool(re.search(r'\d+', sentence))
                has_kw = bool(re.search(r'\b(income|lakh|crore|percent|cgpa|deadline|renew|portal|documents?|marksheet)\b', sentence, re.IGNORECASE))
                if has_num and has_kw:
                    is_relevant = True

            if is_relevant:
                # Avoid overlapping spans
                if any(start >= s and end <= e for s, e in found_spans):
                    continue

                is_grounded, g_start, g_end = cls.verify_and_ground_quote(raw_text, sentence, start, end)
                if is_grounded:
                    found_spans.add((g_start, g_end))
                    claims.append({
                        "id": f"claim_{uuid.uuid4().hex[:10]}",
                        "research_id": research_id,
                        "source_id": source_id,
                        "claim_text": sentence,
                        "exact_quote": raw_text[g_start:g_end],
                        "char_start": g_start,
                        "char_end": g_end,
                        "is_grounded": True,
                        "confidence": 0.95,
                        "extraction_method": "deterministic"
                    })

        return claims

