import pytest
from fastapi.testclient import TestClient
from app.main import app
from app.database.session import SessionLocal, init_db

client = TestClient(app)

@pytest.fixture(autouse=True)
def setup_database():
    init_db()
    yield

def test_api_health():
    res = client.get("/api/health")
    assert res.status_code == 200
    assert res.json()["status"] == "healthy"

def test_load_scholarship_demo_deterministic():
    res = client.post("/api/demo/load")
    assert res.status_code == 200
    data = res.json()
    assert "research_id" in data
    research_id = data["research_id"]

    # Verify analysis results
    res_analysis = client.get(f"/api/research/{research_id}/results")
    assert res_analysis.status_code == 200
    analysis = res_analysis.json()
    
    assert analysis["kpis"]["total_requirements"] >= 7
    assert analysis["kpis"]["detected_conflicts_count"] >= 2
    assert analysis["kpis"]["dark_spots_count"] >= 1
    assert len(analysis["checklist"]) >= 3

    # Test PDF export
    pdf_res = client.get(f"/api/research/{research_id}/export/pdf")
    assert pdf_res.status_code == 200
    assert pdf_res.headers["content-type"] == "application/pdf"
    assert len(pdf_res.content) > 1000

    # Test JSON export
    json_res = client.get(f"/api/research/{research_id}/export/json")
    assert json_res.status_code == 200
    json_data = json_res.json()
    assert json_data["engine"] == "NullSpace Epistemic Audit Engine"

def test_custom_research_workflow():
    # 1. Create Research Project (generates counterfactual ontology before sources)
    p_res = client.post("/api/research", json={
        "title": "State Merit Higher Ed Grant",
        "domain": "scholarship",
        "objective": "Find all eligibility criteria, income thresholds, and deadlines for state grants"
    })
    assert p_res.status_code == 200
    p_data = p_res.json()
    r_id = p_data["id"]
    assert p_data["requirements_count"] >= 5

    # 2. Add manual source
    s_res = client.post(f"/api/research/{r_id}/sources/manual", json={
        "title": "State Higher Education Circular",
        "text": "Annual gross family income must not exceed Rs. 3,00,000. Application deadline is 31 December 2026. Applicants must submit income certificate and marksheet.",
        "published_date": "2026-09-01"
    })
    assert s_res.status_code == 200
    assert s_res.json()["status"] == "ingested"

    # 3. Run Analysis Pipeline
    a_res = client.post(f"/api/research/{r_id}/analyze")
    assert a_res.status_code == 200
    analysis = a_res.json()

    assert analysis["kpis"]["total_requirements"] >= 5
    assert analysis["kpis"]["evidence_coverage_pct"] > 0
    # Mandatory requirement without claim is flagged as Dark Spot (e.g. renewal policy)
    assert any(m["is_dark_spot"] for m in analysis["matrix"])

