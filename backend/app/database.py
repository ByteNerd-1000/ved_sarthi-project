"""
Database configuration and initialization
"""

from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession, async_sessionmaker
from sqlalchemy.orm import declarative_base
from sqlalchemy import Column, Integer, String, Text, DateTime, JSON, Boolean
from datetime import datetime
import os

# Database URL (using SQLite for simplicity, can be upgraded to PostgreSQL)
DATABASE_URL = os.getenv("DATABASE_URL", "sqlite+aiosqlite:///./healthcare_chatbot.db")

engine = create_async_engine(DATABASE_URL, echo=True)
AsyncSessionLocal = async_sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)
Base = declarative_base()

# Database Models
class ChatHistory(Base):
    __tablename__ = "chat_history"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(String, index=True)
    message = Column(Text)
    response = Column(Text)
    language = Column(String, default="en")
    timestamp = Column(DateTime, default=datetime.utcnow)
    accuracy_score = Column(Integer, nullable=True)

class OutbreakAlert(Base):
    __tablename__ = "outbreak_alerts"
    
    id = Column(Integer, primary_key=True, index=True)
    disease_name = Column(String, index=True)
    region = Column(String)
    severity = Column(String)  # low, medium, high, critical
    description = Column(Text)
    recommendations = Column(JSON)
    created_at = Column(DateTime, default=datetime.utcnow)
    is_active = Column(Boolean, default=True)

class VaccinationSchedule(Base):
    __tablename__ = "vaccination_schedules"
    
    id = Column(Integer, primary_key=True, index=True)
    age_group = Column(String)
    vaccine_name = Column(String)
    dose_number = Column(Integer)
    description = Column(Text)
    country = Column(String, default="IN")  # Default to India
    language = Column(String, default="en")

class DiseaseSymptom(Base):
    __tablename__ = "disease_symptoms"
    
    id = Column(Integer, primary_key=True, index=True)
    disease_name = Column(String, index=True)
    symptoms = Column(JSON)  # List of symptoms
    prevention = Column(JSON)  # List of preventive measures
    treatment = Column(Text)
    severity = Column(String)
    language = Column(String, default="en")

class EvaluationQuestion(Base):
    __tablename__ = "evaluation_questions"
    
    id = Column(Integer, primary_key=True, index=True)
    question = Column(Text)
    expected_answer_keywords = Column(JSON)
    category = Column(String)  # preventive, symptoms, vaccination, general
    language = Column(String, default="en")

async def init_db():
    """Initialize database tables"""
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

async def initialize_sample_data():
    """Initialize database with sample healthcare data"""
    from app.database import AsyncSessionLocal
    from app.models.health_data import HealthDataService
    
    async with AsyncSessionLocal() as session:
        service = HealthDataService(session)
        await service.initialize_sample_data()
        await session.commit()

async def get_db():
    """Dependency for getting database session"""
    async with AsyncSessionLocal() as session:
        try:
            yield session
        finally:
            await session.close()

