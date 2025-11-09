#!/usr/bin/env python3
import re

with open("/home/chika/app/frontend-v1/index.html", "r") as f:
    content = f.read()

# Find the hero-messages div closing tag and input area
pattern = r'(</div>\s*<!-- Input Area -->)'

replacement = r'''</div>

                <!-- Query Counter & Reset -->
                <div style="display: flex; justify-content: space-between; align-items: center; padding: 12px 32px 8px 32px;">
                    <div id="query-counter" style="color: var(--chika-primary); font-size: 0.875rem; font-weight: 600;">
                        10 questions remaining
                    </div>
                    <button onclick="resetConversation()" style="background: rgba(239, 68, 68, 0.1); border: 1px solid rgba(239, 68, 68, 0.3); border-radius: 8px; padding: 6px 12px; color: #ef4444; font-size: 0.875rem; cursor: pointer; transition: all 0.2s; font-weight: 600;">
                        🔄 New Conversation
                    </button>
                </div>
                
                <!-- Input Area -->'''

content = re.sub(pattern, replacement, content, count=1)

# Add resetConversation function before closing script tag
reset_func = '''
async function resetConversation() {
    if (!confirm("Start a new conversation? (Your query limit stays the same)")) return;
    
    try {
        const response = await fetch("/demo/session/reset", {
            method: "DELETE",
            credentials: "include"
        });
        
        if (!response.ok) throw new Error("Reset failed");
        
        const data = await response.json();
        
        // Clear messages UI
        const messagesDiv = document.getElementById("hero-messages");
        if (messagesDiv) {
            messagesDiv.innerHTML = '<h4 style="color: var(--text-secondary); text-align: center; padding: 40px 0;">💬 Ask me anything!</h4>';
        }
        
        // Update counter
        updateQueryCounter(data.queries_remaining);
        
        console.log("✅ Conversation reset");
    } catch (error) {
        console.error("❌ Reset error:", error);
        alert("Failed to reset. Please refresh the page.");
    }
}

'''

# Find last occurrence of closing script tag and add function before it
last_script_idx = content.rfind('</script>')
if last_script_idx != -1:
    content = content[:last_script_idx] + reset_func + content[last_script_idx:]

with open("/home/chika/app/frontend-v1/index.html", "w") as f:
    f.write(content)

print("✅ Reset button + counter added to frontend")
