"""
Evaluation API endpoints for measuring chatbot accuracy
"""

from fastapi import APIRouter, HTTPException, Depends
from pydantic import BaseModel
from typing import List, Optional, Dict
from sqlalchemy.ext.asyncio import AsyncSession
from app.database import get_db, ChatHistory, EvaluationQuestion
from app.models.chatbot import ChatbotService
from sqlalchemy import select, func
from datetime import datetime, timedelta

router = APIRouter()

class EvaluationRequest(BaseModel):
    question: str
    expected_answer_keywords: List[str]
    category: str
    language: str = "en"

class EvaluationResult(BaseModel):
    question: str
    response: str
    accuracy_score: int
    keywords_matched: List[str]
    keywords_missing: List[str]

@router.post("/evaluate")
async def evaluate_response(
    request: EvaluationRequest,
    db: AsyncSession = Depends(get_db)
):
    """Evaluate a single question-answer pair"""
    try:
        chatbot_service = ChatbotService(db)
        result = await chatbot_service.process_message(
            message=request.question,
            user_id="evaluation",
            language=request.language
        )
        
        response = result["response"].lower()
        expected_keywords = [kw.lower() for kw in request.expected_answer_keywords]
        
        # Check which keywords are present
        keywords_matched = [kw for kw in expected_keywords if kw in response]
        keywords_missing = [kw for kw in expected_keywords if kw not in response]
        
        # Calculate accuracy based on keyword matching
        accuracy_score = int((len(keywords_matched) / len(expected_keywords)) * 100) if expected_keywords else 0
        
        # Save evaluation question
        eval_question = EvaluationQuestion(
            question=request.question,
            expected_answer_keywords=request.expected_answer_keywords,
            category=request.category,
            language=request.language
        )
        db.add(eval_question)
        await db.commit()
        
        return EvaluationResult(
            question=request.question,
            response=result["response"],
            accuracy_score=accuracy_score,
            keywords_matched=keywords_matched,
            keywords_missing=keywords_missing
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/accuracy")
async def get_accuracy_stats(
    days: int = 30,
    db: AsyncSession = Depends(get_db)
):
    """Get overall accuracy statistics"""
    try:
        # Calculate date range
        start_date = datetime.utcnow() - timedelta(days=days)
        
        # Get all chat history with accuracy scores
        stmt = select(ChatHistory).where(
            ChatHistory.accuracy_score.isnot(None),
            ChatHistory.timestamp >= start_date
        )
        result = await db.execute(stmt)
        history = result.scalars().all()
        
        if not history:
            return {
                "overall_accuracy": 0,
                "total_evaluations": 0,
                "average_accuracy": 0,
                "accuracy_by_category": {}
            }
        
        # Calculate statistics
        accuracy_scores = [h.accuracy_score for h in history if h.accuracy_score is not None]
        average_accuracy = sum(accuracy_scores) / len(accuracy_scores) if accuracy_scores else 0
        
        # Count responses meeting 80% threshold
        above_threshold = sum(1 for score in accuracy_scores if score >= 80)
        overall_accuracy = (above_threshold / len(accuracy_scores) * 100) if accuracy_scores else 0
        
        return {
            "overall_accuracy": round(overall_accuracy, 2),
            "total_evaluations": len(accuracy_scores),
            "average_accuracy": round(average_accuracy, 2),
            "responses_above_80_percent": above_threshold,
            "target_met": overall_accuracy >= 80
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/batch-evaluate")
async def batch_evaluate(
    questions: List[EvaluationRequest],
    db: AsyncSession = Depends(get_db)
):
    """Evaluate multiple questions in batch"""
    try:
        results = []
        chatbot_service = ChatbotService(db)
        
        for req in questions:
            result = await chatbot_service.process_message(
                message=req.question,
                user_id="batch_evaluation",
                language=req.language
            )
            
            response = result["response"].lower()
            expected_keywords = [kw.lower() for kw in req.expected_answer_keywords]
            
            keywords_matched = [kw for kw in expected_keywords if kw in response]
            keywords_missing = [kw for kw in expected_keywords if kw not in response]
            
            accuracy_score = int((len(keywords_matched) / len(expected_keywords)) * 100) if expected_keywords else 0
            
            results.append({
                "question": req.question,
                "response": result["response"],
                "accuracy_score": accuracy_score,
                "keywords_matched": keywords_matched,
                "keywords_missing": keywords_missing,
                "category": req.category
            })
        
        # Calculate overall accuracy
        if results:
            avg_accuracy = sum(r["accuracy_score"] for r in results) / len(results)
            above_80 = sum(1 for r in results if r["accuracy_score"] >= 80)
            overall_percentage = (above_80 / len(results)) * 100
        else:
            avg_accuracy = 0
            overall_percentage = 0
        
        return {
            "results": results,
            "average_accuracy": round(avg_accuracy, 2),
            "overall_accuracy_percentage": round(overall_percentage, 2),
            "target_met": overall_percentage >= 80
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/test-questions")
async def get_test_questions(db: AsyncSession = Depends(get_db)):
    """Get standard test questions for evaluation"""
    # Standard test questions for evaluation
    test_questions = [
        {
            "question": "What are the symptoms of dengue?",
            "expected_answer_keywords": ["fever", "headache", "mosquito", "symptom"],
            "category": "symptoms",
            "language": "en"
        },
        {
            "question": "When should I get vaccinated?",
            "expected_answer_keywords": ["vaccine", "schedule", "age", "dose"],
            "category": "vaccination",
            "language": "en"
        },
        {
            "question": "How can I prevent malaria?",
            "expected_answer_keywords": ["mosquito", "net", "prevent", "repellent"],
            "category": "preventive",
            "language": "en"
        },
        {
            "question": "What is the treatment for typhoid?",
            "expected_answer_keywords": ["antibiotic", "treatment", "doctor", "medical"],
            "category": "treatment",
            "language": "en"
        },
        {
            "question": "What vaccines are recommended for infants?",
            "expected_answer_keywords": ["BCG", "DPT", "vaccine", "infant"],
            "category": "vaccination",
            "language": "en"
        }
    ]
    
    return {"test_questions": test_questions}

