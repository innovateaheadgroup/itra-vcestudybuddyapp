from app.models.models import EvidenceLog, SATMilestone, SATProject
from app.services.sat_export import generate_sat_export_html


def test_sat_export_html_generation() -> None:
    project = SATProject(id=1, user_id=1, subject_id=1, title="SAT Demo", context_md="Context section")
    milestones = [
        SATMilestone(
            id=1,
            sat_project_id=1,
            part=1,
            checklist_json={"items": ["A"]},
            status_json={"completed": []},
            due_dates_json={},
        )
    ]
    evidence = [
        EvidenceLog(
            id=1,
            sat_project_id=1,
            entry_type="decision",
            content_md="Chose iterative design",
            attachment_refs_json={"urls": ["https://example.com"]},
        )
    ]
    html = generate_sat_export_html(project, milestones, evidence)
    assert "<html" in html.lower()
    assert "SAT Demo" in html
    assert "Chose iterative design" in html
