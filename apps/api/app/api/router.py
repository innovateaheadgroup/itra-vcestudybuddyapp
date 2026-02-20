from fastapi import APIRouter

from app.api.routes import (
    auth,
    buddy,
    curriculum,
    dashboard,
    exam_skills,
    mark,
    practice,
    profile,
    projects,
    quickwins,
    sat,
    tools,
)

api_router = APIRouter(prefix="/api")
api_router.include_router(auth.router)
api_router.include_router(dashboard.router)
api_router.include_router(curriculum.router)
api_router.include_router(practice.router)
api_router.include_router(mark.router)
api_router.include_router(exam_skills.router)
api_router.include_router(buddy.router)
api_router.include_router(tools.router)
api_router.include_router(quickwins.router)
api_router.include_router(sat.router)
api_router.include_router(projects.router)
api_router.include_router(profile.router)
