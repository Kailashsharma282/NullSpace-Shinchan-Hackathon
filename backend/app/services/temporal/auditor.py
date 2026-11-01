import re
import json
import uuid
import datetime
from typing import Dict, Any, List, Optional, Tuple
from app.core.config import settings

class TemporalAuditor:
    # Academic cycle regex: e.g. 2023-24, 2024-2025, 2025-26, 2026-27
    CYCLE_REGEX = re.compile(r'\b(202[0-9])\s*[-/]\s*([0-9]{2,4})\b')
    # Standalone 4-digit years: e.g. 2020 through 2030
    YEAR_REGEX = re.compile(r'\b(202[0-9]|203[0-5])\b')
    # Specific date regex: e.g. 31 December 2026, 15-Aug-2024, 2025-11-01
    DATE_REGEX = re.compile(r'\b(\d{1,2}(?:st|nd|rd|th)?\s+(?:Jan(?:uary)?|Feb(?:ruary)?|Mar(?:ch)?|Apr(?:il)?|May|Jun(?:e)?|Jul(?:y)?|Aug(?:ust)?|Sep(?:tember)?|Oct(?:ober)?|Nov(?:ember)?|Dec(?:ember)?)\s+\d{4})\b', re.IGNORECASE)

    @classmethod
    def audit_source_temporality(
        cls, 
        source_id: str, 
        raw_text: str, 
        published_date: Optional[str], 
        research_id: str,
        current_year: Optional[int] = None
    ) -> Dict[str, Any]:
        ref_year = current_year or settings.CURRENT_REFERENCE_YEAR
        
        # 1. Extract academic cycles
        cycles = []
        for m in cls.CYCLE_REGEX.finditer(raw_text):
            y1 = m.group(1)
            y2 = m.group(2)
            if len(y2) == 2:
                cycle_str = f"{y1}-{y2}"
            else:
                cycle_str = f"{y1}-{y2[-2:]}"
            if cycle_str not in cycles:
                cycles.append(cycle_str)

        # 2. Extract calendar dates & deadlines
        dates = []
        for m in cls.DATE_REGEX.finditer(raw_text):
            d_str = m.group(1).strip()
            if d_str not in dates:
                dates.append(d_str)

        # 3. Extract years
        years = []
        for m in cls.YEAR_REGEX.finditer(raw_text):
            yr = int(m.group(1))
            if yr not in years:
                years.append(yr)
        years.sort()

        # If meta published date exists, extract year from it
        pub_year = None
        if published_date:
            m_pub = re.search(r'\b(202[0-9])\b', published_date)
            if m_pub:
                pub_year = int(m_pub.group(1))
                if pub_year not in years:
                    years.append(pub_year)
                    years.sort()

        # 4. Classify temporal status
        status = "date_unknown"
        reason = "No explicit academic cycle or calendar year detected in source."

        if cycles:
            # Analyze cycle years
            max_cycle_start = max([int(c.split("-")[0]) for c in cycles])
            if max_cycle_start >= ref_year:
                status = "current"
                reason = f"Source targets active application cycle ({', '.join(cycles)})."
            elif max_cycle_start == ref_year - 1:
                status = "potentially_outdated"
                reason = f"Source references previous application cycle ({', '.join(cycles)}); rules may have been revised for {ref_year}."
            else:
                status = "outdated"
                reason = f"Source refers to superseded cycle ({', '.join(cycles)}), older than 1 year prior to current reference {ref_year}."
        elif years:
            max_year = max(years)
            if max_year >= ref_year:
                status = "current"
                reason = f"Source cites current reference year ({max_year})."
            elif max_year == ref_year - 1:
                status = "potentially_outdated"
                reason = f"Source only references year {max_year}; may lack revisions for {ref_year}."
            else:
                status = "outdated"
                reason = f"Source references historical year {max_year} (current reference is {ref_year})."
        elif pub_year:
            if pub_year >= ref_year:
                status = "current"
                reason = f"Publication metadata reflects current period ({pub_year})."
            elif pub_year == ref_year - 1:
                status = "potentially_outdated"
                reason = f"Published in previous year {pub_year}."
            else:
                status = "outdated"
                reason = f"Published in {pub_year}; requires verification against current guidelines."

        return {
            "id": f"temp_{uuid.uuid4().hex[:10]}",
            "research_id": research_id,
            "source_id": source_id,
            "detected_years": json.dumps([str(y) for y in years]),
            "detected_cycles": json.dumps(cycles),
            "calendar_deadlines": json.dumps(dates[:5]),
            "temporal_status": status,
            "staleness_reason": reason
        }

