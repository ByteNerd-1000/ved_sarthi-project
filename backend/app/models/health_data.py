"""
Health data service for managing vaccination schedules, disease symptoms, etc.
"""

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from app.database import VaccinationSchedule, DiseaseSymptom
from typing import List, Dict, Optional
import json

class HealthDataService:
    def __init__(self, db_session: AsyncSession):
        self.db_session = db_session
    
    async def get_vaccination_info(self, query: str, language: str = "en") -> List[Dict]:
        """Get vaccination information based on query"""
        query_lower = query.lower()
        
        # Search for age-related queries
        age_groups = ["infant", "child", "adult", "baby", "newborn", "teen", "adolescent"]
        age_filter = None
        for age in age_groups:
            if age in query_lower:
                age_filter = age
                break
        
        # Build query
        stmt = select(VaccinationSchedule)
        if age_filter:
            stmt = stmt.where(VaccinationSchedule.age_group.ilike(f"%{age_filter}%"))
        if language != "en":
            stmt = stmt.where(VaccinationSchedule.language == language)
        
        result = await self.db_session.execute(stmt)
        schedules = result.scalars().all()
        
        return [{
            "vaccine_name": s.vaccine_name,
            "age_group": s.age_group,
            "dose_number": s.dose_number,
            "description": s.description,
            "country": s.country
        } for s in schedules[:5]]  # Limit to 5 results
    
    async def get_disease_info(self, query: str, language: str = "en") -> List[Dict]:
        """Get disease information based on query"""
        query_lower = query.lower()
        
        # Extract potential disease names from query
        stmt = select(DiseaseSymptom).where(DiseaseSymptom.language == language)
        result = await self.db_session.execute(stmt)
        diseases = result.scalars().all()
        
        # Filter diseases that match query
        matching_diseases = []
        for disease in diseases:
            disease_name_lower = disease.disease_name.lower()
            if disease_name_lower in query_lower or any(
                symptom.lower() in query_lower for symptom in (disease.symptoms or [])
            ):
                matching_diseases.append({
                    "disease_name": disease.disease_name,
                    "symptoms": disease.symptoms or [],
                    "prevention": disease.prevention or [],
                    "treatment": disease.treatment,
                    "severity": disease.severity
                })
        
        return matching_diseases[:3]  # Limit to 3 results
    
    async def get_symptom_info(self, query: str, language: str = "en") -> List[Dict]:
        """Get symptom information based on query"""
        return await self.get_disease_info(query, language)
    
    async def initialize_sample_data(self):
        """Initialize database with sample healthcare data"""
        # Check if data already exists
        try:
            result = await self.db_session.execute(select(VaccinationSchedule))
            if result.scalars().first():
                return  # Data already initialized
        except Exception:
            # Table might not exist yet, continue with initialization
            pass
        
        # Sample vaccination schedules
        vaccinations = [
            VaccinationSchedule(
                age_group="Newborn (0-1 month)",
                vaccine_name="BCG",
                dose_number=1,
                description="BCG vaccine protects against tuberculosis. Given at birth or within first month.",
                country="IN",
                language="en"
            ),
            VaccinationSchedule(
                age_group="Infant (6-8 weeks)",
                vaccine_name="DPT",
                dose_number=1,
                description="DPT vaccine protects against Diphtheria, Pertussis, and Tetanus. First dose at 6-8 weeks.",
                country="IN",
                language="en"
            ),
            VaccinationSchedule(
                age_group="Infant (10-12 weeks)",
                vaccine_name="DPT",
                dose_number=2,
                description="DPT vaccine second dose at 10-12 weeks.",
                country="IN",
                language="en"
            ),
            VaccinationSchedule(
                age_group="Infant (14-16 weeks)",
                vaccine_name="DPT",
                dose_number=3,
                description="DPT vaccine third dose at 14-16 weeks.",
                country="IN",
                language="en"
            ),
            VaccinationSchedule(
                age_group="Child (9-12 months)",
                vaccine_name="MMR",
                dose_number=1,
                description="MMR vaccine protects against Measles, Mumps, and Rubella. First dose at 9-12 months.",
                country="IN",
                language="en"
            ),
            VaccinationSchedule(
                age_group="Adult",
                vaccine_name="COVID-19",
                dose_number=1,
                description="COVID-19 vaccine first dose. Booster doses recommended as per government guidelines.",
                country="IN",
                language="en"
            ),
        ]
        
        # Sample disease symptoms
        diseases = [
            DiseaseSymptom(
                disease_name="Dengue",
                symptoms=["High fever", "Severe headache", "Pain behind eyes", "Joint and muscle pain", "Rash", "Mild bleeding"],
                prevention=["Use mosquito nets", "Wear long-sleeved clothing", "Use mosquito repellent", "Eliminate standing water", "Keep surroundings clean"],
                treatment="Rest, stay hydrated, manage fever with paracetamol. Seek medical attention if symptoms worsen.",
                severity="Moderate to Severe",
                language="en"
            ),
            DiseaseSymptom(
                disease_name="Malaria",
                symptoms=["Fever", "Chills", "Sweating", "Headache", "Nausea", "Vomiting", "Fatigue"],
                prevention=["Use mosquito nets", "Take antimalarial medication in high-risk areas", "Use insect repellent", "Wear protective clothing"],
                treatment="Antimalarial medication prescribed by healthcare provider. Early treatment is crucial.",
                severity="Moderate to Severe",
                language="en"
            ),
            DiseaseSymptom(
                disease_name="Typhoid",
                symptoms=["High fever", "Weakness", "Stomach pain", "Headache", "Loss of appetite", "Rose-colored spots"],
                prevention=["Get vaccinated", "Drink clean water", "Eat well-cooked food", "Maintain hygiene", "Wash hands regularly"],
                treatment="Antibiotics prescribed by healthcare provider. Rest and hydration important.",
                severity="Moderate",
                language="en"
            ),
            DiseaseSymptom(
                disease_name="Diarrhea",
                symptoms=["Loose, watery stools", "Abdominal cramps", "Nausea", "Dehydration", "Fever"],
                prevention=["Wash hands regularly", "Drink clean water", "Eat well-cooked food", "Maintain hygiene"],
                treatment="Oral rehydration solution (ORS), rest, and light diet. Seek medical attention if severe or prolonged.",
                severity="Mild to Moderate",
                language="en"
            ),
            DiseaseSymptom(
                disease_name="Common Cold",
                symptoms=["Runny nose", "Sneezing", "Cough", "Sore throat", "Mild fever", "Fatigue"],
                prevention=["Wash hands regularly", "Avoid close contact with sick people", "Cover mouth when coughing", "Maintain good hygiene"],
                treatment="Rest, stay hydrated, over-the-counter medication for symptoms. Usually resolves in 7-10 days.",
                severity="Mild",
                language="en"
            ),
        ]
        
        for vax in vaccinations:
            self.db_session.add(vax)
        
        for disease in diseases:
            self.db_session.add(disease)
        
        await self.db_session.commit()

