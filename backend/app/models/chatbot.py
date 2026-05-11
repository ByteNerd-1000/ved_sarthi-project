"""
Chatbot core logic with multilingual support
"""

from typing import Dict, List, Optional
from app.services.translation import TranslationService
from app.services.ai_service import AIService
from app.models.health_data import HealthDataService
from app.models.alert import AlertService
from sqlalchemy.ext.asyncio import AsyncSession
import json
import re

class ChatbotService:
    def __init__(self, db_session: AsyncSession):
        self.db_session = db_session
        self.translation_service = TranslationService()
        self.ai_service = AIService()
        self.health_data_service = HealthDataService(db_session)
        self.alert_service = AlertService()
    
    async def process_message(
        self, 
        message: str, 
        user_id: str, 
        language: str = "en"
    ) -> Dict:
        """Process user message and generate response"""
        
        # Auto-detect language from message if not explicitly set or if message appears in different language
        detected_lang = await self.translation_service.detect_language(message)
        
        # Use detected language if:
        # 1. Language is set to "auto", OR
        # 2. Detected language is not English and different from selected language
        if language == "auto" or (detected_lang != "en" and detected_lang != language):
            language = detected_lang
        
        # Fetch alerts and health context in parallel for better responsiveness
        import asyncio
        alerts_task = self.alert_service.get_active_alerts()
        health_context_task = self._get_health_context(message, language)
        
        alerts, health_context = await asyncio.gather(alerts_task, health_context_task)
        
        if alerts:
            alert_info = self._format_alerts_for_context(alerts, language)
        else:
            alert_info = ""
        
        # For AI service, pass original message - AI can handle multilingual input
        # AI service will generate response directly in target language when using Groq
        user_message_for_ai = message
        
        # Generate response using AI with health context
        # AI service is configured to respond directly in target language
        response = await self.ai_service.generate_response(
            user_message=user_message_for_ai,
            health_context=health_context,
            alert_context=alert_info,
            language=language
        )
        
        # For rule-based responses (offline mode), translation may still be needed
        # But AI service with Groq should respond directly in target language
        # Only translate if response appears to be in English when target is not English
        if language != "en" and not self._is_response_in_language(response, language):
            # Response might be in English, try to translate it
            try:
                response = await self.translation_service.translate(response, language, "en")
            except Exception as e:
                print(f"Translation fallback failed: {e}, using original response")
        
        # For accuracy evaluation, we still need English version
        if language != "en":
            try:
                message_en = await self.translation_service.translate(message, "en", language)
                response_en = await self.translation_service.translate(response, "en", language)
            except Exception:
                message_en = message
                response_en = response
        else:
            message_en = message
            response_en = response
        
        # Validate response accuracy
        accuracy_score = await self._evaluate_response_accuracy(message_en, response_en, health_context)
        
        return {
            "response": response,
            "language": language,
            "accuracy_score": accuracy_score,
            "sources": health_context.get("sources", []),
            "alerts": alerts if alerts else []
        }
    
    async def _get_health_context(self, message: str, language: str) -> Dict:
        """Extract relevant health context from message"""
        context = {
            "vaccination_info": [],
            "disease_info": [],
            "symptoms_info": [],
            "sources": []
        }
        
        # Check for vaccination queries
        vaccination_keywords = ["vaccine", "vaccination", "immunization", "dose", "vaccinate"]
        if any(keyword in message.lower() for keyword in vaccination_keywords):
            vaccination_data = await self.health_data_service.get_vaccination_info(message, language)
            context["vaccination_info"] = vaccination_data
            context["sources"].append("vaccination_schedule")
        
        # Check for disease/symptom queries
        disease_data = await self.health_data_service.get_disease_info(message, language)
        if disease_data:
            context["disease_info"] = disease_data
            context["sources"].append("disease_symptoms")
        
        # Check for symptom queries
        symptom_data = await self.health_data_service.get_symptom_info(message, language)
        if symptom_data:
            context["symptoms_info"] = symptom_data
            context["sources"].append("disease_symptoms")
        
        return context
    
    def _format_alerts_for_context(self, alerts: List[Dict], language: str) -> str:
        """Format active alerts for AI context"""
        if not alerts:
            return ""
        
        alert_text = "Active Health Alerts:\n"
        for alert in alerts:
            alert_text += f"- {alert['disease_name']}: {alert['description']}\n"
            alert_text += f"  Severity: {alert['severity']}\n"
            if alert.get('recommendations'):
                alert_text += f"  Recommendations: {', '.join(alert['recommendations'])}\n"
        
        return alert_text
    
    def _is_response_in_language(self, response: str, target_language: str) -> bool:
        """Check if response appears to be in target language"""
        if target_language == "en":
            # Check if it's mostly English (non-unicode characters)
            return all(ord(c) < 128 for c in response[:100]) if response else True
        
        # Language-specific character checks
        lang_char_ranges = {
            "hi": "अआइईउऊऋएऐओऔकखगघङचछजझञटठडढणतथदधनपफबभमयरलवशषसह",
            "te": "అఆఇఈఉఊఋఌఎఏఐఒఓఔకఖగఘఙచఛజఝఞటఠడఢణతథదధనపఫబభమయరలవశషసహ",
            "ta": "அஆஇஈஉஊஎஏஐஒஓஔகஙசஞடணதனபமயரலவஶஷஸஹ",
            "bn": "অআইঈউঊঋএঐওঔকখগঘঙচছজঝঞটঠডঢণতথদধনপফবভমযরলশষসহ",
            "mr": "अआइईउऊऋएऐओऔकखगघङचछजझञटठडढणतथदधनपफबभमयरलवशषसह",
            "gu": "અઆઇઈઉઊઋએઐઓઔકખગઘઙચછજઝઞટઠડઢણતથદધનપફબભમયરલવશષસહ",
            "kn": "ಅಆಇಈಉಊಋಎಏಐಒಓಔಕಖಗಘಙಚಛಜಝಞಟಠಡಢಣತಥದಧನಪಫಬಭಮಯರಲವಶಷಸಹ",
            "ml": "അആഇഈഉഊഋഎഏഐഒഓഔകഖഗഘങചഛജഝഞടഠഡഢണതഥദധനപഫബഭമയരലവശഷസഹ",
            "ur": "ابپتٹثجچحخدڈذرڑزژسشصضطظعغفقکگلمنوہھءیے"
        }
        
        if target_language in lang_char_ranges:
            chars = lang_char_ranges[target_language]
            # Check if response contains characters from target language
            sample = response[:200] if len(response) > 200 else response
            return any(char in chars for char in sample)
        
        return True  # Default to true if we can't detect
    
    async def _evaluate_response_accuracy(
        self, 
        user_message: str, 
        response: str, 
        context: Dict
    ) -> int:
        """Evaluate response accuracy (0-100)"""
        score = 100
        
        # Check if response contains relevant information
        if context.get("vaccination_info") and not any(
            term in response.lower() for term in ["vaccine", "vaccination", "dose", "immunization"]
        ):
            score -= 20
        
        if context.get("disease_info") and not any(
            term in response.lower() for term in ["disease", "symptom", "prevent", "treatment"]
        ):
            score -= 20
        
        # Check response length (too short might be incomplete)
        if len(response) < 50:
            score -= 10
        
        # Check for medical accuracy indicators
        medical_terms = ["doctor", "medical", "health", "treatment", "prevention", "symptom"]
        if not any(term in response.lower() for term in medical_terms):
            score -= 15
        
        return max(0, min(100, score))

