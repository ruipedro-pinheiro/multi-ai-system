"""Chika Backend V1 - SIMPLE (NO ROOMS!)

Refacto: User → Message → Multi-AI Responses (direct!)
"""
from fastapi import FastAPI, HTTPException, Request, Depends, BackgroundTasks
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, EmailStr, validator
from typing import Optional, List, Dict
from datetime import datetime
from sqlalchemy.orm import Session
import os
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from slowapi import Limiter, _rate_limit_exceeded_handler
from slowapi.util import get_remote_address
from slowapi.errors import RateLimitExceeded

# Database
from database import get_db, init_db, WaitlistEntry

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


class WaitlistRequest(BaseModel):
    """Waitlist signup request"""
    email: EmailStr


class WaitlistResponse(BaseModel):
    """Waitlist signup response"""
    success: bool
    message: str
    total_signups: int


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
    """Health check endpoint"""
    return {
        "status": "healthy",
        "available_ais": list(llm_router.available_ais.keys()),
        "timestamp": datetime.utcnow().isoformat(),
        "env_check": {
            "gmail_configured": bool(os.getenv('GMAIL_APP_PASSWORD')),
            "db_configured": bool(os.getenv('DATABASE_URL'))
        }
    }


@app.post("/chat", response_model=ChatResponse)
@limiter.limit("10/minute")  # Max 10 requests per minute per IP
async def chat(chat_request: ChatRequest, request: Request):
    """
    Send message to multi-AI system
    
    NO ROOMS! Direct user → message → multi-AI responses
    """
    try:
        # User message with BREVITY INJECTION for landing page demo
        user_msg = {
            "role": "user",
            "content": f"{chat_request.content}\n\n[SYSTEM: Answer in 2-3 sentences maximum. Be concise and direct.]",
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
        
        # LANDING PAGE MODE: Show collaboration = ONE synthesized response
        # Step 1: Collect all AI opinions
        all_opinions = []
        conversation_history = [user_msg]
        
        for ai_id in selected_ais:
            try:
                response = await llm_router.chat(
                    messages=conversation_history,
                    preferred_provider=ai_id
                )
                all_opinions.append({"ai": ai_id, "opinion": response})
                
                # Share response with next AI
                conversation_history.append({
                    "role": "assistant",
                    "content": f"[{ai_id.upper()}]: {response}"
                })
            except Exception as e:
                print(f"❌ {ai_id} failed: {e}")
                continue
        
        # Step 2: If multiple AIs responded, synthesize into ONE answer
        if len(all_opinions) > 1:
            # Ask last AI to synthesize all opinions
            synthesis_prompt = {
                "role": "user",
                "content": f"Based on the discussion above, provide ONE concise final answer (2-3 sentences max)."
            }
            conversation_history.append(synthesis_prompt)
            
            final_response = await llm_router.chat(
                messages=conversation_history,
                preferred_provider=all_opinions[-1]["ai"]
            )
            
            # Return SINGLE synthesized response
            ai_responses = [AIResponse(
                ai="CHIKA",  # Unified AI collaboration
                content=final_response,
                timestamp=datetime.now().isoformat()
            )]
        elif len(all_opinions) == 1:
            # Single AI - return as is
            ai_responses = [AIResponse(
                ai=all_opinions[0]["ai"],
                content=all_opinions[0]["opinion"],
                timestamp=datetime.now().isoformat()
            )]
        else:
            # Fallback to mock
            mock_response = await llm_router.chat(
                messages=[user_msg],
                preferred_provider="mock"
            )
            ai_responses = [AIResponse(
                ai="mock",
                content=mock_response,
                timestamp=datetime.now().isoformat()
            )]
            selected_ais = ["mock"]
        
        return ChatResponse(
            user_message=user_msg,
            ai_responses=ai_responses,
            selected_ais=selected_ais,
            intent_analysis=intent_analysis
        )
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


# === EMAIL HELPER === #

def send_welcome_email(email: str, entry_id: int):
    """Send welcome email via Brevo API - BACKGROUND TASK!"""
    # Create NEW DB session for background task (important!)
    from database import SessionLocal
    import sib_api_v3_sdk
    from sib_api_v3_sdk.rest import ApiException
    db = SessionLocal()
    
    try:
        # Brevo credentials from environment
        brevo_api_key = os.getenv('BREVO_API_KEY')
        
        if not brevo_api_key:
            print(f"⚠️ Brevo not configured. Email not sent to {email}")
            db.close()
            return
        
        html = f"""
        <html>
        <body style="font-family: sans-serif; max-width: 600px; margin: 0 auto; padding: 20px;">
            <h2 style="color: #6366f1;">Welcome to CHIKA Beta! 🎉</h2>
            
            <p>Hey there!</p>
            
            <p>You're officially on the <strong>CHIKA beta waitlist</strong>! We're launching in <strong>December 2025</strong> with limited spots.</p>
            
            <h3>What happens next?</h3>
            <ul>
                <li>We'll email you when beta launches (December 2025)</li>
                <li>You'll get early access before public release</li>
                <li>Special pricing for early testers</li>
            </ul>
            
            <h3>Want to help shape CHIKA?</h3>
            <p>Reply to this email with feedback, feature requests, or just to say hi! We're building in public and love hearing from early supporters.</p>
            
            <p style="margin-top: 40px; color: #666;">
                - Pedro, Founder<br>
                <a href="https://github.com/ruipedro-pinheiro/CHIKA">Follow us on GitHub</a>
            </p>
            
            <p style="font-size: 12px; color: #999; margin-top: 40px;">
                You received this because you signed up on CHIKA waitlist. 
                Reply to unsubscribe.
            </p>
        </body>
        </html>
        """
        
        # Configure Brevo API
        configuration = sib_api_v3_sdk.Configuration()
        configuration.api_key['api-key'] = brevo_api_key
        api_instance = sib_api_v3_sdk.TransactionalEmailsApi(sib_api_v3_sdk.ApiClient(configuration))
        
        # Create email
        send_smtp_email = sib_api_v3_sdk.SendSmtpEmail(
            to=[{"email": email}],
            sender={"name": "CHIKA", "email": "noreply@chika.app"},
            subject="Welcome to CHIKA Beta! 🚀",
            html_content=html
        )
        
        # Send via Brevo API
        print(f"📧 Sending email to {email} via Brevo...")
        api_instance.send_transac_email(send_smtp_email)
        
        print(f"✅ Welcome email sent to {email} via Brevo")
        
        # Mark as sent in database
        entry = db.query(WaitlistEntry).filter(WaitlistEntry.id == entry_id).first()
        if entry:
            entry.email_sent = True  # type: ignore
            entry.email_sent_at = datetime.utcnow()  # type: ignore
            db.commit()
        
    except Exception as e:
        print(f"❌ Email failed for {email}: {e}")
    finally:
        db.close()


# === WAITLIST ROUTES === #

@app.post("/waitlist", response_model=WaitlistResponse)
@limiter.limit("5/minute")
async def waitlist_signup(
    signup: WaitlistRequest, 
    request: Request, 
    background_tasks: BackgroundTasks,
    db: Session = Depends(get_db)
):
    """
    Add email to waitlist
    
    Features:
    - Saves to PostgreSQL/SQLite database
    - Prevents duplicates
    - Sends welcome email (async in background)
    - Rate limited (5/min)
    - Tracks IP, user agent, referrer
    """
    try:
        email = signup.email.lower()
        
        # Check if already signed up
        existing = db.query(WaitlistEntry).filter(WaitlistEntry.email == email).first()
        if existing:
            total = db.query(WaitlistEntry).count()
            return WaitlistResponse(
                success=False,
                message="You're already on the waitlist! 🎉",
                total_signups=total
            )
        
        # Create new entry
        new_entry = WaitlistEntry(
            email=email,
            ip_address=get_remote_address(request),
            user_agent=request.headers.get("user-agent", "unknown"),
            referrer=request.headers.get("referer")
        )
        
        db.add(new_entry)
        db.commit()
        db.refresh(new_entry)
        
        # Send welcome email in BACKGROUND (non-blocking!)
        background_tasks.add_task(send_welcome_email, email, new_entry.id)
        
        total = db.query(WaitlistEntry).count()
        
        return WaitlistResponse(
            success=True,
            message="Amazing! You're on the list. Check your email for confirmation!",
            total_signups=total
        )
        
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/waitlist/count")
async def waitlist_count(db: Session = Depends(get_db)):
    """Get total waitlist signups (public endpoint)"""
    count = db.query(WaitlistEntry).count()
    return {
        "count": count,
        "timestamp": datetime.utcnow().isoformat()
    }


@app.get("/waitlist/admin")
async def waitlist_admin(db: Session = Depends(get_db)):
    """
    Admin dashboard - View all signups
    
    TODO: Add authentication!
    """
    all_signups = db.query(WaitlistEntry).order_by(WaitlistEntry.signup_timestamp.desc()).all()
    return {
        "total": len(all_signups),
        "signups": [entry.to_dict() for entry in all_signups],
        "latest_10": [entry.to_dict() for entry in all_signups[:10]]
    }


@app.post("/waitlist/admin/resend-all")
async def resend_all_emails(background_tasks: BackgroundTasks, db: Session = Depends(get_db)):
    """Resend emails to everyone who hasn't received one yet"""
    pending = db.query(WaitlistEntry).filter(WaitlistEntry.email_sent == False).all()
    
    for entry in pending:
        background_tasks.add_task(send_welcome_email, entry.email, entry.id)
    
    return {
        "success": True,
        "queued": len(pending),
        "emails": [e.email for e in pending]
    }


# Initialize database on startup
@app.on_event("startup")
async def startup_event():
    """Initialize database tables on app startup"""
    print("🔄 Initializing database...")
    init_db()
    print("✅ Database ready!")


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
