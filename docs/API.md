# NullSpace REST API Specification

### System Endpoints
- `GET /api/health` — Service health check and engine version.
- `GET /docs` — Interactive OpenAPI / Swagger UI documentation.
- `GET /redoc` — ReDoc visual API documentation.

### Demo Endpoints
- `POST /api/demo/load` — Instant load of the deterministic synthetic scholarship demo dataset (3 sources, 7 requirements, guaranteed contradictions, dark spots, temporal warnings). Requires zero API keys.

### Research Project Management
- `POST /api/research` — Initialize research project and auto-generate counterfactual decision requirement graph.
- `GET /api/research` — List all stored research projects.
- `GET /api/research/{research_id}` — Get project metadata, requirement nodes, and sources.
- `DELETE /api/research/{research_id}` — Cascade delete project and all associated derived records.

### Ontology Node Endpoints
- `POST /api/research/{research_id}/requirements` — Add custom requirement node.
- `PUT /api/research/{research_id}/requirements/{node_id}` — Update name, description, importance, or mandatory flag.
- `DELETE /api/research/{research_id}/requirements/{node_id}` — Remove requirement node.

### Source Ingestion Endpoints (SSRF Safe)
- `POST /api/research/{research_id}/sources` — Fetch and sanitize live URL with SSRF protection.
- `POST /api/research/{research_id}/sources/manual` — Ingest manual raw text snapshot.
- `GET /api/research/{research_id}/sources` — List all ingested sources with SHA-256 hashes.
- `DELETE /api/research/{research_id}/sources/{source_id}` — Remove source document.

### Epistemic Analysis Endpoints
- `POST /api/research/{research_id}/analyze` — Run complete epistemic pipeline (claim extraction, alignment, dark spot detection, pairwise contradiction detection, temporal decay radar, entropy prioritization).
- `GET /api/research/{research_id}/results` — Get complete epistemic analysis results.
- `GET /api/research/{research_id}/dark-spots` — Get list of requirements with InDegree = 0.
- `GET /api/research/{research_id}/conflicts` — Get list of cross-source contradiction records.
- `GET /api/research/{research_id}/temporal` — Get temporal audit and academic cycle results.
- `GET /api/research/{research_id}/checklist` — Get entropy-ranked verification checklist.

### Human-in-the-Loop Reviews
- `PATCH /api/conflicts/{conflict_id}` — Update status (`confirmed`, `resolved`, `false_positive`, `requires_review`) and user notes.
- `PATCH /api/checklist/{item_id}` — Toggle resolution state of verification checklist item.

### Export Endpoints
- `GET /api/research/{research_id}/export/json` — Download full audit analysis JSON.
- `GET /api/research/{research_id}/export/pdf` — Download publication-ready PDF report generated via ReportLab.

