# NullSpace
### *See What the Sources Don't Say.*
**AI-Assisted Counterfactual Schema Alignment & Contradiction Detection Engine**

---

## 1. Problem Statement

Modern retrieval-augmented generation (RAG) and search assistants suffer from a fatal flaw: **Confirmation Bias & Epistemic Blind Spots**.

When asked a high-stakes question (e.g. scholarship eligibility, visa requirements, government procurement tenders), search engines retrieve pages that discuss *some* topics, but they completely fail to warn users about **what is missing**. If no source mentions renewal rules, an applicant may accept a fellowship only to forfeit it the following year. Furthermore, when multiple blogs or news portals contradict the primary gazette notice, users have no easy way to cross-reference verbatim evidence spans.

## 2. Key Innovations

1. **Counterfactual Ontology Generation (Schema-First)**:
   Generates a mandatory Decision Requirement Graph $G = (V, E)$ *prior* to scraping or reading any user-supplied sources. This eliminates retrieval confirmation bias.

2. **Digital Dark Spot Detection ($InDegree(v) = 0$)**:
   Mathematically identifies mandatory requirement nodes that receive zero evidence across all reviewed sources. Generates high-intent targeted search dorks to resolve them.

3. **Strict Fact vs. AI Separation**:
   Verbatim source quotes are anchored with immutable character start/end offsets ($[start, end]$). AI inferences, heuristic warnings, and gap signals are isolated visually and logically from verbatim facts.

4. **Cross-Source Contradiction Matrix**:
   Performs pairwise comparative inference across claims mapped to the same requirement to surface numeric discrepancies, policy negations, and conflicting document mandates.

5. **Temporal Decay Radar**:
   Audits academic cycles (e.g., `2024-25` vs `2026-27`) and calendar years to flag superseded or outdated policies.

6. **Normalized Shannon Entropy Scorer**:
   Calculates evidence entropy $H_{\text{norm}}(X)$ and produces an intelligent $0 - 100$ priority risk score to guide human-in-the-loop verification.

7. **One-Click Offline Scholarship Demo**:
   Loads synthetic demonstration fixtures immediately with zero external API calls or scraping dependencies.

---

## 3. Technology Stack

- **Frontend**: React 18, TypeScript, Vite, Tailwind CSS, Lucide React, Recharts, TanStack Query.
- **Backend**: Python 3.11+, FastAPI, Pydantic v2, SQLAlchemy, SQLite (WAL mode), BeautifulSoup4, HTTPX, ReportLab.
- **Security**: SSRF protection blocking private IP ranges, loopback, cloud metadata endpoints, and DNS re-resolution checks.
- **Testing**: Pytest with unit and end-to-end integration test suites.

---

## 4. Quick Start (Run Locally)

### Prerequisites
- Python 3.11+
- Node.js 18+ and npm

### One-Command Quick Launch (Windows)
```cmd
run_nullspace.bat
```
This script initializes the Python virtual environment, installs backend dependencies, starts the FastAPI server at `http://127.0.0.1:8000`, and opens the application in your browser.

### Manual Setup

#### 1. Backend Setup
```bash
cd backend
python -m venv .venv

# On Windows:
.\.venv\Scripts\activate
# On Linux/macOS:
source .venv/bin/activate

pip install -r requirements.txt
export PYTHONPATH=backend
python -m uvicorn app.main:app --host 127.0.0.1 --port 8000 --reload
```

#### 2. Frontend Setup (Optional for Development)
*Note: The FastAPI backend automatically serves the built frontend production assets directly from `/`. To run Vite in hot-reload development mode:*
```bash
cd frontend
npm install
npm run dev
```
Open [http://localhost:5173](http://localhost:5173).

---

## 5. Running Automated Tests

Run backend unit and integration tests (20 verification checkpoints):
```bash
# Windows
$env:PYTHONPATH="backend"
.\backend\.venv\Scripts\python -m pytest backend\tests -v

# Linux/macOS
PYTHONPATH=backend ./backend/.venv/bin/python -m pytest backend/tests -v
```

Test frontend typechecking and production build:
```bash
cd frontend
npm run typecheck
npm run build
```

---

## 6. One-Click Scholarship Demo Walkthrough

1. Open `http://localhost:8000` (or `http://localhost:5173`).
2. Click the **Load Scholarship Demo** button in the header.
3. Observe:
   - **Total Requirements**: 7 nodes generated *prior* to ingestion.
   - **Digital Dark Spot**: *Official Application Portal* has $InDegree = 0$.
   - **Contradictions Matrix**:
     - Income Threshold: Gazette (Rs. 3 Lakh) vs Blog A (Rs. 4 Lakh) vs Blog B (Rs. 2 Lakh).
     - Renewal Policy: Blog A (Mandatory with 7.5 CGPA) vs Blog B (Automatic continuation; renewal not required).
     - Documentation: Gazette (Marksheet) vs Blog B (Bank Statement).
   - **Temporal Warning**: Blog A flagged as AY 2025-26; Blog B flagged as 2024 Reference.
   - **Verification Checklist**: Items ranked by priority score ($0-100$) with one-click Google search dorks.
   - **Export**: Click **PDF** or **JSON** in the header to download the report.

---

## 7. Folder Structure

```text
NullSpace/
├── backend/
│   ├── app/
│   │   ├── api/          # FastAPI REST endpoints
│   │   ├── core/         # Config, settings, SSRF security
│   │   ├── database/     # SQLite SQLAlchemy session
│   │   ├── models/       # Database models
│   │   ├── schemas/      # Pydantic v2 schemas
│   │   ├── services/
│   │   │   ├── ontology/       # Counterfactual graph generator
│   │   │   ├── ingestion/      # SSRF-protected safe fetcher
│   │   │   ├── extraction/     # Atomic claim extractor & offset verifier
│   │   │   ├── alignment/      # Bipartite graph alignment engine
│   │   │   ├── contradiction/  # Pairwise contradiction detector
│   │   │   ├── temporal/       # Temporal decay & cycle auditor
│   │   │   ├── prioritization/ # Shannon entropy & risk scorer
│   │   │   ├── dorks/          # Targeted search query generator
│   │   │   ├── demo/           # Synthetic scholarship fixtures
│   │   │   └── export/         # ReportLab PDF & JSON exporter
│   │   └── main.py
│   ├── tests/            # Automated test suite
│   ├── requirements.txt
│   └── Dockerfile
│
├── frontend/
│   ├── src/
│   │   ├── components/   # Dashboard, Ontology, Vault, Conflicts, DarkSpots, etc.
│   │   ├── services/     # Typed API client
│   │   ├── types/        # TypeScript interfaces
│   │   ├── App.tsx       # Root UI shell
│   │   └── main.tsx
│   ├── package.json
│   ├── vite.config.ts
│   └── Dockerfile
│
├── docs/
│   ├── ARCHITECTURE.md   # Architectural specifications & formulas
│   └── API.md            # REST API endpoints contract
├── .env.example
├── docker-compose.yml
├── run_nullspace.bat
├── run_nullspace.sh
└── README.md
```

---

## 8. License & Disclaimers

**Disclaimer:** NullSpace is an epistemic consistency engine designed for informational research. "Grounded & Supported" describes consistent evidence coverage across analyzed sources, not independent legal or government proof. Always cross-examine with official gazette notifications.

