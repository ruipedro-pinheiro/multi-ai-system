// ========== SESSION MANAGEMENT (FIXED) ==========
async function initDemoSession() {
    try {
        // GET session from server (uses HttpOnly cookie automatically)
        const response = await fetch('/demo/session', {
            method: 'GET',
            credentials: 'include'  // IMPORTANT: Send cookies
        });
        
        if (!response.ok) throw new Error('Failed to load session');
        
        demoSession = await response.json();
        
        // Update UI with remaining queries
        updateQueryCounter(demoSession.queries_remaining);
        
        // Restore previous messages (if any)
        if (demoSession.messages && demoSession.messages.length > 0) {
            console.log(`✅ Restoring ${demoSession.messages.length} messages from session`);
            
            const messagesDiv = document.getElementById('hero-messages');
            if (messagesDiv) {
                // Clear welcome message
                messagesDiv.innerHTML = '';
                
                // Restore all messages
                demoSession.messages.forEach(msg => {
                    if (msg.role === 'user') {
                        addHeroMessage('user', msg.content);
                    } else if (msg.role === 'assistant') {
                        addHeroMessage('ai', msg.content, null, msg.author.toUpperCase());
                    }
                });
                
                // Scroll to bottom
                messagesDiv.scrollTop = messagesDiv.scrollHeight;
            }
        }
        
        console.log('✅ Demo session initialized:', demoSession);
        return demoSession;
    } catch (error) {
        console.error('❌ Session init failed:', error);
        // Don't show error - it's normal for first-time visitors
        return {
            session_id: null,
            query_count: 0,
            queries_remaining: 10,
            max_queries: 10,
            messages: []
        };
    }
}
