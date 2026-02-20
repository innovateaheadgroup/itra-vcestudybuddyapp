from __future__ import annotations

from markupsafe import escape

from app.models.models import EvidenceLog, SATMilestone, SATProject


def generate_sat_export_html(
    project: SATProject, milestones: list[SATMilestone], evidence_logs: list[EvidenceLog]
) -> str:
    milestone_html = "".join([f"""
            <section>
              <h3>Part {m.part}</h3>
              <pre>{escape(str(m.checklist_json))}</pre>
              <pre>{escape(str(m.status_json))}</pre>
              <pre>{escape(str(m.due_dates_json))}</pre>
            </section>
            """ for m in milestones])
    evidence_html = "".join([f"""
            <article>
              <h4>{escape(log.entry_type.title())}</h4>
              <p>{escape(log.content_md)}</p>
              <pre>{escape(str(log.attachment_refs_json))}</pre>
            </article>
            """ for log in evidence_logs])

    return f"""<!doctype html>
<html lang="en">
  <head>
    <meta charset="utf-8" />
    <title>SAT Export - {escape(project.title)}</title>
    <style>
      body {{ font-family: Arial, sans-serif; margin: 24px; color: #1f2937; }}
      h1, h2, h3 {{ color: #111827; }}
      section, article {{ border: 1px solid #d1d5db; padding: 12px; margin-bottom: 12px; border-radius: 8px; }}
      pre {{ white-space: pre-wrap; background: #f9fafb; padding: 8px; border-radius: 6px; }}
    </style>
  </head>
  <body>
    <h1>{escape(project.title)}</h1>
    <h2>Context</h2>
    <p>{escape(project.context_md)}</p>
    <h2>Milestones</h2>
    {milestone_html or "<p>No milestones yet.</p>"}
    <h2>Evidence Log</h2>
    {evidence_html or "<p>No evidence entries yet.</p>"}
  </body>
</html>"""
