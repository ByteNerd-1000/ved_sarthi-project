"""
Offline Translation service for multilingual support
Uses local translation dictionary - no internet required
Supports: English, Hindi, Telugu, Tamil, Bengali, Marathi, Gujarati, Kannada, Malayalam, Urdu
"""

from typing import Dict, Optional
import json

# Supported languages mapping
SUPPORTED_LANGUAGES = {
    "en": "English",
    "hi": "Hindi",
    "te": "Telugu",
    "ta": "Tamil",
    "bn": "Bengali",
    "mr": "Marathi",
    "gu": "Gujarati",
    "kn": "Kannada",
    "ml": "Malayalam",
    "ur": "Urdu"
}

# Comprehensive offline translation dictionary
TRANSLATION_DICTIONARY = {
    # Common medical terms
    "vaccine": {
        "hi": "टीका", "te": "వాక్సిన్", "ta": "தடுப்பூசி", 
        "bn": "ভ্যাকসিন", "mr": "लस", "gu": "વેક્સિન", "kn": "ವ್ಯಾಕ್ಸೀನ್", "ml": "വാക్సിൻ", "ur": "ویکسین"
    },
    "symptom": {
        "hi": "लक्षण", "te": "లక్షణాలు", "ta": "அறிகுறிகள்",
        "bn": "লক্ষণ", "mr": "लक्षणे", "gu": "લક્ષણો", "kn": "ಲಕ್ಷಣಗಳು", "ml": "ലക്ഷണങ്ങൾ", "ur": "علامات"
    },
    "disease": {
        "hi": "रोग", "te": "వ్యాధి", "ta": "நோய்",
        "bn": "রোগ", "mr": "रोग", "gu": "રોગ", "kn": "ರೋಗ", "ml": "രോഗം", "ur": "بیماری"
    },
    "prevention": {
        "hi": "रोकथाम", "te": "నివారణ", "ta": "தடுப்பு",
        "bn": "প্রতিরোধ", "mr": "प्रतिबंध", "gu": "પ્રતિરોધ", "kn": "ತಡೆಗಟ್ಟುವಿಕೆ", "ml": "തടയൽ", "ur": "روک تھام"
    },
    "treatment": {
        "hi": "उपचार", "te": "చికిత్స", "ta": "சிகிச்சை",
        "bn": "চিকিৎসা", "mr": "उपचार", "gu": "સારવાર", "kn": "ಚಿಕಿತ್ಸೆ", "ml": "ചികിത്സ", "ur": "علاج"
    },
    "fever": {
        "hi": "बुखार", "te": "జ్వరం", "ta": "காய்ச்சல்",
        "bn": "জ্বর", "mr": "ताप", "gu": "તાવ", "kn": "ಜ್ವರ", "ml": "പനി", "ur": "بخار"
    },
    "headache": {
        "hi": "सिरदर्द", "te": "తలనొప్పి", "ta": "தலைவலி",
        "bn": "মাথাব্যথা", "mr": "डोकेदुखी", "gu": "માથાનો દુખાવો", "kn": "ತಲೆನೋವು", "ml": "തലവേദന", "ur": "سر درد"
    },
    "doctor": {
        "hi": "डॉक्टर", "te": "డాక్టర్", "ta": "மருத்துவர்",
        "bn": "ডাক্তার", "mr": "डॉक्टर", "gu": "ડૉક્ટર", "kn": "ವೈದ್ಯ", "ml": "ഡോക്ടർ", "ur": "ڈاکٹر"
    },
    "health": {
        "hi": "स्वास्थ्य", "te": "ఆరోగ్యం", "ta": "ஆரோக்கியம்",
        "bn": "স্বাস্থ্য", "mr": "आरोग्य", "gu": "આરೋಗ್ಯ", "kn": "ಆರೋಗ್ಯ", "ml": "ആരോഗ്യം", "ur": "صحت"
    },
    "medicine": {
        "hi": "दवा", "te": "మందు", "ta": "மருந்து",
        "bn": "ঔষধ", "mr": "औषध", "gu": "દવા", "kn": "ಮದ್ದು", "ml": "മരുന്ന്", "ur": "دوا"
    },
    # Common phrases
    "hello": {
        "hi": "नमस्ते", "te": "నమస్కారం", "ta": "வணக்கம்",
        "bn": "নমস্কার", "mr": "नमस्कार", "gu": "નમસ્તે", "kn": "ನಮಸ್ಕಾರ", "ml": "നമസ്കാരം", "ur": "السلام علیکم"
    },
    "thank you": {
        "hi": "धन्यवाद", "te": "ధన్యవాదాలు", "ta": "நன்றி",
        "bn": "ধন্যবাদ", "mr": "धन्यवाद", "gu": "આભાર", "kn": "ಧನ್ಯವಾದ", "ml": "നന്ദി", "ur": "شکریہ"
    },
    "yes": {
        "hi": "हाँ", "te": "అవును", "ta": "ஆம்",
        "bn": "হ্যাঁ", "mr": "होय", "gu": "હા", "kn": "ಹೌದು", "ml": "അതെ", "ur": "ہاں"
    },
    "no": {
        "hi": "नहीं", "te": "కాదు", "ta": "இல்லை",
        "bn": "না", "mr": "नाही", "gu": "ના", "kn": "ಇಲ್ಲ", "ml": "ഇല്ല", "ur": "نہیں"
    }
}

# Common responses in multiple languages
COMMON_RESPONSES = {
    "en": {
        "greeting": "Hello! I'm your healthcare assistant. I can help you with information about preventive healthcare, disease symptoms, vaccination schedules, and health alerts. How can I assist you today?",
        "vaccination_info": "Vaccination is an important preventive measure. Please consult with your local healthcare provider or visit a government health center for vaccination schedules suitable for your age group.",
        "symptom_query": "If you're experiencing symptoms, it's important to consult with a healthcare professional. For emergency situations, please contact emergency services immediately.",
        "disease_query": "For information about specific diseases, prevention, and treatment, please consult with healthcare professionals. Prevention through vaccination and healthy practices is always recommended.",
        "default": "I'm here to help with healthcare information. You can ask me about vaccinations, disease symptoms, preventive measures, or health alerts. For specific medical advice, please consult with a qualified healthcare professional."
    },
    "hi": {
        "greeting": "नमस्ते! मैं आपका स्वास्थ्य सहायक हूं। मैं आपको निवारक स्वास्थ्य देखभाल, बीमारी के लक्षण, टीकाकरण कार्यक्रम और स्वास्थ्य अलर्ट के बारे में जानकारी में मदद कर सकता हूं। आज मैं आपकी कैसे मदद कर सकता हूं?",
        "vaccination_info": "टीकाकरण एक महत्वपूर्ण निवारक उपाय है। कृपया अपने स्थानीय स्वास्थ्य देखभाल प्रदाता से परामर्श करें या अपने आयु समूह के लिए उपयुक्त टीकाकरण कार्यक्रम के लिए सरकारी स्वास्थ्य केंद्र पर जाएं।",
        "symptom_query": "यदि आप लक्षणों का अनुभव कर रहे हैं, तो स्वास्थ्य देखभाल पेशेवर से परामर्श करना महत्वपूर्ण है। आपातकालीन स्थितियों के लिए, कृपया तुरंत आपातकालीन सेवाओं से संपर्क करें।",
        "disease_query": "विशिष्ट बीमारियों, रोकथाम और उपचार के बारे में जानकारी के लिए, कृपया स्वास्थ्य देखभाल पेशेवरों से परामर्श करें। टीकाकरण और स्वस्थ प्रथाओं के माध्यम से रोकथाम हमेशा अनुशंसित है।",
        "default": "मैं स्वास्थ्य देखभाल की जानकारी में मदद के लिए यहां हूं। आप मुझसे टीकाकरण, बीमारी के लक्षण, निवारक उपाय, या स्वास्थ्य अलर्ट के बारे में पूछ सकते हैं। विशिष्ट चिकित्सा सलाह के लिए, कृपया एक योग्य स्वास्थ्य देखभाल पेशेवर से परामर्श करें।"
    }

    ,"te": {
        "greeting": "నమస్కారం! నేను మీ ఆరోగ్య సహాయం. నేను నివారణార్ధక ఆరోగ్య పరిరక్షణ, రోగాల లక్షణాలు, టీకా షెడ్యూలు మరియు ఆరోగ్య అలర్ట్‌ల గురించి సహాయపడగలను. నేను మీకు ఎలా సహాయం చేయగలను?",
        "vaccination_info": "టీకాకరణం ఒక ముఖ్యమైన నివారణ చర్య. దయచేసి మీ స్థానిక ఆరోగ్య సేవా నిపుణుడిని సంప్రదించండి లేదా మీ వయస్సు సమూహానికి సరిపోయే టీకా షెడ్యూల్ కోసం ప్రభుత్వ ఆరోగ్య కేంద్రాన్ని సందర్శించండి.",
        "symptom_query": "మీకు లక్షణాలు ఉంటే, ఆరోగ్య సంరక్షణ నిపుణుడిని సంప్రదించడం ముఖ్యం. అత్యవసర పరిస్థితులలో వెంటనే అత్యవసర సేవలను సంప్రదించండి.",
        "disease_query": "నిర్దిష్ట వ్యాధుల గురించి, నిరోధక చర్యలు మరియు చికిత్స గురించి సమాచారం కోసం, దయచేసి ఆరోగ్య నిపుణులను సంప్రదించండి. టీకాకరణ మరియు ఆరోగ్యకర జీవనశైలి ద్వారా నిరోధకమే సూచించబడుతుంది.",
        "default": "నేను ఆరోగ్య సమాచారంలో సహాయం చేయడానికి ఇక్కడ ఉన్నాను. మీరు నన్ను టీకాలు, వ్యాధి లక్షణాలు, నివారణా చర్యలు లేదా ఆరోగ్య అలర్ట్స్ గురించి అడగవచ్చు. ప్రత్యేక వైద్య సలహాకు దయచేసి ఒక తగిన ఆరోగ్య నిపుణ్ని సంప్రదించండి."
    },

    "ta": {
        "greeting": "வணக்கம்! நான் உங்கள் உடல்நலம் உதவியாளர். தடுப்பு சுகாதாரம், நோய்களின் அறிகுறிகள், தடுப்பூசி அட்டவணை மற்றும் சுகாதார எச்சரிக்கைகள் பற்றிய தகவலில் உங்களுக்கு உதவ முடியும். இன்று நான் எப்படி உங்களுக்கு உதவலாம்?",
        "vaccination_info": "தடுப்பூசி ஒரு முக்கியமான தடுப்பு நடவடிக்கை. உங்கள் உள்ளூர் சுகாதார சேவை வழங்குநரை அணுகவும் அல்லது உங்கள் வயது குழுவிற்கான தடுப்பூசி அட்டவணைக்கு அரசு சுகாதார மையத்தை அணுகவும்.",
        "symptom_query": "நீங்கள் அறிகுறிகளை அனுபவித்தால், ஒரு சுகாதார நிபுணரை அணுகுவது முக்கியம். அவசர நிலைகளில் உடனடியாக அவசர சேவைகளுக்குச் தொடர்பு கொள்ளவும்.",
        "disease_query": "குறிப்பிட்ட நோய்கள், தடுப்பு மற்றும் சிகிச்சை பற்றிய தகவலுக்கு சுகாதார நிபுணர்களை அணுகவும். தடுப்பூசி மற்றும் ஆரோக்கியமான பழக்க வழக்கங்கள் மூலம் தடுப்பு எப்போதும் பரிந்துரைக்கப்படுகிறது.",
        "default": "நான் சுகாதாரத் தகவல்களில் உதவ தயாராக இருக்கிறேன். நீங்கள் என்னை தடுப்பூசிகள், நோய் அறிகுறிகள், தடுப்பு நடவடிக்கைகள் அல்லது சுகாதார எச்சரிக்கைகள் பற்றி கேட்கலாம். குறிப்பிட்ட மருத்துவ ஆலோசனைக்காக ஒரு தகுதி பெற்ற சுகாதார நிபுணரை அணுகவும்."
    },

    "bn": {
        "greeting": "নমস্কার! আমি আপনার স্বাস্থ্য সহকারী। আমি প্রতিরোধমূলক স্বাস্থ্য, রোগের লক্ষণ, টিকাকরণ সূচি এবং স্বাস্থ্য সতর্কতা সম্পর্কে তথ্য দেওয়ার ক্ষেত্রে সাহায্য করতে পারি। আজ আমি কীভাবে আপনাকে সাহায্য করতে পারি?",
        "vaccination_info": "টিকাকরণ একটি গুরুত্বপূর্ণ প্রতিরোধমূলক ব্যবস্থা। আপনার স্থানীয় স্বাস্থ্যসেবাদাতার সঙ্গে পরামর্শ করুন বা আপনার বয়সের জন্য উপযুক্ত টিকাকরণ সূচির জন্য সরকারি স্বাস্থ্য কেন্দ্রে যান।",
        "symptom_query": "আপনি যদি লক্ষণ অনুভব করেন, তবে স্বাস্থ্যসেবা পেশাদারের সঙ্গে পরামর্শ করা গুরুত্বপূর্ণ। জরুরি অবস্থায়, দয়া করে অবিলম্বে জরুরি পরিষেবাগুলোর সঙ্গে যোগাযোগ করুন।",
        "disease_query": "নির্দিষ্ট রোগ, প্রতিরোধ ও চিকিৎসা সম্পর্কে তথ্যের জন্য স্বাস্থ্য পেশাদারদের পরামর্শ নিন। টিকাকরণ এবং স্বাস্থ্যকর অভ্যাসের মাধ্যমে প্রতিরোধ সবসময় পরামর্শ দেওয়া হয়।",
        "default": "আমি স্বাস্থ্য তথ্যের জন্য সাহায্য করতে এখানে আছি। আপনি আমার কাছে টিকাকরণ, রোগের লক্ষণ, প্রতিরোধমূলক ব্যবস্থা, বা স্বাস্থ্য সতর্কতা সম্পর্কে জিজ্ঞাসা করতে পারেন। নির্দিষ্ট চিকিৎসা পরামর্শের জন্য একটি যোগ্য স্বাস্থ্য পেশাদারের সঙ্গে পরামর্শ করুন।"
    },

    "mr": {
        "greeting": "नमस्कार! मी तुमचा आरोग्य सहाय्यक आहे. मी प्रतिबंधात्मक आरोग्य, आजारांची लक्षणे, लस शेड्यूल आणि आरोग्य इशाऱ्यांविषयी माहिती देऊ शकतो. आज मी तुम्हाला कशाप्रकारे मदत करू?",
        "vaccination_info": "लस घेणे हे एक महत्त्वाचे प्रतिबंधात्मक पाऊल आहे. कृपया आपल्या स्थानिक आरोग्य सेवा प्रदात्याशी सल्ला घ्या किंवा आपल्या वयोगटासाठी योग्य लस शेड्युलसाठी सरकारी आरोग्य केंद्राला भेट द्या.",
        "symptom_query": "आपल्याला लक्षणे आढळल्यास, आरोग्यव्यवस्थेतील तज्ञाचा सल्ला घेणे आवश्यक आहे. अत्यावश्‍यक परिस्थितीत तत्काळ आपत्कालीन सेवांशी संपर्क करा.",
        "disease_query": "विशिष्ट आजारांविषयी, प्रतिबंध व उपचाराबद्दल माहितीकरिता आरोग्यतज्ञांचा सल्ला घ्या. लस आणि आरोग्यदायी सवयींमुळे प्रतिबंध नेहमीच सुचवला जातो.",
        "default": "मी आरोग्य विषयक माहितीमध्ये मदत करण्यासाठी येथे आहे. तुम्ही मला लस, आजारांचे लक्षणे, प्रतिबंधात्मक उपाय किंवा आरोग्य इशाऱ्यांविषयी विचारू शकता. विशिष्ट वैद्यकीय सल्ल्यासाठी पात्र आरोग्यतज्ञाचा सल्ला घ्या."
    },

    "gu": {
        "greeting": "નમસ્તે! હું તમારો આરોગ્ય સહાયક છું. હું રોધક આરોગ્ય, રોગના લક્ષણો, રસીકરણ સમયસૂચિ અને આરોગ્ય ચેતવણીઓ વિશે માહિતીમાં મદદ કરી શકું છું. આજે હું કેવી રીતે મદદ કરી શકું?",
        "vaccination_info": "રસીકરણ એક મહત્વપૂર્ણ રોધક પગલું છે. કૃપા કરો અને તમારા સ્થાનિક આરોગ્ય સેવાપ્રદાતાને સંપર્ક કરો અથવા તમારી વયસમૂહ માટે યોગ્ય રસીકરણ સમયસૂચિ માટે સરકારી આરોગ્ય કેન્દ્રની મુલાકાત લો.",
        "symptom_query": "જો તમને લક્ષણો અનુભવે છે, તો આરોગ્ય વ્યાવસાયિકનો પરામર્શ જરૂરી છે. તાત્કાલિક પરિસ્થિતિઓમાં તરત જ ત્વરિત સેવાનો સંપર્ક કરો.",
        "disease_query": "નિર્ધારિત રોગો, રોધન અને સારવાર વિશે માહિતી માટે આરોગ્ય નિષ્ણાતનો પરામર્શ કરો. રસીકરણ અને આરોગ્યવર્ધક આચરણ દ્વારા રોધક પગલાં સદાય ભલામણ કરવામાં આવે છે.",
        "default": "હું આરોગ્ય માહિતીમાં મદદ કરવા માટે અહીં છું. તમે મને રસીકરણ, રોગના લક્ષણો, રક્ષણાત્મક પગલાં અથવા આરોગ્ય ચેતવણીઓ વિશે પૂછો. વિશિષ્ટ તબીબી સલાહ માટે કૃપા કરીને લાયકાત ધરાવતા આરોગ્ય નિષ્ણાતનો સંપર્ક કરો."
    },

    "kn": {
        "greeting": "ನಮಸ್ಕಾರ! ನಾನು ನಿಮ್ಮ ಆರೋಗ್ಯ ಸಹಾಯಕ. ನುರಿತ ಆರೋಗ್ಯ, ರೋಗದ ಲಕ್ಷಣಗಳು, ಲಸಿಕೆ ವೇಳಾಪಟ್ಟಿ ಮತ್ತು ಆರೋಗ್ಯ ಎಚ್ಚರಿಕೆಗಳ ಬಗ್ಗೆ ನಿಮಗೆ ಸಹಾಯ ಮಾಡಬಹುದು. ನಾನು ನಿಮಗೆ ಹೇಗೆ ಸಹಾಯ ಮಾಡಬಹುದು?",
        "vaccination_info": "ಲಸಿಕೆ ನೀಡುವುದು ಒಂದು ಮುಖ್ಯ ನಿರೋಧಕ ಕ್ರಮ. ದಯವಿಟ್ಟು ನಿಮ್ಮ ಸ್ಥಳೀಯ ಆರೋಗ್ಯ ಸೇವಾ ಒದಗಿಸುವವರನ್ನು ಸಂಪರ್ಕಿಸಿ ಅಥವಾ ನಿಮ್ಮ ವಯಸ್ಸಿನ ಗುಂಪಿಗೆ ಸೂಕ್ತವಾದ ಲಸಿಕೆ ವೇಳಾಪಟ್ಟಿಗಾಗಿ ಸರ್ಕಾರಿ ಆರೋಗ್ಯ ಕೇಂದ್ರವನ್ನು ಭೇಟಿ ಮಾಡಿ.",
        "symptom_query": "ನೀವು ಲಕ್ಷಣಗಳನ್ನು ಅನುಭವಿಸಿದರೆ, ಆರೋಗ್ಯ ವೃತ್ತಿಪರರನ್ನು ಸಂಪರ್ಕಿಸುವುದು ಮುಖ್ಯ. ತುರ್ತು ಪರಿಸ್ಥಿತಿಗಳಲ್ಲಿ ತಕ್ಷಣ ತುರ್ತು ಸೇವೆಗಳನ್ನು ಸಂಪರ್ಕಿಸಿ.",
        "disease_query": "ನಿರ್ದಿಷ್ಟ ರೋಗಗಳ ಬಗ್ಗೆ ನಿರೋಧನ ಮತ್ತು ಚಿಕಿತ್ಸೆ ಕುರಿತ ಮಾಹಿತಿಗಾಗಿ ಆರೋಗ್ಯ ವೃತ್ತಿಪರರನ್ನು ಸಂಪರ್ಕಿಸಿ. ಲಸಿಕೆ ಮತ್ತು ಆರೋಗ್ಯಕರ ಅಭ್ಯಾಸಗಳು ನಿರೋಧನಕ್ಕೆ ಶಿಫಾರಸು ಮಾಡಲ್ಪಡುತ್ತವೆ.",
        "default": "ನಾನು ಆರೋಗ್ಯ ಮಾಹಿತಿಯಲ್ಲಿ ಸಹಾಯ ಮಾಡಲು ಇಲ್ಲಿದ್ದೇನೆ. ನೀವು ಲಸಿಕೆಗಳು, ರೋಗದ ಲಕ್ಷಣಗಳು, ನಿರೋಧಕ ಕ್ರಮಗಳು ಅಥವಾ ಆರೋಗ್ಯ ಎಚ್ಚರಿಕೆಗಳ ಬಗ್ಗೆ ನನಗೆ ಕೇಳಬಹುದು. ವಿಶೇಷ ವೈದ್ಯಕೀಯ ಸಲಹೆಗಾಗಿ ಅರ್ಹತೆಯಿರುವ ಆರೋಗ್ಯ ವೃತ್ತಿಪರರನ್ನು ಸಂಪರ್ಕಿಸಿ."
    },

    "ml": {
        "greeting": "നമസ്കാരം! ഞാൻ നിങ്ങളുടെ ആരോഗ്യ സഹായിയാണ്. ഞാൻ മുൻകരുതൽ ആരോഗ്യമേഖല, രോഗലക്ഷണങ്ങൾ, വാക്സിൻ ഷെഡ്യൂളുകൾ, ആരോഗ്യ മുന്നറിയിപ്പുകൾ എന്നിവയെക്കുറിച്ച് നിങ്ങളെ സഹായിക്കാം. ഇന്ന് ഞാൻ നിങ്ങളെ എങ്ങനെ സഹായിക്കാം?",
        "vaccination_info": "വാക്സിനേഷൻ ഒരു പ്രധാന പ്രതിരോധ നടപടിയാണ്. ദയവായി നിങ്ങളുടെ പ്രാദേശിക ആരോഗ്യ സേവാ ദാതാവിനെ സമീപിക്കുക അല്ലെങ്കിൽ നിങ്ങളുടെ പ്രായത്തിനനുസരിച്ചുള്ള വാക്സിൻ ഷെഡ്യൂളിനായി സർക്കാർ ആരോഗ്യ കേന്ദ്രത്തിൽ എത്തുക.",
        "symptom_query": "നിങ്ങൾക്ക് ലക്ഷണങ്ങൾ അനുഭവപ്പെടുകയാണെങ്കിൽ, ആരോഗ്യ വിദഗ്ധന്റെ ഉപദേശം തേടുന്നത് പ്രധാനമാണ്. അടിയന്തര സാഹചര്യങ്ങളിൽ ഉടൻ തന്നെ അടിയന്തര സേവനങ്ങളുമായി ബന്ധപ്പെടുക.",
        "disease_query": "പ്രത്യേക രോഗങ്ങളെക്കുറിച്ചുള്ള, പ്രതിരോധവും ചികിത്സയും സംബന്ധിച്ച വിവരങ്ങൾക്ക് ആരോഗ്യ വിദഗ്ധരുടെ ഉപദേശം തേടുക. വാക്സിനേഷനും ആരോഗ്യകരമായ ജീവിതശൈലിയും വഴി പ്രതിരോധം എപ്പോഴും ശുപാർശ ചെയ്യപ്പെടുന്നു.",
        "default": "ഞാൻ ആരോഗ്യ വിവരത്തിൽ നിങ്ങളെ സഹായിക്കാൻ ഇവിടെ ഉണ്ട. നിങ്ങൾക്ക് വാക്സിനേഷൻ, രോഗലക്ഷണങ്ങൾ, മുൻകരുതൽ നടപടികൾ അല്ലെങ്കിൽ ആരോഗ്യ മുന്നറിയിപ്പുകൾ സംബന്ധിച്ച വിവരങ്ങൾ ചോദിക്കാം. പ്രത്യേക മെഡിക്കൽ ഉപദേശങ്ങൾക്ക് യോഗ്യതയുള്ള ആരോഗ്യ വിദഗ്ധനെ സമീപിക്കുക."
    },

    "ur": {
        "greeting": "السلام علیکم! میں آپ کا صحت معاون ہوں۔ میں آپ کو احتیاطی صحت کی دیکھ بھال، بیماری کی علامات، ویکسینیشن شیڈول اور صحت کی خبرداریاں فراہم کرنے میں مدد کر سکتا ہوں۔ میں آج آپ کی کیسے مدد کر سکتا ہوں؟",
        "vaccination_info": "ویکسینیشن ایک اہم حفاظتی اقدام ہے۔ براہ کرم اپنے مقامی ہیلتھ کیئر فراہم کنندہ سے مشورہ کریں یا اپنے عمر کے مناسب ویکسین شیڈول کے لیے سرکاری صحت مرکز سے رجوع کریں۔",
        "symptom_query": "اگر آپ علامات محسوس کر رہے ہیں تو صحت کے ماہر سے مشورہ کرنا ضروری ہے۔ ہنگامی حالات میں فوری طور پر ہنگامی خدمات سے رابطہ کریں۔",
        "disease_query": "مخصوص بیماریوں، روک تھام اور علاج کے بارے میں معلومات کے لیے صحت کے ماہرین سے رابطہ کریں۔ ویکسینیشن اور صحت مند عادات کے ذریعے روک تھام ہمیشہ تجویز کی جاتی ہے۔",
        "default": "میں صحت سے متعلق معلومات میں آپ کی مدد کے لیے یہاں ہوں۔ آپ مجھ سے ویکسینیشن، بیماری کی علامات، احتیاطی اقدامات یا صحت کی خبرداریاں کے بارے میں پوچھ سکتے ہیں۔ مخصوص طبی مشورے کے لیے براہ کرم کسی مستند صحت پیشہ ور سے رجوع کریں۔"
    }
}

class TranslationService:
    def __init__(self):
        self.translator_type = "offline"
        # Cache for translations
        self.translation_cache: Dict[str, Dict[str, str]] = {}
    
    async def translate(
        self, 
        text: str, 
        target_lang: str, 
        source_lang: str = "en"
    ) -> str:
        """Translate text to target language using offline dictionary"""
        if target_lang == source_lang or target_lang not in SUPPORTED_LANGUAGES:
            return text
        
        # Check cache first
        cache_key = f"{source_lang}:{target_lang}:{text}"
        if cache_key in self.translation_cache:
            return self.translation_cache[cache_key]
        
        # For now, return English text for complex sentences
        # In a full implementation, you would use a local translation model
        # or more comprehensive dictionary
        
        # Check for common phrases
        # First, try to match the entire text to a known English common response
        text_stripped = text.strip()
        for key, en_val in COMMON_RESPONSES.get("en", {}).items():
            if text_stripped.lower() == en_val.strip().lower():
                # Return the canned response in target language if available
                return COMMON_RESPONSES.get(target_lang, {}).get(key, en_val)

        # If the caller passed a response key directly (e.g., 'greeting'), handle it
        if text_stripped in COMMON_RESPONSES.get(target_lang, {}):
            return COMMON_RESPONSES[target_lang][text_stripped]
        
        # Check for individual words
        words = text.split()
        translated_words = []
        for word in words:
            word_lower = word.lower().strip('.,!?;:')
            if word_lower in TRANSLATION_DICTIONARY:
                if target_lang in TRANSLATION_DICTIONARY[word_lower]:
                    translated_words.append(TRANSLATION_DICTIONARY[word_lower][target_lang])
                else:
                    translated_words.append(word)
            else:
                translated_words.append(word)
        
        result = " ".join(translated_words)
        
        # Cache the result
        self.translation_cache[cache_key] = result
        return result
    
    async def detect_language(self, text: str) -> str:
        """Detect language of text (simple heuristic-based detection)"""
        # Simple keyword-based detection
        text_lower = text.lower()
        
        # Hindi keywords
        hindi_chars = "अआइईउऊऋएऐओऔकखगघङचछजझञटठडढणतथदधनपफबभमयरलवशषसह"
        if any(char in text for char in hindi_chars):
            return "hi"
        
        # Tamil keywords
        tamil_chars = "அஆஇஈஉஊஎஏஐஒஓஔகஙசஞடணதனபமயரலவஶஷஸஹ"
        if any(char in text for char in tamil_chars):
            return "ta"
        
        # Telugu keywords
        telugu_chars = "అఆఇఈఉఊఋఌఎఏఐఒఓఔకఖగఘఙచఛజఝఞటఠడఢణతథదధనపఫబభమయరలవశషసహ"
        if any(char in text for char in telugu_chars):
            return "te"
        
        # Bengali keywords
        bengali_chars = "অআইঈউঊঋএঐওঔকখগঘঙচছজঝঞটঠডঢণতথদধনপফবভমযরলশষসহ"
        if any(char in text for char in bengali_chars):
            return "bn"
        
        # Default to English
        return "en"
    
    def get_supported_languages(self) -> Dict[str, str]:
        """Get list of supported languages"""
        return SUPPORTED_LANGUAGES
    
    def translate_common_response(self, response_type: str, language: str) -> str:
        """Translate common response types"""
        if language in COMMON_RESPONSES:
            return COMMON_RESPONSES[language].get(response_type, COMMON_RESPONSES["en"].get(response_type, ""))
        return COMMON_RESPONSES["en"].get(response_type, "")

