import hashlib
import re
from urllib.parse import urlparse
from typing import Dict, Any, Optional, Tuple
from bs4 import BeautifulSoup
import httpx
from app.core.config import settings
from app.core.security import validate_url_for_ssrf

class IngestionError(Exception):
    pass

def compute_sha256(text: str) -> str:
    return hashlib.sha256(text.encode("utf-8")).hexdigest()

def extract_meta_date(soup: BeautifulSoup) -> Optional[str]:
    # Look for common schema.org and OpenGraph publication date tags
    date_attrs = [
        {"name": "article:published_time"},
        {"property": "article:published_time"},
        {"name": "article:modified_time"},
        {"property": "article:modified_time"},
        {"name": "pubdate"},
        {"name": "date"},
        {"property": "og:published_time"},
        {"itemprop": "datePublished"},
        {"itemprop": "dateModified"}
    ]
    for attr in date_attrs:
        meta = soup.find("meta", attrs=attr)
        if meta and meta.get("content"):
            content = meta.get("content", "").strip()
            # Extract basic ISO date YYYY-MM-DD
            m = re.search(r"\b(\d{4}-\d{2}-\d{2})\b", content)
            if m:
                return m.group(1)
            return content[:19]
    return None

def clean_html_content(html: str) -> Tuple[str, str, Optional[str]]:
    """
    Strips scripts, styling, ads, navigation and returns (title, normalized_text, pub_date)
    """
    soup = BeautifulSoup(html, "html.parser")

    # Extract title
    title = "Untitled Source"
    if soup.title and soup.title.string:
        title = soup.title.string.strip()

    # Try meta date
    pub_date = extract_meta_date(soup)

    # Decompose non-content elements
    for tag in soup(["script", "style", "nav", "footer", "header", "aside", "noscript", "svg", "form", "iframe"]):
        tag.decompose()

    # Prioritize main or article if present
    main_elem = soup.find("main") or soup.find("article") or soup.body or soup
    
    # Get text with clean paragraph spacing
    lines = []
    for element in main_elem.find_all(["p", "h1", "h2", "h3", "h4", "li", "tr"]):
        text = element.get_text(" ", strip=True)
        if text and len(text) > 3:
            lines.append(text)
    
    if not lines:
        raw = soup.get_text("\n", strip=True)
        lines = [line.strip() for line in raw.split("\n") if len(line.strip()) > 3]

    normalized_text = "\n\n".join(lines)
    return title, normalized_text, pub_date

async def fetch_and_clean_url(url: str) -> Dict[str, Any]:
    url = url.strip()
    parsed = urlparse(url)
    domain = parsed.netloc or "unknown-domain"

    # SSRF Check
    is_safe, reason = validate_url_for_ssrf(url)
    if not is_safe:
        return {
            "url": url,
            "domain": domain,
            "title": "Blocked URL",
            "raw_text": "",
            "content_hash": "",
            "published_date": None,
            "status": "failed",
            "error_message": f"Security violation: {reason}"
        }

    try:
        async with httpx.AsyncClient(
            timeout=settings.HTTP_TIMEOUT_SECONDS,
            follow_redirects=True,
            max_redirects=settings.MAX_REDIRECTS,
            headers={"User-Agent": settings.USER_AGENT}
        ) as client:
            resp = await client.get(url)
            
            # Recheck final URL after redirects for SSRF
            final_safe, final_reason = validate_url_for_ssrf(str(resp.url))
            if not final_safe:
                return {
                    "url": url,
                    "domain": domain,
                    "title": "Redirect Blocked",
                    "raw_text": "",
                    "content_hash": "",
                    "published_date": None,
                    "status": "failed",
                    "error_message": f"Redirect blocked: {final_reason}"
                }

            if resp.status_code >= 400:
                return {
                    "url": url,
                    "domain": domain,
                    "title": f"HTTP {resp.status_code}",
                    "raw_text": "",
                    "content_hash": "",
                    "published_date": None,
                    "status": "failed",
                    "error_message": f"HTTP Error {resp.status_code}: {resp.reason_phrase}"
                }

            content_type = resp.headers.get("content-type", "").lower()
            if "text" not in content_type and "json" not in content_type and "xml" not in content_type:
                return {
                    "url": url,
                    "domain": domain,
                    "title": "Unsupported Media",
                    "raw_text": "",
                    "content_hash": "",
                    "published_date": None,
                    "status": "failed",
                    "error_message": f"Unsupported Content-Type: {content_type}"
                }

            if len(resp.content) > settings.MAX_RESPONSE_SIZE_BYTES:
                return {
                    "url": url,
                    "domain": domain,
                    "title": "Oversized Page",
                    "raw_text": "",
                    "content_hash": "",
                    "published_date": None,
                    "status": "failed",
                    "error_message": f"Response exceeds size limit ({len(resp.content)} > {settings.MAX_RESPONSE_SIZE_BYTES} bytes)"
                }

            title, cleaned_text, pub_date = clean_html_content(resp.text)
            if not cleaned_text:
                return {
                    "url": url,
                    "domain": domain,
                    "title": title or "Empty Page",
                    "raw_text": "",
                    "content_hash": "",
                    "published_date": pub_date,
                    "status": "failed",
                    "error_message": "No readable textual content could be extracted."
                }

            content_hash = compute_sha256(cleaned_text)
            return {
                "url": url,
                "domain": domain,
                "title": title,
                "raw_text": cleaned_text,
                "content_hash": content_hash,
                "published_date": pub_date,
                "status": "ingested",
                "error_message": None
            }

    except httpx.TimeoutException:
        return {
            "url": url,
            "domain": domain,
            "title": "Timeout",
            "raw_text": "",
            "content_hash": "",
            "published_date": None,
            "status": "failed",
            "error_message": f"Connection timed out after {settings.HTTP_TIMEOUT_SECONDS}s."
        }
    except Exception as e:
        return {
            "url": url,
            "domain": domain,
            "title": "Ingestion Failed",
            "raw_text": "",
            "content_hash": "",
            "published_date": None,
            "status": "failed",
            "error_message": f"Fetch error: {str(e)}"
        }

def process_manual_text(title: str, text: str, url: str = "manual://user-input", published_date: Optional[str] = None) -> Dict[str, Any]:
    cleaned = text.strip()
    return {
        "url": url,
        "domain": "manual-input",
        "title": title,
        "raw_text": cleaned,
        "content_hash": compute_sha256(cleaned),
        "published_date": published_date,
        "status": "ingested",
        "error_message": None
    }

