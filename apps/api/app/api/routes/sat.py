from fastapi import APIRouter, Depends, HTTPException
from fastapi.responses import HTMLResponse
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.api.deps import get_current_user
from app.core.database import get_db
from app.models.models import EvidenceLog, SATMilestone, SATProject, User
from app.schemas import (
    EvidenceLogCreate,
    EvidenceLogOut,
    SATMilestoneOut,
    SATProjectCreate,
    SATProjectOut,
)
from app.services.sat_export import generate_sat_export_html

router = APIRouter(prefix="/sat", tags=["sat"])


@router.get("/projects", response_model=list[SATProjectOut])
def list_sat_projects(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> list[SATProjectOut]:
    projects = db.scalars(
        select(SATProject)
        .where(SATProject.user_id == current_user.id)
        .order_by(SATProject.created_at.desc())
    ).all()
    return [SATProjectOut.model_validate(project) for project in projects]


@router.post("/projects", response_model=SATProjectOut)
def create_sat_project(
    payload: SATProjectCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> SATProjectOut:
    project = SATProject(
        user_id=current_user.id,
        subject_id=payload.subject_id,
        title=payload.title,
        context_md=payload.context_md,
    )
    db.add(project)
    db.commit()
    db.refresh(project)

    # Starter milestones for SAT Part 1 and Part 2.
    for part in [1, 2]:
        milestone = SATMilestone(
            sat_project_id=project.id,
            part=part,
            checklist_json={
                "items": [
                    "Define problem/context",
                    "Document approach decisions",
                    "Record test evidence",
                    "Reflect on improvements",
                ]
            },
            status_json={"completed": []},
            due_dates_json={},
        )
        db.add(milestone)
    db.commit()
    return SATProjectOut.model_validate(project)


@router.get("/projects/{project_id}/milestones", response_model=list[SATMilestoneOut])
def list_milestones(
    project_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> list[SATMilestoneOut]:
    project = db.scalar(
        select(SATProject).where(SATProject.id == project_id, SATProject.user_id == current_user.id)
    )
    if not project:
        raise HTTPException(status_code=404, detail="SAT project not found")
    milestones = db.scalars(
        select(SATMilestone)
        .where(SATMilestone.sat_project_id == project.id)
        .order_by(SATMilestone.part)
    ).all()
    return [SATMilestoneOut.model_validate(item) for item in milestones]


@router.post("/evidence", response_model=EvidenceLogOut)
def create_evidence_log(
    payload: EvidenceLogCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> EvidenceLogOut:
    project = db.scalar(
        select(SATProject).where(
            SATProject.id == payload.sat_project_id, SATProject.user_id == current_user.id
        )
    )
    if not project:
        raise HTTPException(status_code=404, detail="SAT project not found")
    log = EvidenceLog(
        sat_project_id=payload.sat_project_id,
        entry_type=payload.entry_type,
        content_md=payload.content_md,
        attachment_refs_json=payload.attachment_refs_json,
    )
    db.add(log)
    db.commit()
    db.refresh(log)
    return EvidenceLogOut.model_validate(log)


@router.get("/projects/{project_id}/evidence", response_model=list[EvidenceLogOut])
def list_evidence(
    project_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> list[EvidenceLogOut]:
    project = db.scalar(
        select(SATProject).where(SATProject.id == project_id, SATProject.user_id == current_user.id)
    )
    if not project:
        raise HTTPException(status_code=404, detail="SAT project not found")
    entries = db.scalars(
        select(EvidenceLog)
        .where(EvidenceLog.sat_project_id == project_id)
        .order_by(EvidenceLog.created_at.desc())
    ).all()
    return [EvidenceLogOut.model_validate(log) for log in entries]


@router.get("/{project_id}/export", response_class=HTMLResponse)
def export_sat(
    project_id: int, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)
) -> str:
    project = db.scalar(
        select(SATProject).where(SATProject.id == project_id, SATProject.user_id == current_user.id)
    )
    if not project:
        raise HTTPException(status_code=404, detail="SAT project not found")
    milestones = db.scalars(
        select(SATMilestone)
        .where(SATMilestone.sat_project_id == project.id)
        .order_by(SATMilestone.part)
    ).all()
    evidence = db.scalars(
        select(EvidenceLog)
        .where(EvidenceLog.sat_project_id == project.id)
        .order_by(EvidenceLog.created_at.desc())
    ).all()
    return generate_sat_export_html(project, milestones, evidence)
