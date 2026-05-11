"""
Alerts API endpoints
"""

from fastapi import APIRouter, HTTPException, Depends
from pydantic import BaseModel
from typing import List, Optional
from sqlalchemy.ext.asyncio import AsyncSession
from app.database import get_db
from app.models.alert import AlertService

router = APIRouter()

class CreateAlertRequest(BaseModel):
    disease_name: str
    region: str
    severity: str
    description: str
    recommendations: List[str]

@router.get("/active")
async def get_active_alerts(
    region: Optional[str] = None,
    db: AsyncSession = Depends(get_db)
):
    """Get active outbreak alerts"""
    try:
        alert_service = AlertService(db)
        alerts = await alert_service.get_active_alerts(region)
        return {"alerts": alerts}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/create")
async def create_alert(
    request: CreateAlertRequest,
    db: AsyncSession = Depends(get_db)
):
    """Create a new outbreak alert"""
    try:
        alert_service = AlertService(db)
        alert = await alert_service.create_alert(
            disease_name=request.disease_name,
            region=request.region,
            severity=request.severity,
            description=request.description,
            recommendations=request.recommendations
        )
        return alert
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/regions")
async def get_alert_regions(db: AsyncSession = Depends(get_db)):
    """Get list of regions with active alerts"""
    from sqlalchemy import select, distinct
    from app.database import OutbreakAlert
    
    stmt = select(distinct(OutbreakAlert.region)).where(
        OutbreakAlert.is_active == True
    )
    result = await db.execute(stmt)
    regions = result.scalars().all()
    return {"regions": regions}

