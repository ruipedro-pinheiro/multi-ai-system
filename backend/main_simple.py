"""Chika Backend V1 - SIMPLE (NO ROOMS!)

Refacto: User → Message → Multi-AI Responses (direct!)
"""
from fastapi import FastAPI, HTTPException, Request
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, validator
from typing import Optional, List, Dict
from datetime import datetime
from slowapi import Limiter, _rate_limit_exceeded_handler
from slowapi.util import get_remote_address
from slowapi.errors import RateLimitExceeded

# Config
from config import settings
from providers.llm_router import LLMRouter
from orchestrator.smart_router import SmartRouter
from orchestrator.collaborator import AICollaborator

# Security
from security.input_sanitizer import InputSanitizer
from security.prompt_filter import PromptSecurityFilter
from security.headers import SecurityHeadersMiddleware

# Initialize Rate Limiter
limiter = Limiter(key_func=get_remote_address)

# Initialize FastAPI
app = FastAPI(
    title="Chika API V1",
    version="1.0.0",
    description="Multi-AI chat platform - Simple & Direct"
)

# Rate limiting
app.state.limiter = limiter
app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)

# CORS - Allow all origins for demo (Cloudflare Tunnel blocks specific origins)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Allow all for now - Cloudflare tunnel issue
    allow_credentials=False,  # Must be False with allow_origins=["*"]
    allow_methods=["GET", "POST", "OPTIONS"],
    allow_headers=["*"],
    max_age=3600
)
app.add_middleware(SecurityHeadersMiddleware)

# Initialize LLM Router
llm_router = LLMRouter()
smart_router = SmartRouter()


# === Pydantic Models === #

class ChatRequest(BaseModel):
    """Simple chat request - NO ROOMS!"""
    content: str
    preferred_ais: Optional[List[str]] = None  # If None, SmartRouter decides
    
    @validator('content')
    def validate_content(cls, v):
        if not v or len(v.strip()) == 0:
            raise ValueError("Message cannot be empty")
        
        if len(v) > 50000:
            raise ValueError("Message too long (max 50000 chars)")
        
        # SECURITY: Sanitize
        sanitized, is_safe, error = InputSanitizer.sanitize_message(v)
        if not is_safe:
            raise ValueError(f"Invalid message: {error}")
        
        # SECURITY: Check prompt injection
        is_safe_prompt, reason = PromptSecurityFilter.is_safe(sanitized)
        if not is_safe_prompt:
            raise ValueError(f"Unsafe prompt: {reason}")
        
        return sanitized
    
    @validator('preferred_ais')
    def validate_ais(cls, v):
        if v is None:
            return None
        
        allowed = ['claude', 'gpt', 'gemini', 'llama', 'ollama', 'mock']
        for ai in v:
            if ai not in allowed:
                raise ValueError(f"Invalid AI: {ai}. Allowed: {allowed}")
        return v


class AIResponse(BaseModel):
    """Single AI response"""
    ai: str
    content: str
    timestamp: str
    reasoning: Optional[str] = None


class ChatResponse(BaseModel):
    """Chat response with multiple AI answers"""
    user_message: Dict
    ai_responses: List[AIResponse]
    selected_ais: List[str]
    intent_analysis: Optional[Dict] = None


# === Routes === #

@app.get("/")
async def root():
    """API info"""
    return {
        "name": "Chika V1",
        "version": "1.0.0",
        "available_ais": llm_router.get_available_providers(),
        "endpoints": {
            "chat": "POST /chat",
            "health": "GET /health"
        }
    }


@app.get("/health")
async def health():
    """Health check"""
    available = llm_router.get_available_providers()
    return {
        "status": "healthy",
        "available_ais": available,
        "timestamp": datetime.now().isoformat()
    }


@app.post("/chat", response_model=ChatResponse)
@limiter.limit("10/minute")  # Max 10 requests per minute per IP
async def chat(chat_request: ChatRequest, request: Request):
    """
    Send message to multi-AI system
    
    NO ROOMS! Direct user → message → multi-AI responses
    """
    try:
        # User message
        user_msg = {
            "role": "user",
            "content": chat_request.content,
            "timestamp": datetime.now().isoformat()
        }
        
        # Determine which AIs to use
        if chat_request.preferred_ais:
            # User specified AIs
            selected_ais = chat_request.preferred_ais
            intent_analysis = None
        else:
            # SmartRouter decides
            available_ais = llm_router.get_available_providers()
            selected_ais = smart_router.select_ais(chat_request.content, available_ais)
            intent_analysis = None  # SmartRouter does analysis internally
        
        # Get responses from selected AIs (SEQUENTIAL COLLABORATION!)
        ai_responses = []
        conversation_history = [user_msg]  # Build shared context
        
        for ai_id in selected_ais:
            try:
                # Call AI with FULL conversation history (including previous AI responses)
                response = await llm_router.chat(
                    messages=conversation_history,
                    preferred_provider=ai_id
                )
                
                # Create AI response object
                ai_response = AIResponse(
                    ai=ai_id,
                    content=response,
                    timestamp=datetime.now().isoformat()
                )
                ai_responses.append(ai_response)
                
                # ADD THIS AI'S RESPONSE TO HISTORY (so next AI sees it!)
                conversation_history.append({
                    "role": "assistant",
                    "content": f"[{ai_id.upper()}]: {response}",
                    "timestamp": datetime.now().isoformat()
                })
                
            except Exception as e:
                # If one AI fails, continue with others
                print(f"❌ {ai_id} failed: {e}")
                continue
        
        # If ALL AIs failed, use mock
        if not ai_responses:
            mock_response = await llm_router.chat(
                messages=[user_msg],
                preferred_provider="mock"
            )
            
            ai_responses.append(AIResponse(
                ai="mock",
                content=mock_response,
                timestamp=datetime.now().isoformat(),
                reasoning="Fallback: All real AIs unavailable"
            ))
            selected_ais = ["mock"]
        
        return ChatResponse(
            user_message=user_msg,
            ai_responses=ai_responses,
            selected_ais=selected_ais,
            intent_analysis=intent_analysis
        )
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
