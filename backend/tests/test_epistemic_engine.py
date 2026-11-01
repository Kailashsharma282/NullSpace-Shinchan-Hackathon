import pytest
from app.services.ontology.engine import generate_counterfactual_ontology, detect_domain
from app.core.security import validate_url_for_ssrf
from app.services.ingestion.fetcher import clean_html_content, process_manual_text
from app.services.extraction.claim_extractor import ClaimExtractor
from app.services.alignment.matcher import AlignmentEngine
from app.services.contradiction.detector import ContradictionDetector
from app.services.temporal.auditor import TemporalAuditor
from app.services.prioritization.entropy import EpistemicScorer
from app.services.dorks.generator import DorkGenerator
from app.models.project import RequirementNode, ExtractedClaim, ConflictRecord, TemporalAudit

def test_01_requirement_generation():
    nodes = generate_counterfactual_ontology("Find all requirements for applying for a government scholarship")
    assert len(nodes) >= 5
    keys = [n.key for n in nodes]
    assert "income_threshold" in keys
    assert "eligibility" in keys
    assert "renewal_policy" in keys

def test_02_requirement_graph_validation():
    nodes = generate_counterfactual_ontology("Requirements for Student Visa")
    for n in nodes:
        assert n.name
        assert n.description
        assert 1 <= n.importance <= 5
        assert isinstance(n.mandatory, bool)

def test_03_ssrf_url_validation():
    # Block loopback
    safe, msg = validate_url_for_ssrf("http://127.0.0.1:8000/secret")
    assert not safe
    # Block internal metadata
    safe, msg = validate_url_for_ssrf("http://169.254.169.254/latest/meta-data")
    assert not safe
    # Block unsupported scheme
    safe, msg = validate_url_for_ssrf("file:///etc/passwd")
    assert not safe
    # Valid external URL
    safe, msg = validate_url_for_ssrf("https://www.google.com")
    assert safe

def test_04_html_text_extraction():
    html = """
    <html>
      <head><title>Test Scholarship Notice</title></head>
      <body>
        <nav><a href="/">Home</a></nav>
        <main>
          <h1>Scholarship Guidelines</h1>
          <p>Annual gross family income must not exceed Rs. 3,00,000.</p>
        </main>
        <script>console.log("bad");</script>
      </body>
    </html>
    """
    title, text, pub = clean_html_content(html)
    assert title == "Test Scholarship Notice"
    assert "Annual gross family income must not exceed Rs. 3,00,000." in text
    assert "console.log" not in text

def test_05_claim_grounding_and_exact_offsets():
    raw_text = "Announcement: Annual gross family income must not exceed Rs. 3,00,000 from all sources."
    quote = "Annual gross family income must not exceed Rs. 3,00,000 from all sources."
    is_grounded, start, end = ClaimExtractor.verify_and_ground_quote(raw_text, quote)
    assert is_grounded
    assert raw_text[start:end] == quote
    assert start == 14
    assert end == 14 + len(quote)

def test_06_claim_grounding_mismatch_rejection():
    raw_text = "Only students with family income under 3 lakh are eligible."
    invented_quote = "Paraphrased quote that does not appear in source text."
    is_grounded, start, end = ClaimExtractor.verify_and_ground_quote(raw_text, invented_quote)
    assert not is_grounded
    assert start == -1

def test_07_requirement_to_claim_semantic_mapping():
    req = RequirementNode(
        id="req_income",
        research_id="test_res",
        key="income_threshold",
        name="Family Income Threshold",
        description="What is the maximum permitted annual gross family income?",
        mandatory=True,
        importance=5
    )
    score, explanation = AlignmentEngine.calculate_match_score(
        "Annual gross family income must not exceed Rs. 3,00,000.",
        req
    )
    assert score >= 0.5
    assert "income" in explanation or "Matched" in explanation

def test_08_contradiction_detection_numeric():
    req_name = "Family Income Threshold"
    claim_a = ExtractedClaim(
        id="c1",
        research_id="res1",
        source_id="s1",
        claim_text="Annual family income must not exceed Rs. 3,00,000.",
        exact_quote="Annual family income must not exceed Rs. 3,00,000.",
        char_start=0,
        char_end=40
    )
    claim_b = ExtractedClaim(
        id="c2",
        research_id="res1",
        source_id="s2",
        claim_text="Applicants with family income up to Rs. 4,00,000 are eligible.",
        exact_quote="Applicants with family income up to Rs. 4,00,000 are eligible.",
        char_start=0,
        char_end=50
    )
    rel_type, conf, exp = ContradictionDetector.evaluate_claim_pair(claim_a, claim_b, req_name)
    assert rel_type == "contradiction"
    assert conf >= 0.9
    assert "Direct numeric conflict" in exp

def test_09_contradiction_detection_policy_negation():
    req_name = "Renewal Policy"
    claim_a = ExtractedClaim(
        id="c1",
        research_id="res1",
        source_id="s1",
        claim_text="Students must note that annual renewal is mandatory each year.",
        exact_quote="Students must note that annual renewal is mandatory each year.",
        char_start=0,
        char_end=50
    )
    claim_b = ExtractedClaim(
        id="c2",
        research_id="res1",
        source_id="s2",
        claim_text="Continuation is automatic; subsequent annual renewal is not required.",
        exact_quote="Continuation is automatic; subsequent annual renewal is not required.",
        char_start=0,
        char_end=50
    )
    rel_type, conf, exp = ContradictionDetector.evaluate_claim_pair(claim_a, claim_b, req_name)
    assert rel_type == "contradiction"
    assert "Direct policy opposition" in exp

def test_10_neutral_claim_handling():
    req_name = "Application Deadline"
    claim_a = ExtractedClaim(
        id="c1",
        research_id="res1",
        source_id="s1",
        claim_text="The application portal opens on 1st November.",
        exact_quote="The application portal opens on 1st November.",
        char_start=0,
        char_end=40
    )
    claim_b = ExtractedClaim(
        id="c2",
        research_id="res1",
        source_id="s2",
        claim_text="Late submissions will be archived by the administrative office.",
        exact_quote="Late submissions will be archived by the administrative office.",
        char_start=0,
        char_end=50
    )
    rel_type, conf, exp = ContradictionDetector.evaluate_claim_pair(claim_a, claim_b, req_name)
    assert rel_type == "neutral"

def test_11_temporal_auditing():
    text_current = "Notification for Academic Year 2026-27. Deadline 31 December 2026."
    res = TemporalAuditor.audit_source_temporality("src1", text_current, "2026-10-01", "res1", current_year=2026)
    assert res["temporal_status"] == "current"

    text_stale = "Scholarship guidelines for AY 2023-24."
    res_stale = TemporalAuditor.audit_source_temporality("src2", text_stale, "2023-05-01", "res1", current_year=2026)
    assert res_stale["temporal_status"] in ("potentially_outdated", "outdated")

def test_12_entropy_and_dark_spot_calculation():
    req = RequirementNode(
        id="req_renewal",
        research_id="res1",
        key="renewal_policy",
        name="Renewal Policy",
        description="Continuation rules",
        mandatory=True,
        importance=5
    )
    # Zero mapped claims => Dark Spot
    score_res = EpistemicScorer.score_requirement(
        req=req,
        mapped_claims=[],
        conflicts=[],
        temporal_audits=[]
    )
    assert score_res["is_dark_spot"] is True
    assert score_res["status"] == "dark_spot"
    assert score_res["entropy"] == 1.0
    assert score_res["priority_score"] >= 65.0
    assert score_res["risk_category"] in ("Critical", "High")

def test_13_dork_generation():
    dork = DorkGenerator.generate_dork_for_dark_spot("Renewal Policy", "renewal_policy", "Government Scholarship", "scholarship", 2026)
    assert "site:gov.in" in dork["query"]
    assert "Renewal Policy" in dork["query"]
    assert "https://www.google.com/search?q=" in dork["search_url"]

