"""
Outbreak alert service for real-time health alerts
"""

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from app.database import OutbreakAlert
from typing import List, Dict, Optional
from datetime import datetime, timedelta
import asyncio
import httpx

class AlertService:
    def __init__(self, db_session: Optional[AsyncSession] = None):
        self.db_session = db_session
        self.monitoring_active = False
    
    async def get_active_alerts(self, region: Optional[str] = None) -> List[Dict]:
        """Get active outbreak alerts"""
        if not self.db_session:
            from app.database import AsyncSessionLocal
            async with AsyncSessionLocal() as session:
                return await self._fetch_alerts(session, region)
        return await self._fetch_alerts(self.db_session, region)
    
    async def _fetch_alerts(self, session: AsyncSession, region: Optional[str] = None) -> List[Dict]:
        """Fetch alerts from database"""
        stmt = select(OutbreakAlert).where(OutbreakAlert.is_active == True)
        if region:
            stmt = stmt.where(OutbreakAlert.region.ilike(f"%{region}%"))
        
        result = await session.execute(stmt)
        alerts = result.scalars().all()
        
        return [{
            "id": alert.id,
            "disease_name": alert.disease_name,
            "region": alert.region,
            "severity": alert.severity,
            "description": alert.description,
            "recommendations": alert.recommendations or [],
            "created_at": alert.created_at.isoformat() if alert.created_at else None
        } for alert in alerts]
    
    async def create_alert(
        self,
        disease_name: str,
        region: str,
        severity: str,
        description: str,
        recommendations: List[str]
    ) -> Dict:
        """Create a new outbreak alert"""
        if not self.db_session:
            from app.database import AsyncSessionLocal
            async with AsyncSessionLocal() as session:
                return await self._create_alert_in_db(
                    session, disease_name, region, severity, description, recommendations
                )
        return await self._create_alert_in_db(
            self.db_session, disease_name, region, severity, description, recommendations
        )
    
    async def _create_alert_in_db(
        self,
        session: AsyncSession,
        disease_name: str,
        region: str,
        severity: str,
        description: str,
        recommendations: List[str]
    ) -> Dict:
        """Create alert in database"""
        alert = OutbreakAlert(
            disease_name=disease_name,
            region=region,
            severity=severity,
            description=description,
            recommendations=recommendations,
            is_active=True
        )
        session.add(alert)
        await session.commit()
        await session.refresh(alert)
        
        return {
            "id": alert.id,
            "disease_name": alert.disease_name,
            "region": alert.region,
            "severity": alert.severity,
            "description": alert.description,
            "recommendations": alert.recommendations,
            "created_at": alert.created_at.isoformat() if alert.created_at else None
        }
    
    async def fetch_government_alerts(self) -> List[Dict]:
        """Fetch alerts from local database (offline mode)"""
        # Offline mode - alerts are stored locally in database
        # No internet connection required
        # Alerts can be manually added via the API or initialized in the database
        return []  # Return empty list - alerts are managed locally via database
    
    async def start_monitoring(self):
        """Start monitoring for new alerts (runs indefinitely)"""
        if self.monitoring_active:
            return
        
        self.monitoring_active = True
        print("Alert monitoring service started")
        
        while self.monitoring_active:
            try:
                # Fetch alerts from government database
                government_alerts = await self.fetch_government_alerts()
                
                # Process and store new alerts
                if government_alerts:
                    from app.database import AsyncSessionLocal
                    async with AsyncSessionLocal() as session:
                        for alert_data in government_alerts:
                            # Check if alert already exists
                            stmt = select(OutbreakAlert).where(
                                OutbreakAlert.disease_name == alert_data["disease_name"],
                                OutbreakAlert.region == alert_data["region"],
                                OutbreakAlert.is_active == True
                            )
                            result = await session.execute(stmt)
                            existing = result.scalar_one_or_none()
                            
                            if not existing:
                                await self._create_alert_in_db(
                                    session,
                                    alert_data["disease_name"],
                                    alert_data["region"],
                                    alert_data["severity"],
                                    alert_data["description"],
                                    alert_data.get("recommendations", [])
                                )
                                await session.commit()
                                print(f"New alert created: {alert_data['disease_name']} in {alert_data['region']}")
                
                # Check every hour
                await asyncio.sleep(3600)
            except Exception as e:
                print(f"Error in alert monitoring: {e}")
                await asyncio.sleep(3600)

