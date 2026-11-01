# NullSpace System Architecture

## Overview
NullSpace is an AI-assisted counterfactual schema alignment and contradiction detection engine designed to detect:
1. Missing Information (Digital Dark Spots)
2. Cross-Source Factual Contradictions
3. Outdated or Stale Application Cycles
4. Ungrounded Claims
5. Epistemic Uncertainty using Normalized Shannon Entropy

```
+-------------------------------------------------------------------------------+
|                             NULLSPACE CLIENT (SPA)                            |
|             React 18 + TypeScript + Tailwind CSS + Lucide Icons               |
+-------------------------------------------------------------------------------+
         |                                                   ^
         | REST API Calls                                    | JSON & PDF Streams
         v                                                   |
+-------------------------------------------------------------------------------+
|                             FASTAPI APPLICATION LAYER                         |
|   /api/health | /api/research | /api/demo/load | /api/analyze | /api/export   |
+-------------------------------------------------------------------------------+
         |                        |                        |
         v                        v                        v
+------------------+    +-------------------+    +-------------------+
|  Ontology Engine |    | Safe Ingestion    |    | Claim Extractor   |
| (Schema-First)   |    | (SSRF Protection) |    | (Exact Offsets)   |
+------------------+    +-------------------+    +-------------------+
         |                        |                        |
         +------------------------+------------------------+
                                  |
                                  v
+-------------------------------------------------------------------------------+
|                            EPISTEMIC AUDIT SERVICES                           |
|  - Bipartite Graph Alignment Engine (Requirements <-> Claims)                 |
|  - Digital Dark Spot Identification (InDegree(v) = 0 for mandatory nodes)     |
|  - Cross-Source Contradiction Matrix (Pairwise NLI & Threshold Diff)          |
|  - Temporal Decay Radar (Academic Cycle & Calendar Year Auditor)              |
|  - Shannon Entropy Scorer (Normalized Evidence Entropy & 0-100 Priority)      |
|  - Targeted Search Dork Generator (Bypass noise with high-intent operators)   |
+-------------------------------------------------------------------------------+
                                  |
                                  v
+-------------------------------------------------------------------------------+
|                       DATA PERSISTENCE & EXPORT LAYER                         |
|  - SQLite (WAL mode) with SQLAlchemy ORM                                      |
|  - ReportLab PDF Generation Engine & Structured JSON Serializer               |
+-------------------------------------------------------------------------------+
```

---

## Core Algorithms & Mathematical Formulations

### 1. Counterfactual Schema Generation
Unlike naive RAG pipelines that summarize whatever a search engine retrieves, NullSpace constructs a mandatory Decision Requirement Graph $G = (V, E)$ *prior* to reading any external sources.
For any research domain, $V$ contains requirement nodes $v_i = (\text{name}, \text{description}, \text{mandatory}, \text{importance})$.

### 2. Exact Span Offsets & Immutability
When a source document is ingested:
1. Cleaned text is normalized and hashed via SHA-256:
   $$\text{ContentHash} = \text{SHA256}(\text{RawText})$$
2. For every extracted claim $c$, its quote span $[start, end]$ is mathematically validated:
   $$\text{RawText}[start : end] == c.\text{exact\_quote}$$
   If any discrepancy exists, the claim is marked ungrounded and rejected from the primary evidence vault.

### 3. Digital Dark Spot Condition
For any mandatory node $v \in V_{\text{mandatory}}$:
$$\text{IsDarkSpot}(v) \iff \text{InDegree}(v) = 0$$
$$\text{InDegree}(v) = |\{ c \in \text{Claims} : \text{mapped}(c, v) \}|$$
When $\text{InDegree}(v) = 0$, the system proves that none of the ingested sources provided the mandatory decision information.

### 4. Normalized Shannon Evidence Entropy
For any requirement node $v$ with $N > 0$ claims distributed over $k=4$ epistemic states (Support, Contradiction, Stale, Unverified):
$$H(X_v) = -\sum_{i=1}^k p_i \log_2(p_i)$$
$$H_{\text{norm}}(X_v) = \frac{H(X_v)}{\log_2(k)}$$
For missing requirements ($N = 0$), missingness uncertainty is defined as maximum: $U_{\text{missing}} = 1.0$.

### 5. Priority Risk Score ($0 - 100$)
$$\text{PriorityScore}(v) = \min\left(100, \left( 
0.35 \cdot \frac{\text{Importance}}{5} \cdot 35 + 
0.30 \cdot U_{\text{missing}} \cdot 30 + 
0.20 \cdot \mathbb{I}_{\text{conflict}} \cdot 20 + 
0.15 \cdot \mathbb{I}_{\text{stale}} \cdot 15 + 
0.10 \cdot H_{\text{norm}} \cdot 10 
\right)\right)$$
- **Critical Risk**: Score $\ge 75$
- **High Risk**: Score $\ge 55$
- **Medium Risk**: Score $\ge 35$
- **Low Risk**: Score $< 35$

