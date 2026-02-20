from datetime import datetime
from typing import Any, Literal

from pydantic import BaseModel, ConfigDict, EmailStr, Field


class UserOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    email: EmailStr
    role: str
    created_at: datetime


class AuthTokenPair(BaseModel):
    access_token: str
    refresh_token: str
    token_type: str = "bearer"


class RegisterRequest(BaseModel):
    email: EmailStr
    password: str = Field(min_length=8)
    role: Literal["student", "admin", "tutor"] = "student"


class LoginRequest(BaseModel):
    email: EmailStr
    password: str


class RefreshRequest(BaseModel):
    refresh_token: str


class PasswordResetRequest(BaseModel):
    email: EmailStr


class PasswordResetConfirmRequest(BaseModel):
    token: str
    new_password: str = Field(min_length=8)


class LessonOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    topic_id: int
    title: str
    content_md: str
    estimated_minutes: int


class TopicOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    subject_id: int
    unit: int
    aos: str
    outcome: str
    title: str
    order: int
    key_skills_json: dict[str, Any]


class TopicCardOut(BaseModel):
    topic: TopicOut
    mastery_pct: int
    status: Literal["Not started", "Learning", "Practising", "Ready"]
    estimated_time: int


class QuestionOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    topic_id: int
    type: str
    exam_style: str
    command_terms: list[str]
    marks: int
    difficulty: int
    prompt_md: str
    case_material_md: str | None = None
    options_json: dict[str, Any] | None = None
    starter_code: str | None = None
    dataset_id: int | None = None


class FeedbackCriterion(BaseModel):
    name: str
    score: int
    max: int
    notes: list[str]


class DrillRecommendation(BaseModel):
    topic_id: int
    count: int


class FeedbackObject(BaseModel):
    score: int
    max_score: int
    criteria: list[FeedbackCriterion]
    missing: list[str]
    next_steps: list[str]
    drills: list[DrillRecommendation]
    mistake_tags: list[str]
    integrity_mode: Literal["foundation", "scored"]


class SetBuilderRequest(BaseModel):
    number_of_questions: int = Field(default=10, ge=1, le=50)
    time_target_minutes: int = Field(default=30, ge=5, le=180)
    mixed_topics: bool = True
    unit: int | None = Field(default=None, ge=1, le=4)
    topic_ids: list[int] = Field(default_factory=list)
    difficulty: int | None = Field(default=None, ge=1, le=5)
    question_types: list[str] = Field(default_factory=list)
    exam_styles: list[str] = Field(default_factory=list)
    subject_code: str | None = None


class PracticeSetResponse(BaseModel):
    questions: list[QuestionOut]
    estimated_minutes: int


class AttemptSubmitRequest(BaseModel):
    question_id: int
    answer_text: str | None = None
    code_snapshot: str | None = None
    integrity_mode: Literal["foundation", "scored"] = "foundation"
    track: Literal["foundation", "scored"] = "foundation"
    unit: int = Field(ge=1, le=4)
    is_sat_assessment: bool = False


class MarkResponse(BaseModel):
    feedback: FeedbackObject
    where_marks_were_lost: list[str]
    common_mistakes: list[str]
    upgrade_response: dict[str, Any]


class BuddyChatRequest(BaseModel):
    prompt: str
    unit: int = Field(ge=1, le=4)
    track: Literal["foundation", "scored"]
    integrity_mode: Literal["foundation", "scored"] = "foundation"
    question_context: str | None = None
    marks: int | None = None


class BuddyChatResponse(BaseModel):
    quick_diagnosis: str
    what_to_fix_first: list[str]
    hints: list[str]
    mini_drill: str
    checklist_aligned_to_marks: list[str]
    feedback: FeedbackObject


class CodeRunRequest(BaseModel):
    code: str
    tests_public: str | None = None
    language: Literal["python"] = "python"


class CodeRunResponse(BaseModel):
    passed: bool
    output: str
    failed_test: str | None = None


class CodeSnapshotCreate(BaseModel):
    filename: str
    content: str
    metadata_json: dict[str, Any] = Field(default_factory=dict)


class CodeSnapshotOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    user_id: int
    filename: str
    content: str
    metadata_json: dict[str, Any]
    created_at: datetime


class DataLabUploadOut(BaseModel):
    dataset_id: int
    filename: str
    columns: dict[str, str]
    preview_rows: list[dict[str, Any]]
    cleaning_suggestions: list[str]


class DataLabChartConfigCreate(BaseModel):
    dataset_id: int
    config_json: dict[str, Any]


class QuickWinsSessionRequest(BaseModel):
    minutes: Literal[5, 10, 15]


class QuickWinsItemOut(BaseModel):
    id: int
    topic_id: int | None = None
    question_id: int | None = None
    next_due_at: datetime
    interval_days: int
    ease_factor: float


class QuickWinsSessionOut(BaseModel):
    items: list[QuickWinsItemOut]
    streak: int
    mastery_trend: list[float]


class QuickWinsReviewRequest(BaseModel):
    queue_item_id: int
    correct: bool


class SATProjectCreate(BaseModel):
    subject_id: int
    title: str
    context_md: str


class SATProjectOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    user_id: int
    subject_id: int
    title: str
    context_md: str
    created_at: datetime


class SATMilestoneOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    sat_project_id: int
    part: int
    checklist_json: dict[str, Any]
    status_json: dict[str, Any]
    due_dates_json: dict[str, Any]


class EvidenceLogCreate(BaseModel):
    sat_project_id: int
    entry_type: Literal["decision", "test", "feedback", "reflection"]
    content_md: str
    attachment_refs_json: dict[str, Any] = Field(default_factory=dict)


class EvidenceLogOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    sat_project_id: int
    entry_type: str
    content_md: str
    attachment_refs_json: dict[str, Any]
    created_at: datetime


class ProjectOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    subject_id: int
    unit: int
    title: str
    brief_md: str
    rubric_json: dict[str, Any]


class ProjectSubmissionCreate(BaseModel):
    project_id: int
    submission_type: Literal["code", "report", "data"]
    content_ref: str
    reflection_md: str | None = None


class ProjectSubmissionOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    project_id: int
    user_id: int
    submission_type: str
    content_ref: str
    reflection_md: str | None
    feedback_json: dict[str, Any]
    created_at: datetime


class ExamTemplate(BaseModel):
    id: str
    title: str
    structure: list[str]
    example: str


class CommandTermGuide(BaseModel):
    term: str
    definition: str
    checklist: list[str]
    example: str
