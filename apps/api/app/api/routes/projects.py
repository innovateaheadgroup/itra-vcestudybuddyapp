from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.api.deps import get_current_user
from app.core.database import get_db
from app.models.models import Project, ProjectSubmission, User
from app.schemas import ProjectOut, ProjectSubmissionCreate, ProjectSubmissionOut

router = APIRouter(prefix="/projects", tags=["projects"])


@router.get("", response_model=list[ProjectOut])
def list_projects(
    subject_id: int | None = None,
    unit: int | None = Query(default=None, ge=1, le=2),
    db: Session = Depends(get_db),
) -> list[ProjectOut]:
    query = select(Project).where(Project.unit.in_([1, 2]))
    if subject_id:
        query = query.where(Project.subject_id == subject_id)
    if unit:
        query = query.where(Project.unit == unit)
    projects = db.scalars(query.order_by(Project.unit, Project.id)).all()
    return [ProjectOut.model_validate(project) for project in projects]


@router.get("/{project_id}", response_model=ProjectOut)
def get_project(project_id: int, db: Session = Depends(get_db)) -> ProjectOut:
    project = db.scalar(select(Project).where(Project.id == project_id))
    if not project:
        raise HTTPException(status_code=404, detail="Project not found")
    return ProjectOut.model_validate(project)


@router.post("/submissions", response_model=ProjectSubmissionOut)
def submit_project(
    payload: ProjectSubmissionCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> ProjectSubmissionOut:
    project = db.scalar(select(Project).where(Project.id == payload.project_id))
    if not project:
        raise HTTPException(status_code=404, detail="Project not found")

    feedback_json = {
        "manual_feedback": "Initial submission received. Teacher/tutor can add final rubric comments.",
        "ai_stub": {
            "strength": "You have included a relevant artefact.",
            "improve": "Link your reflection explicitly to rubric criteria.",
        },
    }
    submission = ProjectSubmission(
        project_id=payload.project_id,
        user_id=current_user.id,
        submission_type=payload.submission_type,
        content_ref=payload.content_ref,
        reflection_md=payload.reflection_md,
        feedback_json=feedback_json,
    )
    db.add(submission)
    db.commit()
    db.refresh(submission)
    return ProjectSubmissionOut.model_validate(submission)


@router.get("/{project_id}/submissions", response_model=list[ProjectSubmissionOut])
def list_project_submissions(
    project_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> list[ProjectSubmissionOut]:
    submissions = db.scalars(
        select(ProjectSubmission)
        .where(ProjectSubmission.project_id == project_id, ProjectSubmission.user_id == current_user.id)
        .order_by(ProjectSubmission.created_at.desc())
    ).all()
    return [ProjectSubmissionOut.model_validate(submission) for submission in submissions]
