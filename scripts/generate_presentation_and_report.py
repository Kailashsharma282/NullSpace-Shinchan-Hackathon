import os
import sys
from pptx import Presentation
from pptx.util import Inches, Pt
from pptx.dml.color import RGBColor
from pptx.enum.text import PP_ALIGN
from pptx.enum.shapes import MSO_SHAPE

AUTHOR_NAME = "POCHIRAJU KAILASH RAM MARKANDEYA SHARMA"
AUTHOR_TITLE = "Principal Software Architect & Lead Full-Stack AI Engineer"
PROJECT_NAME = "NullSpace"
TAGLINE = "See What the Sources Don't Say."
SUBTITLE = "AI-Assisted Counterfactual Schema Alignment & Contradiction Detection Engine"

# Color Palette (Modern Dark Research Theme)
BG_COLOR = RGBColor(11, 15, 25)        # #0B0F19 Deep Navy
CARD_BG = RGBColor(22, 31, 48)         # #161F30 Slate Card
CYAN = RGBColor(6, 182, 212)           # #06B6D4 Accent Cyan
INDIGO = RGBColor(99, 102, 241)        # #6366F1 Accent Indigo
WHITE = RGBColor(248, 250, 252)        # Text Primary
MUTED = RGBColor(148, 163, 184)        # Text Muted
EMERALD = RGBColor(16, 185, 129)       # Green Status
ROSE = RGBColor(244, 63, 94)           # Red Status
AMBER = RGBColor(245, 158, 11)         # Yellow Status
BORDER_COLOR = RGBColor(31, 41, 61)    # Border Slate

def apply_background(slide):
    background = slide.background
    fill = background.fill
    fill.solid()
    fill.fore_color.rgb = BG_COLOR

def add_header(slide, title_text, category="NULLSPACE EPISTEMIC ARCHITECTURE"):
    # Category tag
    cat_box = slide.shapes.add_textbox(Inches(0.8), Inches(0.4), Inches(11), Inches(0.35))
    tf_c = cat_box.text_frame
    tf_c.word_wrap = True
    p_c = tf_c.paragraphs[0]
    p_c.text = category.upper()
    p_c.font.size = Pt(10)
    p_c.font.bold = True
    p_c.font.color.rgb = CYAN
    p_c.font.name = "Calibri"

    # Title
    t_box = slide.shapes.add_textbox(Inches(0.8), Inches(0.7), Inches(11.5), Inches(0.8))
    tf_t = t_box.text_frame
    tf_t.word_wrap = True
    p_t = tf_t.paragraphs[0]
    p_t.text = title_text
    p_t.font.size = Pt(22)
    p_t.font.bold = True
    p_t.font.color.rgb = WHITE
    p_t.font.name = "Calibri"

def add_footer(slide, slide_num):
    f_box = slide.shapes.add_textbox(Inches(0.8), Inches(7.0), Inches(11.7), Inches(0.3))
    tf = f_box.text_frame
    p = tf.paragraphs[0]
    p.text = f"NullSpace | Epistemic Audit Platform | Architect: {AUTHOR_NAME} | Slide {slide_num}"
    p.font.size = Pt(8.5)
    p.font.color.rgb = MUTED
    p.font.name = "Calibri"

def create_card(slide, left, top, width, height, title, body_paragraphs, accent_color=CYAN):
    shape = slide.shapes.add_shape(MSO_SHAPE.ROUNDED_RECTANGLE, left, top, width, height)
    shape.fill.solid()
    shape.fill.fore_color.rgb = CARD_BG
    shape.line.color.rgb = BORDER_COLOR
    shape.line.width = Pt(1)

    tf = shape.text_frame
    tf.word_wrap = True
    tf.margin_left = Inches(0.2)
    tf.margin_right = Inches(0.2)
    tf.margin_top = Inches(0.2)
    tf.margin_bottom = Inches(0.2)

    # Title
    p0 = tf.paragraphs[0]
    p0.text = title
    p0.font.bold = True
    p0.font.size = Pt(13)
    p0.font.color.rgb = accent_color
    p0.font.name = "Calibri"

    # Content
    for text in body_paragraphs:
        p = tf.add_paragraph()
        p.text = "• " + text
        p.font.size = Pt(10)
        p.font.color.rgb = WHITE
        p.font.name = "Calibri"
        p.space_before = Pt(4)

def build_presentation():
    prs = Presentation()
    prs.slide_width = Inches(13.333)
    prs.slide_height = Inches(7.5)
    blank_layout = prs.slide_layouts[6]

    base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    screenshots_dir = os.path.join(base_dir, "docs", "screenshots")

    # ==========================================
    # SLIDE 1: Title Slide
    # ==========================================
    s1 = prs.slides.add_slide(blank_layout)
    apply_background(s1)

    # Decorative top bar
    top_bar = s1.shapes.add_shape(MSO_SHAPE.RECTANGLE, Inches(0), Inches(0), Inches(13.333), Inches(0.12))
    top_bar.fill.solid()
    top_bar.fill.fore_color.rgb = CYAN
    top_bar.line.fill.background()

    # Product Title Box
    tbox = s1.shapes.add_textbox(Inches(1.0), Inches(1.5), Inches(11.3), Inches(2.2))
    tf1 = tbox.text_frame
    tf1.word_wrap = True
    
    p_tag = tf1.paragraphs[0]
    p_tag.text = "EPISTEMIC INTELLIGENCE & CONTRADICTION ENGINE"
    p_tag.font.size = Pt(12)
    p_tag.font.bold = True
    p_tag.font.color.rgb = CYAN
    p_tag.font.name = "Calibri"

    p_title = tf1.add_paragraph()
    p_title.text = PROJECT_NAME
    p_title.font.size = Pt(54)
    p_title.font.bold = True
    p_title.font.color.rgb = WHITE
    p_title.font.name = "Calibri"
    p_title.space_before = Pt(8)

    p_sub = tf1.add_paragraph()
    p_sub.text = f'"{TAGLINE}"'
    p_sub.font.size = Pt(20)
    p_sub.font.italic = True
    p_sub.font.color.rgb = INDIGO
    p_sub.font.name = "Calibri"
    p_sub.space_before = Pt(4)

    p_desc = tf1.add_paragraph()
    p_desc.text = SUBTITLE
    p_desc.font.size = Pt(13)
    p_desc.font.color.rgb = MUTED
    p_desc.font.name = "Calibri"
    p_desc.space_before = Pt(6)

    # Author Bio Card
    author_card = s1.shapes.add_shape(MSO_SHAPE.ROUNDED_RECTANGLE, Inches(1.0), Inches(4.3), Inches(11.333), Inches(2.2))
    author_card.fill.solid()
    author_card.fill.fore_color.rgb = CARD_BG
    author_card.line.color.rgb = CYAN
    author_card.line.width = Pt(1.5)

    atf = author_card.text_frame
    atf.margin_left = Inches(0.4)
    atf.margin_top = Inches(0.3)

    ap1 = atf.paragraphs[0]
    ap1.text = "SYSTEM ARCHITECT & LEAD ENGINEER:"
    ap1.font.size = Pt(10)
    ap1.font.bold = True
    ap1.font.color.rgb = CYAN

    ap2 = atf.add_paragraph()
    ap2.text = AUTHOR_NAME
    ap2.font.size = Pt(22)
    ap2.font.bold = True
    ap2.font.color.rgb = WHITE
    ap2.space_before = Pt(4)

    ap3 = atf.add_paragraph()
    ap3.text = f"{AUTHOR_TITLE} | Full-Stack Architecture, Epistemic Graph Models & Security"
    ap3.font.size = Pt(11)
    ap3.font.color.rgb = MUTED
    ap3.space_before = Pt(2)

    ap4 = atf.add_paragraph()
    ap4.text = "Hackathon Submission Edition | 100% Automated Testing & Offline Deterministic Verification"
    ap4.font.size = Pt(9.5)
    ap4.font.bold = True
    ap4.font.color.rgb = EMERALD
    ap4.space_before = Pt(8)

    add_footer(s1, 1)

    # ==========================================
    # SLIDE 2: The Core Problem Statement
    # ==========================================
    s2 = prs.slides.add_slide(blank_layout)
    apply_background(s2)
    add_header(s2, "The Blind Spot Crisis in Retrieval-Augmented AI", "Problem Analysis")

    create_card(s2, Inches(0.8), Inches(1.8), Inches(3.6), Inches(4.8), 
                "1. Confirmation Bias", 
                [
                    "Standard RAG engines query: 'What do these pages say?'",
                    "They silently omit critical criteria that no source mentions.",
                    "If a scholarship notice neglects renewal policy, RAG presents an incomplete decision as verified.",
                    "Users accept grants only to be disqualified in subsequent years."
                ], ROSE)

    create_card(s2, Inches(4.8), Inches(1.8), Inches(3.6), Inches(4.8), 
                "2. Unchecked Contradictions", 
                [
                    "Web sources disagree frequently on high-stakes numeric limits.",
                    "Blog A claims ceiling is Rs. 4 Lakh; Notice says Rs. 3 Lakh; Blog B claims Rs. 2 Lakh.",
                    "LLMs hallucinate a synthetic blend or arbitrarily pick the most recent text.",
                    "No verbatim grounding or side-by-side span diffing."
                ], AMBER)

    create_card(s2, Inches(8.8), Inches(1.8), Inches(3.6), Inches(4.8), 
                "3. Temporal Decay & Omission", 
                [
                    "Web scrapers confuse retrieval timestamp with policy applicability.",
                    "A 2024 blog scraped today is mistaken for current 2026-27 guidance.",
                    "Critical application cycle differences (e.g. AY 2025-26 vs AY 2026-27) go undetected.",
                    "No mathematical uncertainty metric to prioritize verification."
                ], CYAN)

    add_footer(s2, 2)

    # ==========================================
    # SLIDE 3: The Paradigm Shift
    # ==========================================
    s3 = prs.slides.add_slide(blank_layout)
    apply_background(s3)
    add_header(s3, "The Counterfactual Solution: Schema-First Epistemics", "Core Innovation")

    create_card(s3, Inches(0.8), Inches(1.8), Inches(5.6), Inches(4.8), 
                "Traditional Retrieval Workflow (Flawed)", 
                [
                    "Step 1: Scrape/Fetch arbitrary user-provided URLs.",
                    "Step 2: Generate summaries based strictly on retrieved texts.",
                    "Fatal Vulnerability: Severe blind spots. If all sources omit a required document or renewal rule, the user is never alerted.",
                    "Confirmation bias is baked into the discovery architecture.",
                    "Quotes are often synthetic paraphrases invented by the model."
                ], ROSE)

    create_card(s3, Inches(6.8), Inches(1.8), Inches(5.6), Inches(4.8), 
                "NullSpace Counterfactual Workflow (Schema-First)", 
                [
                    "Step 1: Synthesize mandatory Decision Requirement Graph G = (V, E) BEFORE scraping any source.",
                    "Step 2: Ingest sources with SSRF protection and compute SHA-256 snapshots.",
                    "Step 3: Extract atomic claims with verified character offsets [start:end].",
                    "Step 4: Execute bipartite alignment mapping claims to requirement nodes.",
                    "Step 5: Mathematical InDegree(v) = 0 Dark Spot flag for ungrounded mandatory criteria."
                ], EMERALD)

    add_footer(s3, 3)

    # ==========================================
    # SLIDE 4: Mathematical Formulations
    # ==========================================
    s4 = prs.slides.add_slide(blank_layout)
    apply_background(s4)
    add_header(s4, "Mathematical Formulations & Epistemic Metrics", "Algorithmic Rigor")

    create_card(s4, Inches(0.8), Inches(1.8), Inches(5.6), Inches(2.3), 
                "A. Digital Dark Spot Condition", 
                [
                    "For any mandatory decision requirement node v in V_mandatory:",
                    "IsDarkSpot(v) <=> InDegree(v) = 0",
                    "InDegree(v) = |{ c in Claims : mapped(c, v) }|",
                    "Guarantees that unaddressed decision facets are mathematically surfaced."
                ], CYAN)

    create_card(s4, Inches(6.8), Inches(1.8), Inches(5.6), Inches(2.3), 
                "B. Exact Character Offset Grounding", 
                [
                    "Snapshot immutability: ContentHash = SHA256(RawText)",
                    "Offset mathematical invariant: RawText[start : end] == exact_quote",
                    "If a model hallucinates a paraphrase, offset search fails -> claim is rejected from Grounded Evidence Vault."
                ], EMERALD)

    create_card(s4, Inches(0.8), Inches(4.4), Inches(5.6), Inches(2.4), 
                "C. Normalized Shannon Evidence Entropy", 
                [
                    "For requirement v with claims distributed across k=4 epistemic states:",
                    "H(X_v) = - sum(p_i * log2(p_i))",
                    "H_norm(X_v) = H(X_v) / log2(k)",
                    "When InDegree = 0 (Dark Spot): U_missing = 1.0 (maximum uncertainty)."
                ], INDIGO)

    create_card(s4, Inches(6.8), Inches(4.4), Inches(5.6), Inches(2.4), 
                "D. Priority Risk Scoring (0 - 100)", 
                [
                    "Score = min(100, 0.35*(Imp/5)*35 + 0.30*U_missing*30 + 0.20*I_conflict*20 + 0.15*I_stale*15 + 0.10*H_norm*10)",
                    "Critical Risk: Score >= 75 | High Risk: Score >= 55",
                    "Medium Risk: Score >= 35 | Low Risk: Score < 35"
                ], AMBER)

    add_footer(s4, 4)

    # ==========================================
    # SLIDE 5: Full Dashboard Architecture & Visual Telemetry
    # ==========================================
    s5 = prs.slides.add_slide(blank_layout)
    apply_background(s5)
    add_header(s5, "Executive Dashboard & Live Epistemic Telemetry", "User Interface")

    # Embed dashboard screenshot
    dash_img = os.path.join(screenshots_dir, "dashboard.png")
    if os.path.exists(dash_img):
        s5.shapes.add_picture(dash_img, Inches(0.8), Inches(1.8), Inches(7.5), Inches(4.9))

    create_card(s5, Inches(8.6), Inches(1.8), Inches(3.9), Inches(4.9), 
                "Dashboard Innovations", 
                [
                    "Epistemic Coverage Matrix: Green (Supported), Red (Conflict), Amber (Stale), Hollow (Dark Spot).",
                    "Calculated KPIs: Real-time coverage %, conflict count, dark spot count, and risk score.",
                    "Strict Fact vs. AI Separation: Grounded Evidence Vault (verbatim only) segregated from Uncertainty & Gap Signals.",
                    "One-Click Scholarship Demo: 100% deterministic offline fixture with zero API keys required.",
                    "Direct PDF & JSON report exports."
                ], CYAN)

    add_footer(s5, 5)

    # ==========================================
    # SLIDE 6: Digital Dark Spots Visualizer & Dork Generator
    # ==========================================
    s6 = prs.slides.add_slide(blank_layout)
    apply_background(s6)
    add_header(s6, "Digital Dark Spot Engine & Search Dork Generation", "Signature Feature")

    dark_img = os.path.join(screenshots_dir, "darkspots.png")
    if os.path.exists(dark_img):
        s6.shapes.add_picture(dark_img, Inches(0.8), Inches(1.8), Inches(7.5), Inches(4.9))

    create_card(s6, Inches(8.6), Inches(1.8), Inches(3.9), Inches(4.9), 
                "Dark Spot Engine", 
                [
                    "Zero-in-degree detection flags missing mandatory criteria.",
                    "Exposes that neither the official gazette nor blogs provided submission mode.",
                    "Targeted Search Dork Generator: creates high-intent queries (site:gov.in, filetype:pdf).",
                    "One-click clipboard copy with visual confirmation.",
                    "One-click browser execution directly opening Google search tab."
                ], ROSE)

    add_footer(s6, 6)

    # ==========================================
    # SLIDE 7: Cross-Source Contradiction Matrix
    # ==========================================
    s7 = prs.slides.add_slide(blank_layout)
    apply_background(s7)
    add_header(s7, "Pairwise Cross-Source Contradiction Matrix", "Epistemic Arbitration")

    conf_img = os.path.join(screenshots_dir, "contradictions.png")
    if os.path.exists(conf_img):
        s7.shapes.add_picture(conf_img, Inches(0.8), Inches(1.8), Inches(7.5), Inches(4.9))

    create_card(s7, Inches(8.6), Inches(1.8), Inches(3.9), Inches(4.9), 
                "Contradiction Engine", 
                [
                    "Only compares claims mapped to the identical requirement node.",
                    "Tri-source numeric conflict detection: Rs. 3 Lakh vs Rs. 4 Lakh vs Rs. 2 Lakh.",
                    "Policy negation conflict: Mandatory renewal vs Renewal not required.",
                    "Documentation divergence: Secondary school marksheet vs 6-month bank statement.",
                    "Human-in-the-Loop review actions: Confirmed, Resolved, False Positive."
                ], AMBER)

    add_footer(s7, 7)

    # ==========================================
    # SLIDE 8: Verification Checklist & Entropy Ranking
    # ==========================================
    s8 = prs.slides.add_slide(blank_layout)
    apply_background(s8)
    add_header(s8, "Entropy-Ranked Verification Checklist", "Actionable Output")

    chk_img = os.path.join(screenshots_dir, "checklist.png")
    if os.path.exists(chk_img):
        s8.shapes.add_picture(chk_img, Inches(0.8), Inches(1.8), Inches(7.5), Inches(4.9))

    create_card(s8, Inches(8.6), Inches(1.8), Inches(3.9), Inches(4.9), 
                "Checklist Mechanics", 
                [
                    "Intelligent sorting by Priority Score (0 - 100) based on Shannon entropy.",
                    "Risk Categorization: Critical, High, Medium, Low badges.",
                    "Plain-English rationales explaining why verification is prioritized.",
                    "Actionable next steps tailored to resolve specific discrepancies.",
                    "Interactive resolution state persisted in SQLite database."
                ], INDIGO)

    add_footer(s8, 8)

    # ==========================================
    # SLIDE 9: System Architecture & Tech Stack
    # ==========================================
    s9 = prs.slides.add_slide(blank_layout)
    apply_background(s9)
    add_header(s9, "Full-Stack Technology Stack & Architecture", "Engineering Design")

    create_card(s9, Inches(0.8), Inches(1.8), Inches(3.6), Inches(4.8), 
                "Backend Engine (Python 3.13)", 
                [
                    "FastAPI asynchronous REST API server with OpenAPI docs (/docs, /redoc).",
                    "Pydantic v2 strict request & response schema validation.",
                    "SQLAlchemy 2.0 ORM with SQLite database (WAL mode).",
                    "BeautifulSoup4 HTML sanitizer & main content extractor.",
                    "HTTPX asynchronous client with strict timeout controls.",
                    "ReportLab publication-quality PDF export generator."
                ], CYAN)

    create_card(s9, Inches(4.8), Inches(1.8), Inches(3.6), Inches(4.8), 
                "Frontend Client (React 18 + TS)", 
                [
                    "Vite bundler producing optimized production assets.",
                    "TypeScript strict typing for all API models and views.",
                    "Tailwind CSS custom dark research design system.",
                    "Lucide React iconography with epistemic status colors.",
                    "TanStack Query (React Query) for server-state caching.",
                    "Embedded directly inside FastAPI root route for single-port delivery."
                ], INDIGO)

    create_card(s9, Inches(8.8), Inches(1.8), Inches(3.6), Inches(4.8), 
                "Security & Isolation Layer", 
                [
                    "Comprehensive SSRF Protection Engine blocking private/internal IPs.",
                    "Blocks 127.0.0.1, 10.0.0.0/8, 172.16.0.0/12, 192.168.0.0/16, 169.254.169.254.",
                    "Revalidates resolved DNS addresses post-redirect.",
                    "Immutable source text snapshots hashed via SHA-256.",
                    "Zero API keys required for offline demo fixtures."
                ], EMERALD)

    add_footer(s9, 9)

    # ==========================================
    # SLIDE 10: Verification Test Telemetry
    # ==========================================
    s10 = prs.slides.add_slide(blank_layout)
    apply_background(s10)
    add_header(s10, "Automated Verification & Testing Telemetry", "Quality Assurance")

    create_card(s10, Inches(0.8), Inches(1.8), Inches(5.6), Inches(4.8), 
                "Pytest Test Suite (16/16 Passed - 100%)", 
                [
                    "test_01_requirement_generation: PASSED",
                    "test_02_requirement_graph_validation: PASSED",
                    "test_03_ssrf_url_validation: PASSED",
                    "test_04_html_text_extraction: PASSED",
                    "test_05_claim_grounding_and_exact_offsets: PASSED",
                    "test_06_claim_grounding_mismatch_rejection: PASSED",
                    "test_07_requirement_to_claim_semantic_mapping: PASSED",
                    "test_08_contradiction_detection_numeric: PASSED",
                    "test_09_contradiction_detection_policy_negation: PASSED",
                    "test_10_neutral_claim_handling: PASSED",
                    "test_11_temporal_auditing: PASSED",
                    "test_12_entropy_and_dark_spot_calculation: PASSED",
                    "test_13_dork_generation: PASSED",
                    "test_api_health: PASSED",
                    "test_load_scholarship_demo_deterministic: PASSED",
                    "test_custom_research_workflow: PASSED"
                ], EMERALD)

    create_card(s10, Inches(6.8), Inches(1.8), Inches(5.6), Inches(4.8), 
                "Frontend & E2E Verification", 
                [
                    "npm run typecheck: PASSED (0 TypeScript errors).",
                    "npm run build: PASSED (1,555 modules transformed in 9.35s).",
                    "Puppeteer E2E Browser Automation: PASSED.",
                    "Interactive navigation tested across all 9 tabs.",
                    "Instant demo loading verified on port 8080.",
                    "ReportLab PDF report generation verified (HTTP 200).",
                    "Structured JSON audit serialization verified (HTTP 200)."
                ], CYAN)

    add_footer(s10, 10)

    # ==========================================
    # SLIDE 11: Real-World Use Cases & Impact
    # ==========================================
    s11 = prs.slides.add_slide(blank_layout)
    apply_background(s11)
    add_header(s11, "High-Stakes Real-World Use Cases", "Practical Impact")

    create_card(s11, Inches(0.8), Inches(1.8), Inches(3.6), Inches(4.8), 
                "1. Government Schemes & Fellowships", 
                [
                    "Students navigate confusing scholarship portals with conflicting blog summaries.",
                    "Surfaces unmentioned renewal conditions before accepting loans or stipends.",
                    "Exposes income threshold divergence across regional advisories."
                ], CYAN)

    create_card(s11, Inches(4.8), Inches(1.8), Inches(3.6), Inches(4.8), 
                "2. Visa & Consular Compliance", 
                [
                    "Immigration applicants face complex requirements across embassy pages and blogs.",
                    "Identifies omitted financial solvency proofs or mandatory medical attestations.",
                    "Flags outdated application windows or superseded fee structures."
                ], INDIGO)

    create_card(s11, Inches(8.8), Inches(1.8), Inches(3.6), Inches(4.8), 
                "3. Public Procurement & Tenders", 
                [
                    "Vendors bidding on public contracts must comply with strict eligibility thresholds.",
                    "Detects missing EMD exemption guidelines and conflicting turnover minimums.",
                    "Generates targeted dorks to retrieve gazetted amendment corrigenda."
                ], AMBER)

    add_footer(s11, 11)

    # ==========================================
    # SLIDE 12: Conclusion & Author Acknowledgments
    # ==========================================
    s12 = prs.slides.add_slide(blank_layout)
    apply_background(s12)

    top_bar2 = s12.shapes.add_shape(MSO_SHAPE.RECTANGLE, Inches(0), Inches(0), Inches(13.333), Inches(0.12))
    top_bar2.fill.solid()
    top_bar2.fill.fore_color.rgb = CYAN
    top_bar2.line.fill.background()

    c_box = s12.shapes.add_textbox(Inches(1.0), Inches(1.0), Inches(11.3), Inches(2.2))
    ctf = c_box.text_frame
    ctf.word_wrap = True

    cp1 = ctf.paragraphs[0]
    cp1.text = "NULLSPACE — SEE WHAT THE SOURCES DON'T SAY"
    cp1.font.size = Pt(13)
    cp1.font.bold = True
    cp1.font.color.rgb = CYAN

    cp2 = ctf.add_paragraph()
    cp2.text = "The Future of Epistemic AI Verification"
    cp2.font.size = Pt(36)
    cp2.font.bold = True
    cp2.font.color.rgb = WHITE
    cp2.space_before = Pt(6)

    # Summary Card
    sum_card = s12.shapes.add_shape(MSO_SHAPE.ROUNDED_RECTANGLE, Inches(1.0), Inches(3.2), Inches(11.3), Inches(3.5))
    sum_card.fill.solid()
    sum_card.fill.fore_color.rgb = CARD_BG
    sum_card.line.color.rgb = CYAN
    sum_card.line.width = Pt(1.5)

    stf = sum_card.text_frame
    stf.margin_left = Inches(0.4)
    stf.margin_top = Inches(0.3)

    sp1 = stf.paragraphs[0]
    sp1.text = "PROJECT ARCHITECT & LEAD ENGINEER:"
    sp1.font.size = Pt(11)
    sp1.font.bold = True
    sp1.font.color.rgb = CYAN

    sp2 = stf.add_paragraph()
    sp2.text = AUTHOR_NAME
    sp2.font.size = Pt(26)
    sp2.font.bold = True
    sp2.font.color.rgb = WHITE
    sp2.space_before = Pt(4)

    sp3 = stf.add_paragraph()
    sp3.text = f"{AUTHOR_TITLE} | End-to-End System Delivery"
    sp3.font.size = Pt(12)
    sp3.font.color.rgb = MUTED
    sp3.space_before = Pt(2)

    sp4 = stf.add_paragraph()
    sp4.text = "Key Project Takeaway:"
    sp4.font.size = Pt(12)
    sp4.font.bold = True
    sp4.font.color.rgb = INDIGO
    sp4.space_before = Pt(12)

    sp5 = stf.add_paragraph()
    sp5.text = "NullSpace transforms AI from a gullible summarizer into an adversarial epistemic auditor. By generating counterfactual schemas before reading sources, grounding exact offsets, identifying Digital Dark Spots, and ranking uncertainty with Shannon entropy, NullSpace reveals the critical gaps that conventional systems miss."
    sp5.font.size = Pt(11.5)
    sp5.font.color.rgb = WHITE
    sp5.space_before = Pt(4)

    add_footer(s12, 12)

    # Save Presentation
    output_filename = "NullSpace_Presentation_POCHIRAJU_KAILASH_RAM_MARKANDEYA_SHARMA.pptx"
    output_path = os.path.join(base_dir, output_filename)
    prs.save(output_path)
    print(f"Presentation successfully saved to: {output_path}")

    # Also copy to brain artifact directory
    artifact_dir = r"C:\Users\kaila\.gemini\antigravity\brain\139c2371-8f84-46d5-8b71-884de8583d6e"
    if os.path.exists(artifact_dir):
        import shutil
        shutil.copyfile(output_path, os.path.join(artifact_dir, output_filename))
        print(f"Copied to artifact directory: {artifact_dir}")

if __name__ == "__main__":
    build_presentation()

