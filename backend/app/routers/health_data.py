"""
Health data API endpoints
"""

from fastapi import APIRouter, HTTPException, Depends
from pydantic import BaseModel
from typing import List, Optional
from sqlalchemy.ext.asyncio import AsyncSession
from app.database import get_db
from app.models.health_data import HealthDataService

router = APIRouter()

@router.get("/vaccination")
async def get_vaccination_info(
    query: str,
    language: str = "en",
    db: AsyncSession = Depends(get_db)
):
    """Get vaccination information"""
    try:
        service = HealthDataService(db)
        info = await service.get_vaccination_info(query, language)
        return {"vaccination_info": info}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/disease")
async def get_disease_info(
    query: str,
    language: str = "en",
    db: AsyncSession = Depends(get_db)
):
    """Get disease information"""
    try:
        service = HealthDataService(db)
        info = await service.get_disease_info(query, language)
        return {"disease_info": info}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/symptoms")
async def get_symptom_info(
    query: str,
    language: str = "en",
    db: AsyncSession = Depends(get_db)
):
    """Get symptom information"""
    try:
        service = HealthDataService(db)
        info = await service.get_symptom_info(query, language)
        return {"symptom_info": info}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

