"""
Chatbot API endpoints
"""

from fastapi import APIRouter, HTTPException, Depends
from pydantic import BaseModel
from typing import Optional, List
from sqlalchemy.ext.asyncio import AsyncSession
from app.database import get_db, ChatHistory
from app.models.chatbot import ChatbotService
from datetime import datetime

router = APIRouter()

class ChatRequest(BaseModel):
    message: str
    user_id: str = "anonymous"
    language: str = "en"

class ChatResponse(BaseModel):
    response: str
    language: str
    accuracy_score: Optional[int] = None
    sources: List[str] = []
    alerts: List[dict] = []

@router.post("/chat", response_model=ChatResponse)
async def chat(
    request: ChatRequest,
    db: AsyncSession = Depends(get_db)
):
    """Process user message and generate response"""
    try:
        chatbot_service = ChatbotService(db)
        result = await chatbot_service.process_message(
            message=request.message,
            user_id=request.user_id,
            language=request.language
        )
        
        # Save to chat history
        chat_history = ChatHistory(
            user_id=request.user_id,
            message=request.message,
            response=result["response"],
            language=result["language"],
            accuracy_score=result.get("accuracy_score")
        )
        db.add(chat_history)
        await db.commit()
        
        return ChatResponse(**result)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/history/{user_id}")
async def get_chat_history(
    user_id: str,
    limit: int = 50,
    db: AsyncSession = Depends(get_db)
):
    """Get chat history for a user"""
    from sqlalchemy import select
    from sqlalchemy import desc
    
    stmt = select(ChatHistory).where(
        ChatHistory.user_id == user_id
    ).order_by(desc(ChatHistory.timestamp)).limit(limit)
    
    result = await db.execute(stmt)
    history = result.scalars().all()
    
    return [{
        "id": h.id,
        "message": h.message,
        "response": h.response,
        "language": h.language,
        "timestamp": h.timestamp.isoformat() if h.timestamp else None,
        "accuracy_score": h.accuracy_score
    } for h in history]

@router.get("/languages")
async def get_supported_languages():
    """Get list of supported languages"""
    from app.services.translation import TranslationService
    service = TranslationService()
    return service.get_supported_languages()

