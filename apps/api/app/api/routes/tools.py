from __future__ import annotations

from pathlib import Path
from typing import Any

import pandas as pd
from fastapi import APIRouter, Depends, File, HTTPException, UploadFile
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.api.deps import get_current_user
from app.core.config import get_settings
from app.core.database import get_db
from app.core.rate_limit import InMemoryRateLimiter
from app.models.models import CodeSnapshot, DataChartConfig, DatasetAsset, User
from app.schemas import (
    CodeRunRequest,
    CodeRunResponse,
    CodeSnapshotCreate,
    CodeSnapshotOut,
    DataLabChartConfigCreate,
    DataLabUploadOut,
)
from app.services.code_runner import run_python_tests

router = APIRouter(prefix="/tools", tags=["tools"])
settings = get_settings()
code_limiter = InMemoryRateLimiter(max_requests=settings.code_run_rate_limit_per_minute)
BASE_DIR = Path(__file__).resolve().parents[3]
UPLOAD_DIR = BASE_DIR / "uploads"
UPLOAD_DIR.mkdir(parents=True, exist_ok=True)


@router.post("/code-lab/run", response_model=CodeRunResponse)
def run_code(
    payload: CodeRunRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> CodeRunResponse:
    code_limiter.check(f"{current_user.id}:code-run")
    result = run_python_tests(payload.code, payload.tests_public, timeout_seconds=settings.code_run_timeout_seconds)
    return CodeRunResponse(passed=result.passed, output=result.output, failed_test=result.failed_test)


@router.post("/code-lab/snapshots", response_model=CodeSnapshotOut)
def create_snapshot(
    payload: CodeSnapshotCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> CodeSnapshotOut:
    snapshot = CodeSnapshot(
        user_id=current_user.id,
        filename=payload.filename,
        content=payload.content,
        metadata_json=payload.metadata_json,
    )
    db.add(snapshot)
    db.commit()
    db.refresh(snapshot)
    return CodeSnapshotOut.model_validate(snapshot)


@router.get("/code-lab/snapshots", response_model=list[CodeSnapshotOut])
def list_snapshots(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> list[CodeSnapshotOut]:
    snapshots = db.scalars(
        select(CodeSnapshot).where(CodeSnapshot.user_id == current_user.id).order_by(CodeSnapshot.created_at.desc())
    ).all()
    return [CodeSnapshotOut.model_validate(s) for s in snapshots]


def _cleaning_suggestions(df: pd.DataFrame) -> list[str]:
    suggestions: list[str] = []
    missing = df.isna().sum()
    for col, count in missing.items():
        if count > 0:
            suggestions.append(f"Column '{col}' has {int(count)} missing values.")
    numeric_cols = df.select_dtypes(include=["number"]).columns
    for col in numeric_cols:
        series = df[col].dropna()
        if len(series) < 4:
            continue
        q1, q3 = series.quantile(0.25), series.quantile(0.75)
        iqr = q3 - q1
        if iqr == 0:
            continue
        outliers = series[(series < q1 - 1.5 * iqr) | (series > q3 + 1.5 * iqr)]
        if len(outliers) > 0:
            suggestions.append(f"Column '{col}' has potential outliers ({len(outliers)} rows).")
    if not suggestions:
        suggestions.append("No obvious cleaning issues detected. Validate domain rules manually.")
    return suggestions


@router.post("/data-lab/upload", response_model=DataLabUploadOut)
async def upload_csv(
    file: UploadFile = File(...),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> DataLabUploadOut:
    contents = await file.read()
    size_mb = len(contents) / (1024 * 1024)
    if size_mb > settings.max_upload_size_mb:
        raise HTTPException(status_code=400, detail=f"Upload exceeds {settings.max_upload_size_mb} MB limit.")

    filename = file.filename or "dataset.csv"
    storage_ref = UPLOAD_DIR / f"{current_user.id}_{filename}"
    storage_ref.write_bytes(contents)

    try:
        df = pd.read_csv(storage_ref)
    except Exception as exc:
        raise HTTPException(status_code=400, detail="Invalid CSV file") from exc

    columns = {name: str(dtype) for name, dtype in df.dtypes.items()}
    preview_rows = df.head(10).fillna("").to_dict(orient="records")
    suggestions = _cleaning_suggestions(df)

    dataset = DatasetAsset(
        user_id=current_user.id,
        filename=filename,
        storage_ref=str(storage_ref),
        columns_json=columns,
    )
    db.add(dataset)
    db.commit()
    db.refresh(dataset)

    return DataLabUploadOut(
        dataset_id=dataset.id,
        filename=filename,
        columns=columns,
        preview_rows=preview_rows,
        cleaning_suggestions=suggestions,
    )


@router.post("/data-lab/chart-config")
def save_chart_config(
    payload: DataLabChartConfigCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> dict[str, Any]:
    dataset = db.scalar(
        select(DatasetAsset).where(DatasetAsset.id == payload.dataset_id, DatasetAsset.user_id == current_user.id)
    )
    if not dataset:
        raise HTTPException(status_code=404, detail="Dataset not found")

    chart = DataChartConfig(dataset_id=dataset.id, user_id=current_user.id, config_json=payload.config_json)
    db.add(chart)
    db.commit()
    db.refresh(chart)
    return {"id": chart.id, "dataset_id": chart.dataset_id, "config_json": chart.config_json}


@router.get("/data-lab/insight-templates")
def insight_templates() -> dict:
    return {
        "templates": [
            {
                "name": "Claim->Evidence->Explanation->Limitation",
                "structure": [
                    "Claim: State the main trend or finding.",
                    "Evidence: Cite values/calculations.",
                    "Explanation: Explain business/user implication.",
                    "Limitation: Note caveat or uncertainty.",
                ],
            }
        ]
    }
