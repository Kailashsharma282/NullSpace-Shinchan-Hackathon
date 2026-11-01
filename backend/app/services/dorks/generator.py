import urllib.parse
from typing import Dict, Any, List, Optional

class DorkGenerator:
    @staticmethod
    def generate_dork_for_dark_spot(
        req_name: str, 
        req_key: str, 
        project_title: str, 
        domain: str,
        year: int = 2026
    ) -> Dict[str, Any]:
        """
        Generates targeted search dork for unmapped / dark spot requirement.
        """
        clean_title = project_title.replace("Find all requirements for", "").strip()
        
        # Domain specific official sites
        domain_site = "site:gov.in" if "scholarship" in domain.lower() or "scheme" in domain.lower() else "filetype:pdf"

        # Construct high-intent search query
        query = f'{domain_site} "{clean_title}" "{req_name}" {year}'
        encoded_query = urllib.parse.quote_plus(query)
        search_url = f"https://www.google.com/search?q={encoded_query}"
        
        rationale = f"Targets official government or authoritative PDF documents specifically addressing the omitted '{req_name}' requirement for {year}."

        return {
            "query": query,
            "search_url": search_url,
            "rationale": rationale,
            "category": "dark_spot_resolution"
        }

    @staticmethod
    def generate_dork_for_conflict(
        req_name: str, 
        claim_a_text: str, 
        claim_b_text: str, 
        project_title: str,
        year: int = 2026
    ) -> Dict[str, Any]:
        """
        Generates targeted search dork to arbitrate a detected factual contradiction.
        """
        clean_title = project_title.replace("Find all requirements for", "").strip()
        query = f'"{clean_title}" official guidelines OR notification "{req_name}" {year} filetype:pdf'
        encoded_query = urllib.parse.quote_plus(query)
        search_url = f"https://www.google.com/search?q={encoded_query}"

        rationale = f"Retrieves primary official notification PDF to resolve conflicting claims regarding '{req_name}'."

        return {
            "query": query,
            "search_url": search_url,
            "rationale": rationale,
            "category": "conflict_arbitration"
        }

