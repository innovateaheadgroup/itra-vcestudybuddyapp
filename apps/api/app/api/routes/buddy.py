from fastapi import APIRouter

from app.schemas import BuddyChatRequest, BuddyChatResponse
from app.services.buddy import get_buddy_provider

router = APIRouter(prefix="/buddy", tags=["buddy"])


@router.post("/chat", response_model=BuddyChatResponse)
def buddy_chat(payload: BuddyChatRequest) -> BuddyChatResponse:
    provider = get_buddy_provider()
    return provider.coach(payload)
