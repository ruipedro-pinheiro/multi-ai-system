"""Demo endpoints - Persistent anonymous sessions with rate limiting"""
from fastapi import APIRouter, Request, HTTPException, Depends, Response
from pydantic import BaseModel, field_validator
from typing import Optional, List, Dict, Any
from sqlalchemy.orm import Session
from sqlalchemy import desc, asc, func
import uuid
from datetime import datetime

# Models
from models.room import get_db, DemoSession, Room as DBRoom, Message as DBMessage
from providers.llm_router import LLMRouter
from security.input_sanitizer import InputSanitizer
from security.prompt_filter import PromptSecurityFilter

router = APIRouter(prefix="/demo", tags=["demo"])

# === SAFEGUARDS: Circuit Breakers === #
MAX_DISCUSSION_ROUNDS = 5  # Hard limit to prevent infinite loops and cost explosion
CONSENSUS_KEYWORDS = ["CONSENSUS", "AGREE", "AGREED", "FINAL", "CONCLUDED", "COMPLETE"]
DISCUSSION_TIMEOUT_SECONDS = 60  # Future: Force synthesis after timeout

def check_consensus(response_text: str) -> bool:
    """
    Check if AI response indicates consensus using multiple keywords
    
    SAFEGUARD: Multiple keywords prevent infinite loops from missed detections
    Returns True if ANY consensus keyword found (case-insensitive)
    """
    if not response_text:
        return False
    upper_text = response_text.upper()
    return any(keyword in upper_text for keyword in CONSENSUS_KEYWORDS)

# === AI Provider Names (Transparency) === #
AI_DISPLAY_NAMES = {
    "AI-1": "GPT-4",
    "AI-2": "Claude",
    "AI-3": "Gemini"
}


# === Pydantic Models === #

class DemoMessage(BaseModel):
    content: str
    session_id: Optional[str] = None
    
    @field_validator('content')
    @classmethod
    def validate_content(cls, v: str) -> str:
        # Validation length
        if not v or len(v) < 1 or len(v) > 5000:
            raise ValueError("Content must be between 1 and 5000 characters")
        
        # SECURITY: Sanitize input
        sanitized, is_safe, error = InputSanitizer.sanitize_message(v)
        if not is_safe:
            raise ValueError(f"Invalid message: {error}")
        
        # SECURITY: Check for prompt injection
        is_safe_prompt, reason = PromptSecurityFilter.is_safe(sanitized)
        if not is_safe_prompt:
            raise ValueError(f"Unsafe prompt: {reason}")
        
        return sanitized


class DemoSessionResponse(BaseModel):
    session_id: str
    query_count: int
    queries_remaining: int
    max_queries: int
    created_at: str
    messages: list


# === Helper Functions === #

def get_or_create_demo_session(
    session_id: Optional[str],
    db: Session,
    request: Request
) -> DemoSession:
    """Get existing demo session or create new one"""
    
    # Try to find existing session
    if session_id:
        demo = db.query(DemoSession).filter(DemoSession.session_id == session_id).first()
        if demo is not None:
            # Check expiration (property, not SQL)
            if not demo.is_expired:
                return demo
    
    # Create new session
    new_session_id = str(uuid.uuid4())
    
    # Create room for this demo session
    room = DBRoom(
        room_id=f"demo_{new_session_id[:8]}_{int(datetime.utcnow().timestamp())}",
        title="Demo Chat",
        user_id=f"demo_{new_session_id[:8]}",
        active_ais='["gpt", "gemini"]'  # Demo uses free/fast AIs
    )
    db.add(room)
    db.flush()  # Get room.id
    
    # Create demo session linked to room
    demo = DemoSession(
        session_id=new_session_id,
        room_id=room.id,
        query_count=0,
        max_queries=10,
        ip_address=request.client.host if request.client else None,
        user_agent=request.headers.get("user-agent", "")[:500]
    )
    db.add(demo)
    db.commit()
    db.refresh(demo)
    
    return demo


# === Routes === #

@router.post("/chat", response_model=dict)
async def demo_chat(
    message: DemoMessage,
    request: Request,
    response: Response,
    db: Session = Depends(get_db)
):
    """
    Send message in demo mode - persistent session with rate limiting
    
    - Creates/retrieves session from cookie
    - Saves all messages to DB
    - Rate limited to 10 queries per session
    - Session persists across browser restarts (30 days)
    """
    
    # Get or create demo session
    demo = get_or_create_demo_session(message.session_id, db, request)
    
    # SAFEGUARD: Reset query count if it's a new day
    if demo.reset_if_new_day():
        db.commit()
        print(f"✅ Daily reset for session {demo.session_id[:8]}: query_count reset to 0")
    
    # Set cookie for persistence (30 days)
    response.set_cookie(
        key="chika_demo_session",
        value=demo.session_id,
        max_age=30 * 24 * 60 * 60,  # 30 days
        httponly=True,
        samesite="lax"
    )
    
    # Check rate limit
    if demo.query_count >= demo.max_queries:
        raise HTTPException(
            status_code=429,
            detail={
                "message": f"Daily limit reached ({demo.max_queries} questions/day). Try again tomorrow or join waitlist for unlimited access!",
                "query_count": demo.query_count,
                "queries_remaining": 0,
                "max_queries": demo.max_queries,
                "session_id": demo.session_id
            }
        )
    
    # Get room
    room = db.query(DBRoom).filter(DBRoom.id == demo.room_id).first()
    if room is None:
        raise HTTPException(status_code=500, detail="Room not found")
    
    # Save user message
    user_msg = DBMessage(
        room_id=room.id,
        role="user",
        author="user",
        content=message.content,
        mentions="[]",
        timestamp=datetime.utcnow()
    )
    db.add(user_msg)
    
    # Get AI responses (simplified - no full orchestration for demo)
    from providers.llm_router import LLMRouter
    from auth.token_store import TokenStore
    from auth.oauth_refresh import OAuthRefresher
    from auth.oauth_manager import OAuthManager
    
    # Initialize LLM router
    oauth_manager = OAuthManager()
    token_store = TokenStore()
    oauth_refresher = OAuthRefresher(oauth_manager, token_store)
    llm_router = LLMRouter(token_store=token_store, oauth_refresher=oauth_refresher)
    
    ai_responses = []
    available_ais = llm_router.get_available_providers()
    
    # === SHARED CONTEXT SYSTEM (Token-efficient) === #
    demo_ais = [ai for ai in ['AI-1', 'AI-2', 'AI-3'] if ai in available_ais][:2]
    
    if len(demo_ais) < 2:
        return {"success": False, "message": "Not enough AIs available"}
    
    first_ai = demo_ais[0]
    second_ai = demo_ais[1]
    
    # Get conversation history from DB (shared context)
    history = db.query(DBMessage).filter(
        DBMessage.room_id == room.id
    ).order_by(desc(DBMessage.timestamp)).limit(5).all()
    
    shared_context = "\n".join([f"{m.author}: {m.content}" for m in reversed(history)]) if history else ""
    
    # Persistent system prompt (injected once)
    system_prompt = f"""CHIKA Multi-AI Platform

VISION: Multi-AI collaboration with persistent shared context. AIs discuss privately, challenge each other, output superior answers.

CONTEXT INJECTION: All conversation history is available above. Don't repeat context - reference it.

YOUR TASK: Collaborate efficiently. Be concise (1-2 sentences). Challenge ideas. Build on previous messages.

Previous conversation:
{shared_context}

User's new question: {message.content}"""
    
    discussion_log = []
    
    # === AUTONOMOUS AI DISCUSSION (Self-regulated) === #
    
    max_rounds = MAX_DISCUSSION_ROUNDS  # SAFEGUARD: Hard limit
    conversation = []
    current_speaker = first_ai
    ais_agreed = set()  # Track which AIs have agreed
    
    for round_num in range(max_rounds):
        try:
            # Let AIs decide autonomously when to stop
            if round_num == 0:
                instruction = "Give your answer. If you want another AI's input, say DISCUSS. If you're confident, say CONSENSUS."
            else:
                instruction = "Read the discussion. Add your perspective, or say CONSENSUS if you agree with current direction."
            
            prompt = f"{current_speaker}: {instruction}"
            
            # Build message history
            messages = [{"role": "system", "content": system_prompt}]
            for entry in conversation:
                messages.append({"role": "assistant", "content": f"{entry['ai']}: {entry['msg']}"})
            messages.append({"role": "user", "content": prompt})
            
            # Get AI response
            response = await llm_router.chat(
                messages=messages,
                preferred_provider=current_speaker
            )
            
            # Log discussion
            discussion_log.append({
                "ai": current_speaker,
                "msg": response,
                "round": round_num + 1
            })
            
            conversation.append({
                "ai": current_speaker,
                "msg": response
            })
            
            ai_responses.append({
                "ai": current_speaker,
                "display_name": AI_DISPLAY_NAMES.get(current_speaker, current_speaker),
                "content": response
            })
            
            # SAFEGUARD: Check for consensus (multiple keywords)
            if check_consensus(response):
                ais_agreed.add(current_speaker)
                # If both AIs agree, stop discussion
                if len(ais_agreed) >= 2 or round_num >= 3:
                    print(f"✅ Consensus reached: {len(ais_agreed)} AIs agreed after {round_num + 1} rounds")
                    break
            
            # Switch speaker
            current_speaker = second_ai if current_speaker == first_ai else first_ai
            
        except Exception as e:
            print(f"❌ Round {round_num + 1} error: {e}")
            break
    
    # Log discussion outcome
    print(f"✅ Discussion completed: {len(discussion_log)} messages, {len(ais_agreed)} AIs agreed")
    
    # === SYNTHESIS (Token-efficient) === #
    synthesis_response = None
    if len(discussion_log) >= 2:
        try:
            # Minimal synthesis prompt - AIs already share context
            synthesis_ai = "AI-1" if "AI-1" in available_ais else first_ai
            
            synthesis_response = await llm_router.chat(
                messages=[
                    {"role": "system", "content": f"{system_prompt}\n\nDiscussion:\n" + "\n".join([f"{d['ai']}: {d['msg']}" for d in discussion_log])},
                    {"role": "user", "content": "CHIKA, synthesize final answer (1-2 sentences):"}
                ],
                preferred_provider=synthesis_ai
            )
            
            # Save to shared context
            db.add(DBMessage(
                room_id=room.id,
                role="assistant",
                author="CHIKA",
                content=synthesis_response,
                mentions="[]",
                timestamp=datetime.utcnow()
            ))
            
        except Exception as e:
            print(f"❌ Synthesis: {e}")
            synthesis_response = None
    
    # Update session query count
    demo.query_count += 1
    demo.last_activity = datetime.utcnow()
    db.commit()
    
    return {
        "success": True,
        "session_id": demo.session_id,
        "query_count": demo.query_count,
        "queries_remaining": demo.queries_remaining,
        "max_queries": demo.max_queries,
        "synthesis": synthesis_response,
        "ai_responses": ai_responses,
        "user_message": {
            "content": message.content,
            "timestamp": user_msg.timestamp.isoformat()
        }
    }


@router.get("/session", response_model=DemoSessionResponse)
async def get_demo_session(
    request: Request,
    db: Session = Depends(get_db)
):
    """
    Restore demo session - returns session info + message history
    
    SECURITY: Only uses server-side cookie (HttpOnly), NO query params
    Used on page load (F5) to restore conversation
    """
    
    # SECURITY: ONLY get session_id from HttpOnly cookie (not from query params!)
    session_id = request.cookies.get("chika_demo_session")
    
    if not session_id:
        # No existing session - return empty
        return {
            "session_id": "",
            "query_count": 0,
            "queries_remaining": 10,
            "max_queries": 10,
            "created_at": datetime.utcnow().isoformat(),
            "messages": []
        }
    
    # Find session in DB
    demo = db.query(DemoSession).filter(DemoSession.session_id == session_id).first()
    
    if demo is None or demo.is_expired:
        # Session expired or not found
        return {
            "session_id": "",
            "query_count": 0,
            "queries_remaining": 10,
            "max_queries": 10,
            "created_at": datetime.utcnow().isoformat(),
            "messages": []
        }
    
    # Get room and messages
    room = db.query(DBRoom).filter(DBRoom.id == demo.room_id).first()
    if room is None:
        return {
            "session_id": demo.session_id,
            "query_count": demo.query_count,
            "queries_remaining": demo.queries_remaining,
            "max_queries": demo.max_queries,
            "created_at": demo.created_at.isoformat(),
            "messages": []
        }
    
    # Get all messages in room
    messages = db.query(DBMessage).filter(
        DBMessage.room_id == room.id
    ).order_by(asc(DBMessage.timestamp)).all()
    
    messages_data = [{
        "role": m.role,
        "author": m.author,
        "content": m.content,
        "timestamp": m.timestamp.isoformat()
    } for m in messages]
    
    return {
        "session_id": demo.session_id,
        "query_count": demo.query_count,
        "queries_remaining": demo.queries_remaining,
        "max_queries": demo.max_queries,
        "created_at": demo.created_at.isoformat(),
        "messages": messages_data
    }


@router.get("/stats")
async def demo_stats(db: Session = Depends(get_db)):
    """Get demo usage statistics"""
    from sqlalchemy import func
    
    total_sessions = db.query(DemoSession).count()
    active_sessions = db.query(DemoSession).filter(
        DemoSession.query_count > 0
    ).count()
    total_queries = db.query(func.sum(DemoSession.query_count)).scalar() or 0
    
    return {
        "total_sessions": total_sessions,
        "active_sessions": active_sessions,
        "total_queries": total_queries
    }
