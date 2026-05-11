// DOM Elements
const menuToggle = document.getElementById('menuToggle');
const sidebar = document.getElementById('sidebar');
const chatInput = document.getElementById('chatInput');
const sendBtn = document.getElementById('sendBtn');
const chatMessages = document.getElementById('chatMessages');
const voiceBtn = document.getElementById('voiceBtn');
const symptomInput = document.getElementById('symptomInput');
const languageSelect = document.getElementById('languageSelect');
const chatSection = document.getElementById('chatSection');
const historySection = document.getElementById('historySection');
const profileSection = document.getElementById('profileSection');
const emergencySection = document.getElementById('emergencySection');
const profileNameInput = document.getElementById('profileName');
const profileHeightInput = document.getElementById('profileHeight');
const profileWeightInput = document.getElementById('profileWeight');
const saveProfileBtn = document.getElementById('saveProfileBtn');
const symptomCard = document.getElementById('symptomCard');
const tipsCard = document.getElementById('tipsCard');
const recentQueriesCard = document.getElementById('recentQueriesCard');
const findHospitalsNav = document.getElementById('findHospitalsNav');
const headerProfileIcon = document.getElementById('headerProfileIcon');
const profilePopup = document.getElementById('profilePopup');
const closeProfilePopupBtn = document.getElementById('closeProfilePopup');
const popupProfileName = document.getElementById('popupProfileName');
const popupProfileHeight = document.getElementById('popupProfileHeight');
const popupProfileWeight = document.getElementById('popupProfileWeight');

// ── Backend configuration ────────────────────────────────────────────────────
// Replace RENDER_BACKEND_URL with your actual Render service URL after deploying,
// e.g. "https://veda-sarthi-backend.onrender.com"
// Leave as empty string to fall back to localhost during local development.
const RENDER_BACKEND_URL = '';   // ← PASTE YOUR RENDER URL HERE AFTER DEPLOY

const API_BASE_URL = RENDER_BACKEND_URL || 'http://localhost:8002';
// ─────────────────────────────────────────────────────────────────────────────

// Persistent user id (so history works across refresh)
let userId = localStorage.getItem('veda_sarthi_user_id');
if (!userId) {
    userId = 'user_' + Date.now();
    localStorage.setItem('veda_sarthi_user_id', userId);
}

// Current language to send to backend
let currentLanguage = languageSelect ? languageSelect.value || 'en' : 'en';

// Mobile menu toggle
if (menuToggle && sidebar) {
    menuToggle.addEventListener('click', (e) => {
        e.stopPropagation();
        sidebar.classList.toggle('sidebar-visible');
    });

    // Close sidebar when clicking outside on mobile
    document.addEventListener('click', (e) => {
        if (window.innerWidth <= 768) {
            if (!sidebar.contains(e.target) && !menuToggle.contains(e.target)) {
                sidebar.classList.remove('sidebar-visible');
            }
        }
    });

    // Prevent sidebar from closing when clicking inside it
    sidebar.addEventListener('click', (e) => {
        e.stopPropagation();
    });
}

// Auto-resize textarea
if (chatInput) {
    chatInput.addEventListener('input', function() {
        this.style.height = 'auto';
        this.style.height = Math.min(this.scrollHeight, 120) + 'px';
    });
}

// Send message function (calls FastAPI backend)
async function sendMessage() {
    const message = chatInput.value.trim();
    if (!message) return;

    // Remove welcome screen if exists
    const welcomeScreen = document.querySelector('.welcome-screen');
    if (welcomeScreen) {
        welcomeScreen.remove();
    }

    // Add user message
    addMessage(message, 'user');
    chatInput.value = '';
    chatInput.style.height = 'auto';

    // Show typing indicator
    showTypingIndicator();

    try {
        const response = await fetch(`${API_BASE_URL}/api/chatbot/chat`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
                'Accept': 'application/json'
            },
            body: JSON.stringify({
                message,
                user_id: userId,
                language: currentLanguage || 'en'
            })
        });

        if (!response.ok) {
            throw new Error(`HTTP ${response.status}`);
        }

        const data = await response.json();
        removeTypingIndicator();
        addAIBackendResponse(data.response || 'Sorry, I could not understand the response from the server.');
    } catch (error) {
        console.error('Error calling backend:', error);
        removeTypingIndicator();
        addAIBackendResponse('Sorry, I could not reach the server. Please make sure the backend is running on http://localhost:8000.');
    }
}

// Add message to chat
function addMessage(text, type) {
    const messageDiv = document.createElement('div');
    messageDiv.className = `message ${type}`;
    
    const avatar = document.createElement('div');
    avatar.className = 'message-avatar';
    avatar.textContent = type === 'user' ? '👤' : '🏥';
    
    const content = document.createElement('div');
    content.className = 'message-content';
    
    const textDiv = document.createElement('div');
    textDiv.className = 'message-text';
    textDiv.textContent = text;
    
    const time = document.createElement('div');
    time.className = 'message-time';
    time.textContent = new Date().toLocaleTimeString('en-US', { 
        hour: '2-digit', 
        minute: '2-digit' 
    });
    
    content.appendChild(textDiv);
    content.appendChild(time);
    messageDiv.appendChild(avatar);
    messageDiv.appendChild(content);
    
    chatMessages.appendChild(messageDiv);
    scrollToBottom();
}

// Add AI response coming from backend (plain text)
function addAIBackendResponse(text) {
    const messageDiv = document.createElement('div');
    messageDiv.className = 'message ai';

    const avatar = document.createElement('div');
    avatar.className = 'message-avatar';
    avatar.textContent = '🏥';

    const content = document.createElement('div');
    content.className = 'message-content';

    const textDiv = document.createElement('div');
    textDiv.className = 'message-text';
    // Use textContent to avoid injecting HTML
    textDiv.textContent = text;

    const time = document.createElement('div');
    time.className = 'message-time';
    time.textContent = new Date().toLocaleTimeString('en-US', {
        hour: '2-digit',
        minute: '2-digit'
    });

    content.appendChild(textDiv);
    content.appendChild(time);
    messageDiv.appendChild(avatar);
    messageDiv.appendChild(content);

    chatMessages.appendChild(messageDiv);
    scrollToBottom();
}

// Add AI response with contextual content
function addAIResponse(query) {
    const messageDiv = document.createElement('div');
    messageDiv.className = 'message ai';
    
    const avatar = document.createElement('div');
    avatar.className = 'message-avatar';
    avatar.textContent = '🏥';
    
    const content = document.createElement('div');
    content.className = 'message-content';
    
    const textDiv = document.createElement('div');
    textDiv.className = 'message-text';
    
    // Generate contextual response based on query
    const lowerQuery = query.toLowerCase();
    let response = '';
    
    if (lowerQuery.includes('headache') || lowerQuery.includes('fever')) {
        response = `<h4>Symptom Analysis</h4>
        <p>Based on your symptoms of headache and mild fever, here are some recommendations:</p>
        <ul>
            <li><strong>Rest:</strong> Get adequate sleep and avoid stress</li>
            <li><strong>Hydration:</strong> Drink plenty of fluids</li>
            <li><strong>Temperature:</strong> Monitor your fever regularly</li>
            <li><strong>Medication:</strong> Consider over-the-counter pain relievers</li>
        </ul>
        <p>⚠️ If symptoms worsen or persist for more than 3 days, please consult a healthcare professional.</p>`;
    } else if (lowerQuery.includes('breakfast') || lowerQuery.includes('nutrition') || lowerQuery.includes('diet') || lowerQuery.includes('food')) {
        response = `<h4>Healthy Breakfast Recommendations</h4>
        <p>Here are some nutritious breakfast options:</p>
        <ul>
            <li><strong>Oatmeal:</strong> Rich in fiber and keeps you full longer</li>
            <li><strong>Greek Yogurt:</strong> High in protein with probiotics</li>
            <li><strong>Whole Grain Toast:</strong> With avocado or nut butter</li>
            <li><strong>Smoothie Bowl:</strong> Packed with fruits and nuts</li>
            <li><strong>Eggs:</strong> Excellent source of protein and vitamins</li>
        </ul>
        <p>💡 Tip: Include protein, healthy fats, and complex carbs for sustained energy.</p>`;
    } else if (lowerQuery.includes('exercise') || lowerQuery.includes('back pain') || lowerQuery.includes('workout')) {
        response = `<h4>Exercises for Back Pain Relief</h4>
        <p>Here are some gentle exercises that can help:</p>
        <ul>
            <li><strong>Cat-Cow Stretch:</strong> Improves spinal flexibility</li>
            <li><strong>Child's Pose:</strong> Relaxes lower back muscles</li>
            <li><strong>Pelvic Tilts:</strong> Strengthens core muscles</li>
            <li><strong>Knee-to-Chest:</strong> Stretches lower back</li>
            <li><strong>Bird Dog:</strong> Builds core stability</li>
        </ul>
        <p>⚠️ Start slowly and stop if you feel pain. Consult a physiotherapist for persistent issues.</p>`;
    } else if (lowerQuery.includes('stress') || lowerQuery.includes('anxiety') || lowerQuery.includes('mental')) {
        response = `<h4>Stress Management Techniques</h4>
        <p>Natural ways to reduce stress and anxiety:</p>
        <ul>
            <li><strong>Deep Breathing:</strong> Practice 5-10 minutes daily</li>
            <li><strong>Meditation:</strong> Start with guided meditation apps</li>
            <li><strong>Physical Activity:</strong> Regular exercise releases endorphins</li>
            <li><strong>Sleep Hygiene:</strong> Maintain a consistent sleep schedule</li>
            <li><strong>Social Connection:</strong> Spend time with supportive people</li>
        </ul>
        <p>💡 Consider professional help if stress becomes overwhelming.</p>`;
    } else if (lowerQuery.includes('immunity') || lowerQuery.includes('immune')) {
        response = `<h4>Boosting Your Immune System</h4>
        <p>Best foods and practices for immunity:</p>
        <ul>
            <li><strong>Citrus Fruits:</strong> High in vitamin C</li>
            <li><strong>Garlic & Ginger:</strong> Natural immune boosters</li>
            <li><strong>Leafy Greens:</strong> Rich in vitamins and minerals</li>
            <li><strong>Probiotics:</strong> Yogurt and fermented foods</li>
            <li><strong>Adequate Sleep:</strong> 7-8 hours nightly</li>
            <li><strong>Regular Exercise:</strong> Moderate activity is key</li>
        </ul>
        <p>💡 Stay hydrated and manage stress for optimal immune function.</p>`;
    } else if (lowerQuery.includes('sleep') || lowerQuery.includes('insomnia')) {
        response = `<h4>Better Sleep Practices</h4>
        <p>Tips for improving your sleep quality:</p>
        <ul>
            <li><strong>Consistent Schedule:</strong> Go to bed at the same time daily</li>
            <li><strong>Screen-Free Time:</strong> Avoid devices 1 hour before bed</li>
            <li><strong>Cool Environment:</strong> Keep bedroom around 65-68°F</li>
            <li><strong>Relaxation Routine:</strong> Try reading or meditation</li>
            <li><strong>Limit Caffeine:</strong> Avoid after 2 PM</li>
        </ul>
        <p>⚠️ Consult a doctor if sleep issues persist for more than 2 weeks.</p>`;
    } else if (lowerQuery.includes('water') || lowerQuery.includes('hydration') || lowerQuery.includes('dehydration')) {
        response = `<h4>Hydration Guidelines</h4>
        <p>Importance of proper hydration:</p>
        <ul>
            <li><strong>Daily Intake:</strong> Aim for 8-10 glasses (2-2.5 liters)</li>
            <li><strong>Signs of Dehydration:</strong> Dark urine, dry mouth, fatigue</li>
            <li><strong>Increase During:</strong> Exercise, hot weather, illness</li>
            <li><strong>Hydrating Foods:</strong> Watermelon, cucumber, oranges</li>
            <li><strong>Timing:</strong> Drink throughout the day consistently</li>
        </ul>
        <p>💡 Your body needs more water during physical activity and warm weather.</p>`;
    } else if (lowerQuery.includes('vitamin') || lowerQuery.includes('supplement')) {
        response = `<h4>Essential Vitamins & Supplements</h4>
        <p>Important nutrients for overall health:</p>
        <ul>
            <li><strong>Vitamin D:</strong> Bone health and immune function</li>
            <li><strong>Vitamin C:</strong> Antioxidant and immunity</li>
            <li><strong>Omega-3:</strong> Heart and brain health</li>
            <li><strong>B-Complex:</strong> Energy and nervous system</li>
            <li><strong>Calcium:</strong> Bone strength</li>
        </ul>
        <p>⚠️ Consult your doctor before starting any supplement regimen.</p>`;
    } else {
        response = `<h4>Health Advisory</h4>
        <p>Thank you for your question. I'm here to help with your health concerns.</p>
        <p>Based on what you've asked, I recommend:</p>
        <ul>
            <li>Consulting with a healthcare professional for personalized advice</li>
            <li>Maintaining a healthy lifestyle with balanced diet and exercise</li>
            <li>Monitoring your symptoms and keeping a health journal</li>
            <li>Staying hydrated and getting adequate rest</li>
        </ul>
        <p>💡 Is there anything specific about your health you'd like to know more about?</p>`;
    }
    
    textDiv.innerHTML = response;
    
    const time = document.createElement('div');
    time.className = 'message-time';
    time.textContent = new Date().toLocaleTimeString('en-US', { 
        hour: '2-digit', 
        minute: '2-digit' 
    });
    
    content.appendChild(textDiv);
    content.appendChild(time);
    messageDiv.appendChild(avatar);
    messageDiv.appendChild(content);
    
    chatMessages.appendChild(messageDiv);
    scrollToBottom();
}

// Show typing indicator
function showTypingIndicator() {
    const indicator = document.createElement('div');
    indicator.className = 'message ai';
    indicator.id = 'typingIndicator';
    
    const avatar = document.createElement('div');
    avatar.className = 'message-avatar';
    avatar.textContent = '🏥';
    
    const content = document.createElement('div');
    content.className = 'message-content';
    content.style.padding = '12px 20px';
    
    const dots = document.createElement('div');
    dots.className = 'typing-indicator';
    dots.innerHTML = '<div class="typing-dot"></div><div class="typing-dot"></div><div class="typing-dot"></div>';
    
    content.appendChild(dots);
    indicator.appendChild(avatar);
    indicator.appendChild(content);
    
    chatMessages.appendChild(indicator);
    scrollToBottom();
}

// Remove typing indicator
function removeTypingIndicator() {
    const indicator = document.getElementById('typingIndicator');
    if (indicator) indicator.remove();
}

// Scroll to bottom of chat
function scrollToBottom() {
    chatMessages.scrollTop = chatMessages.scrollHeight;
}

// Quick prompt variants for categories
const nutritionPrompts = [
    'What are some healthy breakfast options?',
    'Give me nutrition advice for a busy person.',
    'What should I eat to maintain a balanced diet?',
    'Suggest a simple healthy meal plan for one day.',
    'What are some healthy snacks I can eat between meals?'
];

const exercisePrompts = [
    'Show me simple exercises for back pain.',
    'Suggest a 15-minute daily exercise routine.',
    'What are some easy home workouts for beginners?',
    'Give me light exercises I can do without equipment.',
    'What exercises can help improve my posture?'
];

// Health tips translations by language
const healthTipsByLang = {
    en: [
        {
            title: 'Stay Hydrated',
            text: 'Drink at least 8 glasses of water daily to maintain optimal health and energy levels.'
        },
        {
            title: 'Morning Exercise',
            text: 'Start your day with 15 minutes of light stretching to boost circulation and mood.'
        },
        {
            title: 'Healthy Sleep',
            text: 'Aim for 7–8 hours of quality sleep each night for better cognitive function.'
        },
        {
            title: 'Screen Breaks',
            text: 'Take short breaks from screens every hour to reduce eye strain and fatigue.'
        },
        {
            title: 'Mindful Breathing',
            text: 'Practice 5 minutes of slow, deep breathing daily to reduce stress and improve focus.'
        }
    ],
    hi: [
        {
            title: 'हाइड्रेटेड रहें',
            text: 'दिन में कम से कम 8 गिलास साफ पानी पिएँ ताकि ऊर्जा और स्वास्थ्य बना रहे।'
        },
        {
            title: 'सुबह की कसरत',
            text: 'दिन की शुरुआत 10–15 मिनट हल्की स्ट्रेचिंग से करें, इससे रक्त संचार और मूड बेहतर होता है।'
        },
        {
            title: 'अच्छी नींद',
            text: 'हर रात 7–8 घंटे की गहरी नींद लेने की कोशिश करें, दिमाग और शरीर दोनों के लिए जरूरी है।'
        }
    ],
    mr: [
        {
            title: 'पुरेसा पाणी प्या',
            text: 'दररोज किमान 8 ग्लास स्वच्छ पाणी प्या, यामुळे ऊर्जास्तर आणि आरोग्य चांगले राहते.'
        },
        {
            title: 'सकाळची हलकी व्यायाम',
            text: 'दिवसाची सुरुवात 10–15 मिनिट हलक्या स्ट्रेचिंगने करा, रक्ताभिसरण आणि मूड सुधारतो.'
        },
        {
            title: 'गाढ झोप',
            text: 'दररोज 7–8 तासांची चांगली झोप घेणे मेंदू आणि शरीरासाठी महत्वाचे आहे.'
        }
    ]
    // Other languages will fall back to English if not defined
};

function updateHealthTipsForLanguage(lang) {
    const card = tipsCard;
    if (!card) return;

    const tipsConfig = healthTipsByLang[lang] || healthTipsByLang['en'];
    const tipElements = card.querySelectorAll('.health-tip');

    // Select random unique tips for display
    const pool = [...tipsConfig];
    const selected = [];
    while (selected.length < tipElements.length && pool.length > 0) {
        const idx = Math.floor(Math.random() * pool.length);
        selected.push(pool.splice(idx, 1)[0]);
    }

    tipElements.forEach((el, index) => {
        const cfg = selected[index] || tipsConfig[0];
        const titleEl = el.querySelector('.tip-title');
        const textEl = el.querySelector('.tip-text');
        if (titleEl && textEl && cfg) {
            titleEl.textContent = cfg.title;
            textEl.textContent = cfg.text;
        }
    });
}

// Section navigation
function showSection(section) {
    if (chatSection) {
        chatSection.style.display = (section === 'chat' || section === 'home' || section === 'symptoms' || section === 'tips') ? 'flex' : 'none';
    }
    if (historySection) {
        historySection.style.display = section === 'history' ? 'block' : 'none';
    }
    if (profileSection) {
        profileSection.style.display = section === 'profile' ? 'block' : 'none';
    }
    if (emergencySection) {
        emergencySection.style.display = section === 'emergency' ? 'block' : 'none';
    }

    // Right-panel behavior
    if (symptomCard) {
        symptomCard.style.display = section === 'symptoms' ? 'block' : 'none';
    }
    if (tipsCard) {
        tipsCard.style.display = section === 'tips' ? 'block' : 'none';
    }
    if (recentQueriesCard) {
        recentQueriesCard.style.display = (section === 'home' || section === 'chat') ? 'block' : 'none';
    }

    // When opening history, load from backend
    if (section === 'history') {
        loadChatHistory();
    }
}

function handleNavigation(section) {
    if (!section) {
        return;
    }
    const target = section;
    showSection(target);
    // When Home is clicked, reset to initial welcome screen
    if (target === 'home') {
        resetHomeScreen();
    }
}

// Load chat history from backend
async function loadChatHistory() {
    const container = document.getElementById('historyList');
    if (!container) return;

    container.innerHTML = '<p class="history-loading">Loading previous chats...</p>';

    try {
        const res = await fetch(`${API_BASE_URL}/api/chatbot/history/${encodeURIComponent(userId)}`);
        if (!res.ok) throw new Error(`HTTP ${res.status}`);

        const data = await res.json();
        if (!data || data.length === 0) {
            container.innerHTML = '<p class="history-empty">No previous chats found for this user.</p>';
            return;
        }

        const list = document.createElement('div');
        list.className = 'history-items';

        data.forEach(item => {
            const row = document.createElement('div');
            row.className = 'history-item';

            const q = document.createElement('div');
            q.className = 'history-question';
            q.textContent = item.message;

            const a = document.createElement('div');
            a.className = 'history-answer';
            a.textContent = item.response;

            const meta = document.createElement('div');
            meta.className = 'history-meta';
            meta.textContent = item.timestamp ? new Date(item.timestamp).toLocaleString() : '';

            row.appendChild(q);
            row.appendChild(a);
            row.appendChild(meta);

            list.appendChild(row);
        });

        container.innerHTML = '';
        container.appendChild(list);
    } catch (err) {
        console.error('Error loading history:', err);
        container.innerHTML = '<p class="history-error">Could not load chat history. Please try again.</p>';
    }
}

// Event listeners for sending messages
if (sendBtn) {
    sendBtn.addEventListener('click', sendMessage);
}

if (chatInput) {
    chatInput.addEventListener('keypress', (e) => {
        if (e.key === 'Enter' && !e.shiftKey) {
            e.preventDefault();
            sendMessage();
        }
    });
}

// Voice input functionality
let isRecording = false;

if (voiceBtn) {
    voiceBtn.addEventListener('click', () => {
        isRecording = !isRecording;
        voiceBtn.classList.toggle('recording', isRecording);
        
        if (isRecording) {
            voiceBtn.textContent = '⏸️';
            startVoiceRecording();
        } else {
            voiceBtn.textContent = '🎤';
            stopVoiceRecording();
        }
    });
}

// Voice recording functions
function startVoiceRecording() {
    console.log('Voice recording started...');
    const SpeechRecognition = window.SpeechRecognition || window.webkitSpeechRecognition;
    if (!SpeechRecognition) {
        alert('Voice input is not supported in this browser.');
        isRecording = false;
        if (voiceBtn) {
            voiceBtn.classList.remove('recording');
            voiceBtn.textContent = '🎤';
        }
        return;
    }

    const speechLangMap = {
        en: 'en-IN',
        hi: 'hi-IN',
        mr: 'mr-IN',
        ta: 'ta-IN',
        te: 'te-IN',
        bn: 'bn-IN',
        gu: 'gu-IN'
    };

    const rec = new SpeechRecognition();
    rec.lang = speechLangMap[currentLanguage] || 'en-IN';
    rec.interimResults = false;
    rec.maxAlternatives = 1;

    rec.onresult = (event) => {
        const transcript = event.results[0][0].transcript;
        if (chatInput) {
            chatInput.value = transcript;
            chatInput.style.height = 'auto';
        }
        // Auto-send after capture
        sendMessage();
    };

    rec.onerror = (event) => {
        console.error('Speech recognition error:', event.error);
    };

    rec.onend = () => {
        isRecording = false;
        if (voiceBtn) {
            voiceBtn.classList.remove('recording');
            voiceBtn.textContent = '🎤';
        }
    };

    try {
        rec.start();
    } catch (e) {
        console.error('Failed to start speech recognition:', e);
        isRecording = false;
        if (voiceBtn) {
            voiceBtn.classList.remove('recording');
            voiceBtn.textContent = '🎤';
        }
    }
}

function stopVoiceRecording() {
    console.log('Voice recording stopped...');
    // Recognition instance is local; onend handler will reset UI.
}

// Quick query function - called from HTML
function sendQuickQuery(query) {
    if (chatInput) {
        chatInput.value = query;
        sendMessage();
    }
}

// Category-based quick queries for more variety
function sendCategoryQuickQuery(category) {
    let prompt = '';
    if (category === 'nutrition') {
        const idx = Math.floor(Math.random() * nutritionPrompts.length);
        prompt = nutritionPrompts[idx];
    } else if (category === 'exercise') {
        const idx = Math.floor(Math.random() * exercisePrompts.length);
        prompt = exercisePrompts[idx];
    }
    if (prompt) {
        sendQuickQuery(prompt);
    }
}

// Symptom checker function - called from HTML
function checkSymptom() {
    if (symptomInput) {
        const symptom = symptomInput.value.trim();
        if (symptom) {
            sendQuickQuery(`I'm experiencing: ${symptom}`);
            symptomInput.value = '';
        }
    }
}

// Toggle voice for floating button - called from HTML
function toggleVoice() {
    if (voiceBtn) {
        voiceBtn.click();
    }
}

// Navigation item click handlers
document.querySelectorAll('.nav-item').forEach(item => {
    item.addEventListener('click', function() {
        // Remove active class from all items
        document.querySelectorAll('.nav-item').forEach(i => i.classList.remove('active'));
        // Add active class to clicked item
        this.classList.add('active');

        const section = this.dataset.section;
        handleNavigation(section);
        
        // Close sidebar on mobile after navigation
        if (window.innerWidth <= 768 && sidebar) {
            sidebar.classList.remove('sidebar-visible');
        }
    });
});

// Language selector change event
if (languageSelect) {
    languageSelect.addEventListener('change', function() {
        const languageName = this.options[this.selectedIndex].text;
        currentLanguage = this.value || 'en';
        console.log('Language changed to:', languageName);

        // Update health tips text for selected language
        updateHealthTipsForLanguage(currentLanguage);
        
        // Show notification
        const notification = document.createElement('div');
        notification.style.cssText = `
            position: fixed;
            top: 100px;
            right: 20px;
            background: linear-gradient(135deg, #0891B2 0%, #10B981 100%);
            color: white;
            padding: 16px 24px;
            border-radius: 12px;
            box-shadow: 0 8px 24px rgba(15, 23, 42, 0.12);
            z-index: 10000;
            animation: slideInRight 0.3s ease;
        `;
        notification.textContent = `Language changed to ${languageName}`;
        document.body.appendChild(notification);
        
        setTimeout(() => {
            notification.style.animation = 'slideOutRight 0.3s ease';
            setTimeout(() => notification.remove(), 300);
        }, 2000);
    });
}

// Responsive behavior
function handleResize() {
    if (window.innerWidth > 768 && sidebar) {
        sidebar.classList.remove('sidebar-visible');
    }
}

// Initial check
handleResize();

// Listen for window resize
window.addEventListener('resize', handleResize);

// Add CSS animations for notifications
const style = document.createElement('style');
style.textContent = `
    @keyframes slideInRight {
        from {
            transform: translateX(400px);
            opacity: 0;
        }
        to {
            transform: translateX(0);
            opacity: 1;
        }
    }
    
    @keyframes slideOutRight {
        from {
            transform: translateX(0);
            opacity: 1;
        }
        to {
            transform: translateX(400px);
            opacity: 0;
        }
    }
`;
document.head.appendChild(style);

// Profile persistence
function loadProfile() {
    if (!profileNameInput || !profileHeightInput || !profileWeightInput) return;

    const name = localStorage.getItem('veda_profile_name') || '';
    const height = localStorage.getItem('veda_profile_height') || '';
    const weight = localStorage.getItem('veda_profile_weight') || '';

    profileNameInput.value = name;
    profileHeightInput.value = height;
    profileWeightInput.value = weight;

    updateProfilePopupView();
}

function saveProfile() {
    if (!profileNameInput || !profileHeightInput || !profileWeightInput) return;

    localStorage.setItem('veda_profile_name', profileNameInput.value.trim());
    localStorage.setItem('veda_profile_height', profileHeightInput.value.trim());
    localStorage.setItem('veda_profile_weight', profileWeightInput.value.trim());

    alert('Profile saved successfully.');
    updateProfilePopupView();
}

if (saveProfileBtn) {
    saveProfileBtn.addEventListener('click', saveProfile);
}

// Update read-only popup view based on stored profile
function updateProfilePopupView() {
    if (!popupProfileName || !popupProfileHeight || !popupProfileWeight) return;
    const name = (profileNameInput && profileNameInput.value.trim()) || localStorage.getItem('veda_profile_name') || '';
    const height = (profileHeightInput && profileHeightInput.value.trim()) || localStorage.getItem('veda_profile_height') || '';
    const weight = (profileWeightInput && profileWeightInput.value.trim()) || localStorage.getItem('veda_profile_weight') || '';

    popupProfileName.textContent = name || 'Not set';
    popupProfileHeight.textContent = height ? `${height} cm` : 'Not set';
    popupProfileWeight.textContent = weight ? `${weight} kg` : 'Not set';
}

function showProfilePopup() {
    if (!profilePopup) return;
    updateProfilePopupView();
    profilePopup.style.display = 'block';
}

function hideProfilePopup() {
    if (!profilePopup) return;
    profilePopup.style.display = 'none';
}

if (headerProfileIcon) {
    headerProfileIcon.addEventListener('click', (e) => {
        e.stopPropagation();
        if (profilePopup && profilePopup.style.display === 'block') {
            hideProfilePopup();
        } else {
            showProfilePopup();
        }
    });
}

if (closeProfilePopupBtn) {
    closeProfilePopupBtn.addEventListener('click', (e) => {
        e.stopPropagation();
        hideProfilePopup();
    });
}

// Close popup when clicking outside
document.addEventListener('click', (e) => {
    if (!profilePopup || profilePopup.style.display !== 'block') return;
    if (profilePopup.contains(e.target) || (headerProfileIcon && headerProfileIcon.contains(e.target))) {
        return;
    }
    hideProfilePopup();
});

// Reset chat area back to initial welcome screen and clear messages
function resetHomeScreen() {
    if (!chatMessages) return;

    chatMessages.innerHTML = '';

    const welcome = document.createElement('div');
    welcome.className = 'welcome-screen';
    welcome.innerHTML = `
        <div class="welcome-icon">🏥</div>
        <h1 class="welcome-title">Welcome to Veda Sarthi</h1>
        <p class="welcome-subtitle">
            Your personal AI health assistant. Ask me about symptoms, medications, health tips, or get personalized wellness advice.
        </p>
        <div class="quick-actions">
            <div class="quick-action-card" onclick="sendCategoryQuickQuery('nutrition')">
                <div class="quick-action-icon">🥗</div>
                <div class="quick-action-title">Nutrition Advice</div>
                <div class="quick-action-desc">Get diet recommendations</div>
            </div>
            <div class="quick-action-card" onclick="sendCategoryQuickQuery('exercise')">
                <div class="quick-action-icon">🏃</div>
                <div class="quick-action-title">Exercise Tips</div>
                <div class="quick-action-desc">Fitness guidance</div>
            </div>
        </div>
    `;

    chatMessages.appendChild(welcome);
    scrollToBottom();
}

// Initialize the app
console.log('✅ Veda Sarthi AI Health Assistant - Initialized');
console.log('📱 Ready to assist with your health queries!');

// Initial state: show chat/home and load profile
handleNavigation('home');
loadProfile();
updateHealthTipsForLanguage(currentLanguage);

// Prevent double-tap zoom on mobile
let lastTouchEnd = 0;
document.addEventListener('touchend', function(event) {
    const now = Date.now();
    if (now - lastTouchEnd <= 300) {
        event.preventDefault();
    }
    lastTouchEnd = now;
}, false);

// Find hospitals via Google Maps (uses geolocation when available)
function openHospitalsInMaps() {
    const fallbackUrl = 'https://www.google.com/maps/search/hospitals+near+me';

    if (!navigator.geolocation) {
        window.open(fallbackUrl, '_blank');
        return;
    }

    navigator.geolocation.getCurrentPosition(
        (pos) => {
            const { latitude, longitude } = pos.coords;
            const url = `https://www.google.com/maps/search/hospitals/@${latitude},${longitude},14z`;
            window.open(url, '_blank');
        },
        (err) => {
            console.error('Geolocation error while finding hospitals:', err);
            window.open(fallbackUrl, '_blank');
        },
        { enableHighAccuracy: true, timeout: 8000, maximumAge: 0 }
    );
}

if (findHospitalsNav) {
    findHospitalsNav.addEventListener('click', (e) => {
        e.preventDefault();
        e.stopPropagation();
        openHospitalsInMaps();
    });
}
