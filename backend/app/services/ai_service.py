"""
AI Service for generating chatbot responses
Supports Groq API with fallback to rule-based responses (offline mode)
"""

import os
from typing import Dict, Optional
import json
from app.services.translation import TranslationService

class AIService:
    def __init__(self):
        # Try to initialize Groq API
        self.groq_client = None
        self.api_key = os.getenv("GROQ_API_KEY") or os.getenv("API_KEY")
        self.translation_service = TranslationService()
        
        # Check if API key is provided (starts with gsk_)
        if self.api_key and self.api_key.startswith("gsk_"):
            try:
                from groq import Groq
                self.groq_client = Groq(api_key=self.api_key)
                print("AI Service initialized with Groq API - enhanced responses enabled")
                self.offline_mode = False
            except ImportError:
                print("Groq SDK not installed. Install with: pip install groq")
                print("Falling back to offline mode")
                self.offline_mode = True
            except Exception as e:
                print(f"Error initializing Groq API: {e}")
                print("Falling back to offline mode")
                self.offline_mode = True
        else:
            self.offline_mode = True
            if not self.api_key:
                print("AI Service initialized in OFFLINE MODE - no API key provided")
                print("To enable Groq API, set GROQ_API_KEY environment variable or .env")
            else:
                print("AI Service initialized in OFFLINE MODE - invalid API key format")
        
        # System prompt for chatbot (primarily healthcare, but can answer any topic)
        self.system_prompt = """You are an AI assistant named Veda Sarthi.

PRIMARY ROLE (HEALTHCARE):
- You are a knowledgeable and empathetic healthcare assistant designed to educate rural and semi-urban populations about preventive healthcare, disease symptoms, and vaccination schedules.
- Provide accurate, evidence-based health information in simple language.
- Emphasize preventive measures and vaccination importance.
- Direct users to seek professional medical help when necessary.
- Be culturally sensitive, supportive, and non-judgmental.

OTHER QUESTIONS:
- You can also answer general questions on any topic (education, technology, everyday life, etc.) when the user asks.
- If the question is not about health, answer helpfully and clearly at the level of a general assistant.

SAFETY RULES FOR MEDICAL TOPICS:
- Always prioritize safety: recommend consulting healthcare professionals for serious or urgent symptoms.
- Do NOT give diagnoses or prescribe specific medicines or doses.
- Be clear that your information is educational and not a replacement for a doctor.
- If you don't know something, say so instead of guessing, and suggest consulting a professional."""
    
    async def generate_response(
        self,
        user_message: str,
        health_context: Dict,
        alert_context: str = "",
        language: str = "en"
    ) -> str:
        """Generate AI response with health context"""
        
        # Build context string
        context_parts = []
        
        if alert_context:
            context_parts.append(alert_context)
        
        if health_context.get("vaccination_info"):
            context_parts.append("\nVaccination Information:")
            for vax in health_context["vaccination_info"]:
                context_parts.append(f"- {vax.get('vaccine_name', '')}: {vax.get('description', '')}")
        
        if health_context.get("disease_info"):
            context_parts.append("\nDisease Information:")
            for disease in health_context["disease_info"]:
                context_parts.append(f"- {disease.get('disease_name', '')}: Symptoms: {', '.join(disease.get('symptoms', []))}")
                context_parts.append(f"  Prevention: {', '.join(disease.get('prevention', []))}")
        
        context_string = "\n".join(context_parts)
        
        # Build user message with context
        full_message = f"{user_message}\n\n{context_string}" if context_string else user_message
        
        # Try Groq API first if available
        if self.groq_client:
            try:
                response = await self._generate_groq_response(full_message, language)
                return response
            except Exception as e:
                print(f"Groq API error: {e}, falling back to rule-based response")
        
        # Fallback to rule-based response (offline mode)
        return await self._generate_rule_based_response(user_message, health_context, alert_context, language)
    
    async def _generate_groq_response(self, message: str, language: str = "en") -> str:
        """Generate response using Groq API"""
        if not self.groq_client:
            raise Exception("Groq client not initialized")
        
        # Get language name for better context
        language_names = {
            "en": "English", "hi": "Hindi", "te": "Telugu", "ta": "Tamil",
            "bn": "Bengali", "mr": "Marathi", "gu": "Gujarati", "kn": "Kannada",
            "ml": "Malayalam", "ur": "Urdu"
        }
        lang_name = language_names.get(language, "English")
        
        # Build system prompt with explicit language instruction
        system_prompt = f"""{self.system_prompt}

IMPORTANT: The user's preferred language is {lang_name} ({language}).
You MUST respond directly in {lang_name}. Do not respond in English unless the user explicitly asks in English.
Be culturally appropriate and use natural language for {lang_name} speakers.
Keep responses concise and clear (aim for 100-200 words maximum for faster responses)."""
        
        try:
            # Use Groq's chat completion API with optimized settings
            import asyncio
            
            # Groq SDK might be synchronous, so we'll run it in executor with timeout
            async def call_groq_with_timeout():
                loop = asyncio.get_event_loop()
                
                def call_groq():
                    chat_completion = self.groq_client.chat.completions.create(
                        messages=[
                            {"role": "system", "content": system_prompt},
                            {"role": "user", "content": message}
                        ],
                        model="llama-3.1-8b-instant",  # Faster model for better responsiveness
                        temperature=0.7,
                        max_tokens=500,  # Reduced for faster responses
                        top_p=0.9,
                        stream=False
                    )
                    return chat_completion.choices[0].message.content
                
                # Add timeout to prevent hanging (15 seconds max)
                try:
                    response = await asyncio.wait_for(
                        loop.run_in_executor(None, call_groq),
                        timeout=15.0
                    )
                    return response.strip()
                except asyncio.TimeoutError:
                    print("Groq API call timed out after 15 seconds")
                    raise Exception("Request timeout - please try again")
            
            response = await call_groq_with_timeout()
            return response
        except Exception as e:
            print(f"Error calling Groq API: {e}")
            raise
    
    async def _generate_rule_based_response(
        self,
        user_message: str,
        health_context: Dict,
        alert_context: str,
        language: str = "en"
    ) -> str:
        """Rule-based response generation with natural language variations (offline mode)"""
        import random
        message_lower = user_message.lower()
        
        # Add alert context if available
        if alert_context:
            alert_prefix = alert_context + "\n\n"
        else:
            alert_prefix = ""
        
        # Check for greetings
        if any(word in message_lower for word in ["hello", "hi", "namaste", "hey", "नमस्ते", "greetings"]):
            greetings = [
                "Hello! I'm here to help you with health information. What would you like to know?",
                "Hi there! Feel free to ask me anything about health and wellness.",
                "Namaste! I'm a healthcare information assistant. How can I assist you today?",
                "Welcome! I'm ready to help with your health-related questions.",
                "Hello! Ask me about diseases, symptoms, vaccinations, or preventive health measures."
            ]
            return alert_prefix + random.choice(greetings)
        
        # Check for vaccination queries
        if any(word in message_lower for word in ["vaccine", "vaccination", "immunization", "dose", "टीका", "vaccinate", "jabbing"]):
            if health_context.get("vaccination_info"):
                vax_info_list = health_context["vaccination_info"]
                vax_templates = [
                    "Based on your query, here's important vaccination information:\n\n{vax_list}\n\nVaccination is crucial for building immunity. Always follow your healthcare provider's recommendations.",
                    "Vaccination is one of the best ways to protect your health. Here's relevant information:\n\n{vax_list}\n\nConsult your doctor for personalized vaccination advice.",
                    "Great question about vaccinations! Here's what you should know:\n\n{vax_list}\n\nMake sure to complete your vaccination schedule as recommended by health authorities."
                ]
                
                vax_list_text = "\n".join([f"• {vax.get('vaccine_name', 'Vaccine')}: Recommended for {vax.get('age_group', 'specific age groups')} - {vax.get('description', '')}" 
                                          for vax in vax_info_list[:3]])
                return alert_prefix + random.choice(vax_templates).format(vax_list=vax_list_text)
            return alert_prefix + self.translation_service.translate_common_response("vaccination_info", language)
        
        # Check for specific disease queries
        disease_keywords = {
            "dengue": ["dengue", "डेंगू"],
            "malaria": ["malaria", "मलेरिया"],
            "typhoid": ["typhoid", "टाइफाइड"],
            "diarrhea": ["diarrhea", "diarrhoea", "दस्त"],
            "cold": ["cold", "common cold", "सर्दी", "cough"]
        }
        
        for disease_name, keywords in disease_keywords.items():
            if any(keyword in message_lower for keyword in keywords):
                if health_context.get("disease_info"):
                    for disease in health_context["disease_info"]:
                        if disease_name.lower() in disease.get("disease_name", "").lower():
                            disease_name_full = disease.get('disease_name')
                            symptoms = disease.get("symptoms", [])
                            prevention = disease.get("prevention", [])
                            treatment = disease.get("treatment", "Consult a healthcare professional")
                            
                            # Multiple response templates for variety
                            templates = [
                                f"{disease_name_full} is an important health concern. Here's what you need to know:\n\n"
                                f"Common signs include: {', '.join(symptoms)}\n\n"
                                f"Prevention methods: {', '.join(prevention)}\n\n"
                                f"Treatment approach: {treatment}\n\n"
                                f"If symptoms develop, please seek medical attention promptly.",
                                
                                f"Regarding {disease_name_full}:\n\n"
                                f"📌 Watch for these signs: {', '.join(symptoms)}\n\n"
                                f"🛡️ Protect yourself: {', '.join(prevention)}\n\n"
                                f"💊 Medical management: {treatment}\n\n"
                                f"Don't hesitate to visit a healthcare facility if needed.",
                                
                                f"Let me provide information about {disease_name_full}:\n\n"
                                f"You might experience: {', '.join(symptoms)}\n\n"
                                f"Key prevention steps: {', '.join(prevention)}\n\n"
                                f"Treatment options: {treatment}\n\n"
                                f"Always consult with a qualified doctor for proper diagnosis and care.",
                            ]
                            return alert_prefix + random.choice(templates)
        
        # Check for symptom/prevention queries
        if any(word in message_lower for word in ["symptom", "sign", "feel", "pain", "ache", "hurting", "लक्षण", "fever", "headache", "prevent", "prevention", "avoid", "रोकथाम"]):
            if health_context.get("disease_info"):
                disease = health_context["disease_info"][0]
                disease_name = disease.get('disease_name', 'the condition')
                
                # Varied response based on query type
                if any(word in message_lower for word in ["prevent", "prevention", "avoid", "रोकथाम"]):
                    prevention_steps = disease.get("prevention", [])
                    if prevention_steps:
                        prevention_text = "\n".join([f"✓ {step}" for step in prevention_steps])
                        templates = [
                            f"Excellent question! To stay healthy and prevent {disease_name}:\n\n{prevention_text}\n\nRegular preventive care is your best defense.",
                            f"Here's how to protect yourself from {disease_name}:\n\n{prevention_text}\n\nRemember: prevention is easier than treatment!",
                            f"The best way to avoid {disease_name} is through these preventive measures:\n\n{prevention_text}\n\nStay vigilant about your health."
                        ]
                        return alert_prefix + random.choice(templates)
                else:
                    # Symptom-focused response when we matched a known disease
                    symptoms = disease.get("symptoms", [])
                    if symptoms:
                        symptoms_text = ", ".join(symptoms)
                        templates = [
                            f"If you're concerned about {disease_name}, watch for these signs: {symptoms_text}\n\n"
                            f"If these symptoms appear, consult a healthcare provider soon.",
                            
                            f"The symptoms of {disease_name} typically include: {symptoms_text}\n\n"
                            f"Don't ignore persistent symptoms—seek medical advice.",
                            
                            f"Common symptoms of {disease_name} are: {symptoms_text}\n\n"
                            f"Contact your doctor if you experience any of these signs."
                        ]
                        return alert_prefix + random.choice(templates)
            else:
                # No specific disease match, but user is clearly describing symptoms (like "my hand is paining")
                if any(word in message_lower for word in ["pain", "paining", "ache", "hurting"]):
                    generic_pain_response = (
                        "You mentioned pain: \"{question}\".\n\n"
                        "Hand or limb pain can have many possible causes such as muscle strain, minor injury, overuse, "
                        "joint or nerve problems.\n\n"
                        "General guidance:\n"
                        "• Rest the affected area and avoid heavy use for a while.\n"
                        "• You may use a cold pack in the first 24 hours, then warm compresses if it helps.\n"
                        "• Keep an eye on swelling, redness, numbness, or severe pain.\n\n"
                        "⚠️ This is not a diagnosis. If the pain is severe, associated with injury, "
                        "numbness/weakness, or does not improve in 1–2 days, please consult a qualified doctor as soon as possible."
                    ).format(question=user_message)
                    return alert_prefix + generic_pain_response
                
                # Generic symptom advice when we don't know the exact condition
                generic_symptom_response = (
                    "You are describing symptoms: \"{question}\".\n\n"
                    "Because many different conditions can cause similar symptoms, it is not safe to give a precise "
                    "diagnosis here. However, you can monitor how your symptoms change, rest, stay hydrated, and avoid "
                    "anything that clearly makes them worse.\n\n"
                    "⚠️ If symptoms are severe, suddenly worse, involve trouble breathing, chest pain, loss of consciousness, "
                    "or do not improve over a few days, please seek immediate medical care."
                ).format(question=user_message)
                return alert_prefix + generic_symptom_response
        
        # Check for general disease/illness queries
        if any(word in message_lower for word in ["disease", "illness", "sick", "condition", "रोग", "health"]):
            if health_context.get("disease_info"):
                disease = health_context["disease_info"][0]
                disease_name = disease.get('disease_name', 'health condition')
                templates = [
                    f"You asked about health. Based on available information, {disease_name} is worth knowing about. "
                    f"It affects many people and understanding it can help you stay safe.",
                    
                    f"Health is crucial! Regarding {disease_name}: understanding its symptoms and prevention measures "
                    f"empowers you to take better care of yourself and your family.",
                    
                    f"Good question about health matters! {disease_name} is something everyone should be informed about. "
                    f"Knowledge is your best tool for preventive healthcare."
                ]
                return alert_prefix + random.choice(templates)
        
        # Varied default responses for questions that don't match known patterns (offline mode)
        default_responses = [
            "Thank you for your question. I am primarily designed as a healthcare assistant, so I may not always have detailed information about every topic, but I can still offer general guidance and encourage you to refer to trusted sources and professionals for precise details.",
            "I may not recognize this exact question in my offline knowledge, but I am here to support you, especially with healthcare, symptoms, prevention, and general well‑being. For specific or complex topics, please also consult reliable references or experts.",
            "My offline knowledge is focused on health and preventive care. I might not fully answer this particular topic, but if it relates to your health, symptoms, lifestyle, or prevention, feel free to give me a bit more detail so I can try to help.",
            "I don't have a precise offline answer to that, but I can still help you think about your overall health, habits, and when it is a good idea to talk to a qualified professional about your concern.",
            "I'm still learning in offline mode and might not cover everything. However, I'm always ready to help you with questions about staying healthy, understanding symptoms, and making safer choices."
        ]
        
        return alert_prefix + random.choice(default_responses)

