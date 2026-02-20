from datetime import datetime

from sqlalchemy import DateTime, Float, ForeignKey, Integer, String, Text, UniqueConstraint, func
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy.types import JSON

from app.core.database import Base


class TimestampMixin:
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())


class User(Base, TimestampMixin):
    __tablename__ = "users"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    email: Mapped[str] = mapped_column(String(255), unique=True, index=True)
    password_hash: Mapped[str] = mapped_column(String(255))
    role: Mapped[str] = mapped_column(String(20), default="student")

    attempts: Mapped[list["Attempt"]] = relationship(back_populates="user")
    mastery_items: Mapped[list["Mastery"]] = relationship(back_populates="user")
    quickwins_items: Mapped[list["QuickWinsQueue"]] = relationship(back_populates="user")


class PasswordResetToken(Base, TimestampMixin):
    __tablename__ = "password_reset_tokens"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id", ondelete="CASCADE"), index=True)
    token: Mapped[str] = mapped_column(String(255), unique=True, index=True)
    expires_at: Mapped[datetime] = mapped_column(DateTime(timezone=True))
    used_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)


class Subject(Base):
    __tablename__ = "subjects"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    code: Mapped[str] = mapped_column(String(20), unique=True, index=True)
    name: Mapped[str] = mapped_column(String(120))

    topics: Mapped[list["Topic"]] = relationship(back_populates="subject")
    projects: Mapped[list["Project"]] = relationship(back_populates="subject")
    sat_projects: Mapped[list["SATProject"]] = relationship(back_populates="subject")


class Topic(Base):
    __tablename__ = "topics"
    __table_args__ = (UniqueConstraint("subject_id", "unit", "order", name="uq_topic_subject_unit_order"),)

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    subject_id: Mapped[int] = mapped_column(ForeignKey("subjects.id", ondelete="CASCADE"), index=True)
    unit: Mapped[int] = mapped_column(Integer, index=True)
    aos: Mapped[str] = mapped_column(String(120))
    outcome: Mapped[str] = mapped_column(String(120))
    title: Mapped[str] = mapped_column(String(255))
    order: Mapped[int] = mapped_column(Integer)
    key_skills_json: Mapped[dict] = mapped_column(JSON, default=dict)

    subject: Mapped["Subject"] = relationship(back_populates="topics")
    lessons: Mapped[list["Lesson"]] = relationship(back_populates="topic")
    questions: Mapped[list["Question"]] = relationship(back_populates="topic")


class Lesson(Base):
    __tablename__ = "lessons"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    topic_id: Mapped[int] = mapped_column(ForeignKey("topics.id", ondelete="CASCADE"), index=True)
    title: Mapped[str] = mapped_column(String(255))
    content_md: Mapped[str] = mapped_column(Text)
    estimated_minutes: Mapped[int] = mapped_column(Integer, default=30)

    topic: Mapped["Topic"] = relationship(back_populates="lessons")


class DatasetAsset(Base, TimestampMixin):
    __tablename__ = "dataset_assets"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    user_id: Mapped[int | None] = mapped_column(ForeignKey("users.id", ondelete="SET NULL"), nullable=True)
    filename: Mapped[str] = mapped_column(String(255))
    storage_ref: Mapped[str] = mapped_column(String(500))
    columns_json: Mapped[dict] = mapped_column(JSON, default=dict)


class DataChartConfig(Base, TimestampMixin):
    __tablename__ = "data_chart_configs"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    dataset_id: Mapped[int] = mapped_column(ForeignKey("dataset_assets.id", ondelete="CASCADE"), index=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id", ondelete="CASCADE"), index=True)
    config_json: Mapped[dict] = mapped_column(JSON, default=dict)


class Question(Base):
    __tablename__ = "questions"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    topic_id: Mapped[int] = mapped_column(ForeignKey("topics.id", ondelete="CASCADE"), index=True)
    type: Mapped[str] = mapped_column(String(30), index=True)
    exam_style: Mapped[str] = mapped_column(String(30), index=True)
    command_terms: Mapped[list[str]] = mapped_column(JSON, default=list)
    marks: Mapped[int] = mapped_column(Integer, default=1)
    difficulty: Mapped[int] = mapped_column(Integer, default=1)
    prompt_md: Mapped[str] = mapped_column(Text)
    case_material_md: Mapped[str | None] = mapped_column(Text, nullable=True)
    options_json: Mapped[dict | None] = mapped_column(JSON, nullable=True)
    correct_json: Mapped[dict | None] = mapped_column(JSON, nullable=True)
    rubric_json: Mapped[dict | None] = mapped_column(JSON, nullable=True)
    starter_code: Mapped[str | None] = mapped_column(Text, nullable=True)
    tests_public: Mapped[str | None] = mapped_column(Text, nullable=True)
    tests_hidden: Mapped[str | None] = mapped_column(Text, nullable=True)
    dataset_id: Mapped[int | None] = mapped_column(ForeignKey("dataset_assets.id"), nullable=True)

    topic: Mapped["Topic"] = relationship(back_populates="questions")
    attempts: Mapped[list["Attempt"]] = relationship(back_populates="question")


class Attempt(Base, TimestampMixin):
    __tablename__ = "attempts"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id", ondelete="CASCADE"), index=True)
    question_id: Mapped[int] = mapped_column(ForeignKey("questions.id", ondelete="CASCADE"), index=True)
    answer_text: Mapped[str | None] = mapped_column(Text, nullable=True)
    code_snapshot: Mapped[str | None] = mapped_column(Text, nullable=True)
    score: Mapped[int] = mapped_column(Integer, default=0)
    max_score: Mapped[int] = mapped_column(Integer, default=0)
    feedback_json: Mapped[dict] = mapped_column(JSON, default=dict)
    mistake_tags: Mapped[list[str]] = mapped_column(JSON, default=list)

    user: Mapped["User"] = relationship(back_populates="attempts")
    question: Mapped["Question"] = relationship(back_populates="attempts")


class Mastery(Base):
    __tablename__ = "mastery"
    __table_args__ = (UniqueConstraint("user_id", "topic_id", name="uq_mastery_user_topic"),)

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id", ondelete="CASCADE"), index=True)
    topic_id: Mapped[int] = mapped_column(ForeignKey("topics.id", ondelete="CASCADE"), index=True)
    mastery_score: Mapped[float] = mapped_column(Float, default=0.0)
    last_practiced_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)

    user: Mapped["User"] = relationship(back_populates="mastery_items")


class QuickWinsQueue(Base):
    __tablename__ = "quickwins_queue"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id", ondelete="CASCADE"), index=True)
    topic_id: Mapped[int | None] = mapped_column(ForeignKey("topics.id", ondelete="CASCADE"), nullable=True)
    question_id: Mapped[int | None] = mapped_column(
        ForeignKey("questions.id", ondelete="CASCADE"), nullable=True
    )
    next_due_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())
    interval_days: Mapped[int] = mapped_column(Integer, default=1)
    ease_factor: Mapped[float] = mapped_column(Float, default=2.5)

    user: Mapped["User"] = relationship(back_populates="quickwins_items")


class Project(Base):
    __tablename__ = "projects"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    subject_id: Mapped[int] = mapped_column(ForeignKey("subjects.id", ondelete="CASCADE"), index=True)
    unit: Mapped[int] = mapped_column(Integer, index=True)
    title: Mapped[str] = mapped_column(String(255))
    brief_md: Mapped[str] = mapped_column(Text)
    rubric_json: Mapped[dict] = mapped_column(JSON, default=dict)

    subject: Mapped["Subject"] = relationship(back_populates="projects")
    submissions: Mapped[list["ProjectSubmission"]] = relationship(back_populates="project")


class ProjectSubmission(Base, TimestampMixin):
    __tablename__ = "project_submissions"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    project_id: Mapped[int] = mapped_column(ForeignKey("projects.id", ondelete="CASCADE"), index=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id", ondelete="CASCADE"), index=True)
    submission_type: Mapped[str] = mapped_column(String(20))
    content_ref: Mapped[str] = mapped_column(Text)
    reflection_md: Mapped[str | None] = mapped_column(Text, nullable=True)
    feedback_json: Mapped[dict] = mapped_column(JSON, default=dict)

    project: Mapped["Project"] = relationship(back_populates="submissions")


class SATProject(Base, TimestampMixin):
    __tablename__ = "sat_projects"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id", ondelete="CASCADE"), index=True)
    subject_id: Mapped[int] = mapped_column(ForeignKey("subjects.id", ondelete="CASCADE"), index=True)
    title: Mapped[str] = mapped_column(String(255))
    context_md: Mapped[str] = mapped_column(Text)

    subject: Mapped["Subject"] = relationship(back_populates="sat_projects")
    milestones: Mapped[list["SATMilestone"]] = relationship(back_populates="sat_project")
    evidence_logs: Mapped[list["EvidenceLog"]] = relationship(back_populates="sat_project")


class SATMilestone(Base):
    __tablename__ = "sat_milestones"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    sat_project_id: Mapped[int] = mapped_column(
        ForeignKey("sat_projects.id", ondelete="CASCADE"), index=True
    )
    part: Mapped[int] = mapped_column(Integer)
    checklist_json: Mapped[dict] = mapped_column(JSON, default=dict)
    status_json: Mapped[dict] = mapped_column(JSON, default=dict)
    due_dates_json: Mapped[dict] = mapped_column(JSON, default=dict)

    sat_project: Mapped["SATProject"] = relationship(back_populates="milestones")


class EvidenceLog(Base, TimestampMixin):
    __tablename__ = "evidence_logs"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    sat_project_id: Mapped[int] = mapped_column(
        ForeignKey("sat_projects.id", ondelete="CASCADE"), index=True
    )
    entry_type: Mapped[str] = mapped_column(String(30))
    content_md: Mapped[str] = mapped_column(Text)
    attachment_refs_json: Mapped[dict] = mapped_column(JSON, default=dict)

    sat_project: Mapped["SATProject"] = relationship(back_populates="evidence_logs")


class CodeSnapshot(Base, TimestampMixin):
    __tablename__ = "code_snapshots"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id", ondelete="CASCADE"), index=True)
    filename: Mapped[str] = mapped_column(String(255))
    content: Mapped[str] = mapped_column(Text)
    metadata_json: Mapped[dict] = mapped_column(JSON, default=dict)
