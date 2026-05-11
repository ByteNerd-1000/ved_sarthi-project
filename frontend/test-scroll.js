// TEST SCRIPT - Add this to browser console to test scrolling
// This will add multiple messages to verify scrolling works

function testScrolling() {
    // Remove welcome screen
    const welcomeScreen = document.querySelector('.welcome-screen');
    if (welcomeScreen) {
        welcomeScreen.remove();
    }

    const chatMessages = document.getElementById('chatMessages');
    
    // Add 15 test messages to force scrolling
    for (let i = 1; i <= 15; i++) {
        // User message
        const userMsg = document.createElement('div');
        userMsg.className = 'message user';
        userMsg.innerHTML = `
            <div class="message-avatar">👤</div>
            <div class="message-content">
                <div class="message-text">Test message ${i} - This is a user message to test scrolling functionality.</div>
                <div class="message-time">${new Date().toLocaleTimeString('en-US', { hour: '2-digit', minute: '2-digit' })}</div>
            </div>
        `;
        chatMessages.appendChild(userMsg);

        // AI message
        const aiMsg = document.createElement('div');
        aiMsg.className = 'message ai';
        aiMsg.innerHTML = `
            <div class="message-avatar">🏥</div>
            <div class="message-content">
                <div class="message-text">AI Response ${i} - This is an AI response message. The chat area should scroll when there are many messages like this.</div>
                <div class="message-time">${new Date().toLocaleTimeString('en-US', { hour: '2-digit', minute: '2-digit' })}</div>
            </div>
        `;
        chatMessages.appendChild(aiMsg);
    }

    // Scroll to bottom
    chatMessages.scrollTop = chatMessages.scrollHeight;
    
    console.log('✅ Added 30 test messages. Try scrolling up and down!');
    console.log('📏 Chat Messages Height:', chatMessages.scrollHeight);
    console.log('📏 Chat Messages Visible Height:', chatMessages.clientHeight);
    console.log('📏 Can Scroll:', chatMessages.scrollHeight > chatMessages.clientHeight);
}

// Run the test
testScrolling();
