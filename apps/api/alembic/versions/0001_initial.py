"""initial schema

Revision ID: 0001_initial
Revises:
Create Date: 2026-02-20 00:00:00.000000
"""

from collections.abc import Sequence

import sqlalchemy as sa
from alembic import op

# revision identifiers, used by Alembic.
revision: str = "0001_initial"
down_revision: str | None = None
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    op.create_table(
        "users",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("email", sa.String(length=255), nullable=False, unique=True),
        sa.Column("password_hash", sa.String(length=255), nullable=False),
        sa.Column("role", sa.String(length=20), nullable=False, server_default="student"),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
    )
    op.create_index("ix_users_email", "users", ["email"], unique=True)

    op.create_table(
        "password_reset_tokens",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("user_id", sa.Integer(), sa.ForeignKey("users.id", ondelete="CASCADE"), nullable=False),
        sa.Column("token", sa.String(length=255), nullable=False, unique=True),
        sa.Column("expires_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("used_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
    )
    op.create_index("ix_password_reset_tokens_user_id", "password_reset_tokens", ["user_id"])
    op.create_index("ix_password_reset_tokens_token", "password_reset_tokens", ["token"], unique=True)

    op.create_table(
        "subjects",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("code", sa.String(length=20), nullable=False, unique=True),
        sa.Column("name", sa.String(length=120), nullable=False),
    )
    op.create_index("ix_subjects_code", "subjects", ["code"], unique=True)

    op.create_table(
        "topics",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("subject_id", sa.Integer(), sa.ForeignKey("subjects.id", ondelete="CASCADE"), nullable=False),
        sa.Column("unit", sa.Integer(), nullable=False),
        sa.Column("aos", sa.String(length=120), nullable=False),
        sa.Column("outcome", sa.String(length=120), nullable=False),
        sa.Column("title", sa.String(length=255), nullable=False),
        sa.Column("order", sa.Integer(), nullable=False),
        sa.Column("key_skills_json", sa.JSON(), nullable=False, server_default=sa.text("'{}'::json")),
        sa.UniqueConstraint("subject_id", "unit", "order", name="uq_topic_subject_unit_order"),
    )
    op.create_index("ix_topics_subject_id", "topics", ["subject_id"])
    op.create_index("ix_topics_unit", "topics", ["unit"])

    op.create_table(
        "lessons",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("topic_id", sa.Integer(), sa.ForeignKey("topics.id", ondelete="CASCADE"), nullable=False),
        sa.Column("title", sa.String(length=255), nullable=False),
        sa.Column("content_md", sa.Text(), nullable=False),
        sa.Column("estimated_minutes", sa.Integer(), nullable=False, server_default="30"),
    )
    op.create_index("ix_lessons_topic_id", "lessons", ["topic_id"])

    op.create_table(
        "dataset_assets",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("user_id", sa.Integer(), sa.ForeignKey("users.id", ondelete="SET NULL"), nullable=True),
        sa.Column("filename", sa.String(length=255), nullable=False),
        sa.Column("storage_ref", sa.String(length=500), nullable=False),
        sa.Column("columns_json", sa.JSON(), nullable=False, server_default=sa.text("'{}'::json")),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
    )

    op.create_table(
        "data_chart_configs",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column(
            "dataset_id", sa.Integer(), sa.ForeignKey("dataset_assets.id", ondelete="CASCADE"), nullable=False
        ),
        sa.Column("user_id", sa.Integer(), sa.ForeignKey("users.id", ondelete="CASCADE"), nullable=False),
        sa.Column("config_json", sa.JSON(), nullable=False, server_default=sa.text("'{}'::json")),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
    )
    op.create_index("ix_data_chart_configs_dataset_id", "data_chart_configs", ["dataset_id"])
    op.create_index("ix_data_chart_configs_user_id", "data_chart_configs", ["user_id"])

    op.create_table(
        "questions",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("topic_id", sa.Integer(), sa.ForeignKey("topics.id", ondelete="CASCADE"), nullable=False),
        sa.Column("type", sa.String(length=30), nullable=False),
        sa.Column("exam_style", sa.String(length=30), nullable=False),
        sa.Column("command_terms", sa.JSON(), nullable=False, server_default=sa.text("'[]'::json")),
        sa.Column("marks", sa.Integer(), nullable=False, server_default="1"),
        sa.Column("difficulty", sa.Integer(), nullable=False, server_default="1"),
        sa.Column("prompt_md", sa.Text(), nullable=False),
        sa.Column("case_material_md", sa.Text(), nullable=True),
        sa.Column("options_json", sa.JSON(), nullable=True),
        sa.Column("correct_json", sa.JSON(), nullable=True),
        sa.Column("rubric_json", sa.JSON(), nullable=True),
        sa.Column("starter_code", sa.Text(), nullable=True),
        sa.Column("tests_public", sa.Text(), nullable=True),
        sa.Column("tests_hidden", sa.Text(), nullable=True),
        sa.Column("dataset_id", sa.Integer(), sa.ForeignKey("dataset_assets.id"), nullable=True),
    )
    op.create_index("ix_questions_topic_id", "questions", ["topic_id"])
    op.create_index("ix_questions_type", "questions", ["type"])
    op.create_index("ix_questions_exam_style", "questions", ["exam_style"])

    op.create_table(
        "attempts",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("user_id", sa.Integer(), sa.ForeignKey("users.id", ondelete="CASCADE"), nullable=False),
        sa.Column("question_id", sa.Integer(), sa.ForeignKey("questions.id", ondelete="CASCADE"), nullable=False),
        sa.Column("answer_text", sa.Text(), nullable=True),
        sa.Column("code_snapshot", sa.Text(), nullable=True),
        sa.Column("score", sa.Integer(), nullable=False, server_default="0"),
        sa.Column("max_score", sa.Integer(), nullable=False, server_default="0"),
        sa.Column("feedback_json", sa.JSON(), nullable=False, server_default=sa.text("'{}'::json")),
        sa.Column("mistake_tags", sa.JSON(), nullable=False, server_default=sa.text("'[]'::json")),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
    )
    op.create_index("ix_attempts_user_id", "attempts", ["user_id"])
    op.create_index("ix_attempts_question_id", "attempts", ["question_id"])

    op.create_table(
        "mastery",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("user_id", sa.Integer(), sa.ForeignKey("users.id", ondelete="CASCADE"), nullable=False),
        sa.Column("topic_id", sa.Integer(), sa.ForeignKey("topics.id", ondelete="CASCADE"), nullable=False),
        sa.Column("mastery_score", sa.Float(), nullable=False, server_default="0"),
        sa.Column("last_practiced_at", sa.DateTime(timezone=True), nullable=True),
        sa.UniqueConstraint("user_id", "topic_id", name="uq_mastery_user_topic"),
    )
    op.create_index("ix_mastery_user_id", "mastery", ["user_id"])
    op.create_index("ix_mastery_topic_id", "mastery", ["topic_id"])

    op.create_table(
        "quickwins_queue",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("user_id", sa.Integer(), sa.ForeignKey("users.id", ondelete="CASCADE"), nullable=False),
        sa.Column("topic_id", sa.Integer(), sa.ForeignKey("topics.id", ondelete="CASCADE"), nullable=True),
        sa.Column("question_id", sa.Integer(), sa.ForeignKey("questions.id", ondelete="CASCADE"), nullable=True),
        sa.Column("next_due_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column("interval_days", sa.Integer(), nullable=False, server_default="1"),
        sa.Column("ease_factor", sa.Float(), nullable=False, server_default="2.5"),
    )
    op.create_index("ix_quickwins_queue_user_id", "quickwins_queue", ["user_id"])

    op.create_table(
        "projects",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("subject_id", sa.Integer(), sa.ForeignKey("subjects.id", ondelete="CASCADE"), nullable=False),
        sa.Column("unit", sa.Integer(), nullable=False),
        sa.Column("title", sa.String(length=255), nullable=False),
        sa.Column("brief_md", sa.Text(), nullable=False),
        sa.Column("rubric_json", sa.JSON(), nullable=False, server_default=sa.text("'{}'::json")),
    )
    op.create_index("ix_projects_subject_id", "projects", ["subject_id"])
    op.create_index("ix_projects_unit", "projects", ["unit"])

    op.create_table(
        "project_submissions",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("project_id", sa.Integer(), sa.ForeignKey("projects.id", ondelete="CASCADE"), nullable=False),
        sa.Column("user_id", sa.Integer(), sa.ForeignKey("users.id", ondelete="CASCADE"), nullable=False),
        sa.Column("submission_type", sa.String(length=20), nullable=False),
        sa.Column("content_ref", sa.Text(), nullable=False),
        sa.Column("reflection_md", sa.Text(), nullable=True),
        sa.Column("feedback_json", sa.JSON(), nullable=False, server_default=sa.text("'{}'::json")),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
    )
    op.create_index("ix_project_submissions_project_id", "project_submissions", ["project_id"])
    op.create_index("ix_project_submissions_user_id", "project_submissions", ["user_id"])

    op.create_table(
        "sat_projects",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("user_id", sa.Integer(), sa.ForeignKey("users.id", ondelete="CASCADE"), nullable=False),
        sa.Column("subject_id", sa.Integer(), sa.ForeignKey("subjects.id", ondelete="CASCADE"), nullable=False),
        sa.Column("title", sa.String(length=255), nullable=False),
        sa.Column("context_md", sa.Text(), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
    )
    op.create_index("ix_sat_projects_user_id", "sat_projects", ["user_id"])
    op.create_index("ix_sat_projects_subject_id", "sat_projects", ["subject_id"])

    op.create_table(
        "sat_milestones",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column(
            "sat_project_id", sa.Integer(), sa.ForeignKey("sat_projects.id", ondelete="CASCADE"), nullable=False
        ),
        sa.Column("part", sa.Integer(), nullable=False),
        sa.Column("checklist_json", sa.JSON(), nullable=False, server_default=sa.text("'{}'::json")),
        sa.Column("status_json", sa.JSON(), nullable=False, server_default=sa.text("'{}'::json")),
        sa.Column("due_dates_json", sa.JSON(), nullable=False, server_default=sa.text("'{}'::json")),
    )
    op.create_index("ix_sat_milestones_sat_project_id", "sat_milestones", ["sat_project_id"])

    op.create_table(
        "evidence_logs",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column(
            "sat_project_id", sa.Integer(), sa.ForeignKey("sat_projects.id", ondelete="CASCADE"), nullable=False
        ),
        sa.Column("entry_type", sa.String(length=30), nullable=False),
        sa.Column("content_md", sa.Text(), nullable=False),
        sa.Column("attachment_refs_json", sa.JSON(), nullable=False, server_default=sa.text("'{}'::json")),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
    )
    op.create_index("ix_evidence_logs_sat_project_id", "evidence_logs", ["sat_project_id"])

    op.create_table(
        "code_snapshots",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("user_id", sa.Integer(), sa.ForeignKey("users.id", ondelete="CASCADE"), nullable=False),
        sa.Column("filename", sa.String(length=255), nullable=False),
        sa.Column("content", sa.Text(), nullable=False),
        sa.Column("metadata_json", sa.JSON(), nullable=False, server_default=sa.text("'{}'::json")),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
    )
    op.create_index("ix_code_snapshots_user_id", "code_snapshots", ["user_id"])


def downgrade() -> None:
    op.drop_index("ix_code_snapshots_user_id", table_name="code_snapshots")
    op.drop_table("code_snapshots")
    op.drop_index("ix_evidence_logs_sat_project_id", table_name="evidence_logs")
    op.drop_table("evidence_logs")
    op.drop_index("ix_sat_milestones_sat_project_id", table_name="sat_milestones")
    op.drop_table("sat_milestones")
    op.drop_index("ix_sat_projects_subject_id", table_name="sat_projects")
    op.drop_index("ix_sat_projects_user_id", table_name="sat_projects")
    op.drop_table("sat_projects")
    op.drop_index("ix_project_submissions_user_id", table_name="project_submissions")
    op.drop_index("ix_project_submissions_project_id", table_name="project_submissions")
    op.drop_table("project_submissions")
    op.drop_index("ix_projects_unit", table_name="projects")
    op.drop_index("ix_projects_subject_id", table_name="projects")
    op.drop_table("projects")
    op.drop_index("ix_quickwins_queue_user_id", table_name="quickwins_queue")
    op.drop_table("quickwins_queue")
    op.drop_index("ix_mastery_topic_id", table_name="mastery")
    op.drop_index("ix_mastery_user_id", table_name="mastery")
    op.drop_table("mastery")
    op.drop_index("ix_attempts_question_id", table_name="attempts")
    op.drop_index("ix_attempts_user_id", table_name="attempts")
    op.drop_table("attempts")
    op.drop_index("ix_questions_exam_style", table_name="questions")
    op.drop_index("ix_questions_type", table_name="questions")
    op.drop_index("ix_questions_topic_id", table_name="questions")
    op.drop_table("questions")
    op.drop_index("ix_data_chart_configs_user_id", table_name="data_chart_configs")
    op.drop_index("ix_data_chart_configs_dataset_id", table_name="data_chart_configs")
    op.drop_table("data_chart_configs")
    op.drop_table("dataset_assets")
    op.drop_index("ix_lessons_topic_id", table_name="lessons")
    op.drop_table("lessons")
    op.drop_index("ix_topics_unit", table_name="topics")
    op.drop_index("ix_topics_subject_id", table_name="topics")
    op.drop_table("topics")
    op.drop_index("ix_subjects_code", table_name="subjects")
    op.drop_table("subjects")
    op.drop_index("ix_password_reset_tokens_token", table_name="password_reset_tokens")
    op.drop_index("ix_password_reset_tokens_user_id", table_name="password_reset_tokens")
    op.drop_table("password_reset_tokens")
    op.drop_index("ix_users_email", table_name="users")
    op.drop_table("users")
