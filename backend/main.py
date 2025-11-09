"""Chika Backend - Multi-AI Chat Platform

FastAPI backend with WebSocket support for real-time chat.
"""
from fastapi import FastAPI, WebSocket, WebSocketDisconnect, Depends, HTTPException, Request
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, validator, constr
from typing import Optional, List, Dict
import json
from datetime import datetime

# Config & Models
from config import settings
from models.room import init_db, get_db, Room as DBRoom, Message as DBMessage, DemoSession
from providers.llm_router import LLMRouter
from room.manager import RoomManager

# Security
from security.input_sanitizer import InputSanitizer
from security.prompt_filter import PromptSecurityFilter
from security.secrets_manager import setup_secure_logging
from security.headers import SecurityHeadersMiddleware
from security.rate_limiter import setup_rate_limiting, check_rate_limit_middleware

# Initialize FastAPI
app = FastAPI(
    title="Chika API",
    version="0.1.0",
    description="Utiliser dix IA sans chichi - Multi-AI chat platform"
)

# SECURITY: Setup
setup_secure_logging()
app.add_middleware(SecurityHeadersMiddleware)
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins,
    allow_credentials=True,
    allow_methods=["GET", "POST", "DELETE", "OPTIONS"],
    allow_headers=["Content-Type", "Authorization"],
    max_age=3600
)
setup_rate_limiting(app)

# Initialize database
init_db()

# OAuth System (must be initialized BEFORE LLM Router)
from auth.oauth_manager import OAuthManager
from auth.token_store import TokenStore
from auth.oauth_refresh import OAuthRefresher

oauth_manager = OAuthManager()
token_store = TokenStore()
oauth_refresher = OAuthRefresher(oauth_manager, token_store)

# Initialize LLM Router with OAuth support
llm_router = LLMRouter(token_store=token_store, oauth_refresher=oauth_refresher)


# === Health Check Endpoint === #

@app.get("/health")
async def health_check():
    """
    Health check endpoint for frontend monitoring
    
    Returns available AI providers and backend status
    """
    try:
        available_ais = llm_router.get_available_providers()
        return {
            "status": "online",
            "available_ais": available_ais,
            "timestamp": datetime.utcnow().isoformat()
        }
    except Exception as e:
        return {
            "status": "degraded",
            "available_ais": [],
            "error": str(e),
            "timestamp": datetime.utcnow().isoformat()
        }


# === Pydantic Models === #

class RoomCreate(BaseModel):
    title: constr(min_length=1, max_length=200) = "New Chat"
    active_ais: Optional[List[str]] = ['claude', 'gpt']
    
    @validator('title')
    def validate_title(cls, v):
        sanitized, is_safe, error = InputSanitizer.sanitize_string(v, max_length=200)
        if not is_safe:
            raise ValueError(f"Invalid title: {error}")
        return sanitized
    
    @validator('active_ais')
    def validate_ais(cls, v):
        allowed_ais = ['claude', 'gpt', 'gemini', 'grok', 'ollama', 'mock']
        for ai in v:
            if ai not in allowed_ais:
                raise ValueError(f"Invalid AI: {ai}. Allowed: {allowed_ais}")
        return v


class ChatMessage(BaseModel):
    room_id: constr(min_length=10, max_length=100)
    content: constr(min_length=1, max_length=50000)
    
    @validator('content')
    def validate_content(cls, v):
        # SECURITY: Sanitize input
        sanitized, is_safe, error = InputSanitizer.sanitize_message(v)
        if not is_safe:
            raise ValueError(f"Invalid message: {error}")
        
        # SECURITY: Check for prompt injection
        is_safe_prompt, reason = PromptSecurityFilter.is_safe(sanitized)
        if not is_safe_prompt:
            raise ValueError(f"Unsafe prompt: {reason}")
        
        return sanitized
    
    @validator('room_id')
    def validate_room_id(cls, v):
        sanitized, is_safe, error = InputSanitizer.sanitize_session_id(v)
        if not is_safe:
            raise ValueError(f"Invalid room ID: {error}")
        return sanitized


# === WebSocket Manager === #

class ConnectionManager:
    """Manages WebSocket connections per room"""
    
    def __init__(self):
        self.active_connections: Dict[str, List[WebSocket]] = {}
    
    async def connect(self, websocket: WebSocket, room_id: str):
        await websocket.accept()
        if room_id not in self.active_connections:
            self.active_connections[room_id] = []
        self.active_connections[room_id].append(websocket)
    
    def disconnect(self, websocket: WebSocket, room_id: str):
        if room_id in self.active_connections:
            self.active_connections[room_id].remove(websocket)
    
    async def broadcast(self, room_id: str, message: dict):
        """Broadcast message to all clients in room"""
        if room_id in self.active_connections:
            for connection in self.active_connections[room_id]:
                try:
                    await connection.send_json(message)
                except:
                    pass  # Connection closed

manager = ConnectionManager()


# === Routes === #

@app.get("/")
async def root():
    """API info"""
    return {
        "name": "Chika",
        "slogan": "Utiliser dix IA sans chichi",
        "version": "0.1.0",
        "available_ais": llm_router.get_available_providers(),
        "features": {
            "multi_ai_collaboration": True,
            "private_discussions": True,
            "mentions": True,
            "local_models": "ollama" in llm_router.get_available_providers()
        }
    }


@app.post("/rooms")
async def create_room(
    request: Request,
    room_data: RoomCreate,
    db = Depends(get_db)
):
    """Create a new chat room
    
    SECURITY: Rate limited to prevent spam
    """
    await check_rate_limit_middleware(request, max_requests=5)
    
    room_manager = RoomManager(llm_router, db)
    room = room_manager.create_room(
        title=room_data.title,
        user_id="default_user",  # TODO: Get from auth
        active_ais=room_data.active_ais
    )
    
    return {
        "room_id": room.room_id,
        "title": room.title,
        "active_ais": room.ai_list,
        "created_at": room.created_at.isoformat()
    }


@app.get("/rooms")
async def list_rooms(db = Depends(get_db)):
    """List all rooms for user"""
    room_manager = RoomManager(llm_router, db)
    rooms = room_manager.list_rooms(user_id="default_user")
    
    return [{
        "room_id": r.room_id,
        "title": r.title,
        "active_ais": r.ai_list,
        "created_at": r.created_at.isoformat(),
        "updated_at": r.updated_at.isoformat()
    } for r in rooms]


@app.get("/rooms/{room_id}")
async def get_room(room_id: str, db = Depends(get_db)):
    """Get room details"""
    room_manager = RoomManager(llm_router, db)
    room = room_manager.get_room(room_id)
    
    if not room:
        raise HTTPException(status_code=404, detail="Room not found")
    
    return {
        "room_id": room.room_id,
        "title": room.title,
        "active_ais": room.ai_list,
        "created_at": room.created_at.isoformat(),
        "updated_at": room.updated_at.isoformat()
    }


@app.get("/rooms/{room_id}/messages")
async def get_messages(room_id: str, db = Depends(get_db)):
    """Get all messages in a room"""
    room_manager = RoomManager(llm_router, db)
    room = room_manager.get_room(room_id)
    
    if not room:
        raise HTTPException(status_code=404, detail="Room not found")
    
    messages = room_manager.get_messages(room)
    
    return [{
        "role": m.role,
        "author": m.author,
        "content": m.content,
        "mentions": m.mention_list,
        "discussion_id": m.discussion_id,
        "timestamp": m.timestamp.isoformat()
    } for m in messages]


@app.get("/rooms/{room_id}/discussions")
async def get_discussions(room_id: str, db = Depends(get_db)):
    """Get all AI discussions in a room"""
    room_manager = RoomManager(llm_router, db)
    room = room_manager.get_room(room_id)
    
    if not room:
        raise HTTPException(status_code=404, detail="Room not found")
    
    discussions = room_manager.get_discussions(room)
    
    return [{
        "id": d.id,
        "participants": d.participant_list,
        "topic": d.topic,
        "messages": d.message_list,
        "consensus": d.consensus,
        "status": d.status,
        "created_at": d.created_at.isoformat(),
        "resolved_at": d.resolved_at.isoformat() if d.resolved_at else None
    } for d in discussions]


@app.post("/chat")
async def send_message(
    request_obj: Request,
    chat_msg: ChatMessage,
    db = Depends(get_db)
):
    """Send a chat message and get AI response(s)
    
    SECURITY: Rate limited, sanitized, prompt filtered
    """
    await check_rate_limit_middleware(request_obj, max_requests=10)
    
    # Get room
    room_manager = RoomManager(llm_router, db)
    room = room_manager.get_room(chat_msg.room_id)
    
    if not room:
        raise HTTPException(status_code=404, detail="Room not found")
    
    # Process message (orchestrate AI collaboration)
    result = await room_manager.process_user_message(
        room=room,
        content=chat_msg.content
    )
    
    # Return response
    response_data = {
        "user_message": {
            "role": result['user_message'].role,
            "author": result['user_message'].author,
            "content": result['user_message'].content,
            "timestamp": result['user_message'].timestamp.isoformat()
        },
        "ai_message": {
            "role": result['ai_message'].role,
            "author": result['ai_message'].author,
            "content": result['ai_message'].content,
            "mentions": result['ai_message'].mention_list,
            "timestamp": result['ai_message'].timestamp.isoformat()
        },
        "discussion": None
    }
    
    # Include discussion if exists
    if result['discussion']:
        d = result['discussion']
        response_data['discussion'] = {
            "id": d.id,
            "participants": d.participant_list,
            "topic": d.topic,
            "messages": d.message_list,
            "consensus": d.consensus,
            "status": d.status
        }
    
    # Broadcast to WebSocket clients
    await manager.broadcast(room.room_id, {
        "type": "new_messages",
        "data": response_data
    })
    
    return response_data


@app.websocket("/ws/{room_id}")
async def websocket_endpoint(websocket: WebSocket, room_id: str):
    """WebSocket endpoint for real-time chat"""
    await manager.connect(websocket, room_id)
    
    try:
        while True:
            # Just keep connection alive
            # (messages are broadcasted from /chat endpoint)
            data = await websocket.receive_text()
            # Echo back (optional)
            await websocket.send_json({"type": "ack", "data": "received"})
    
    except WebSocketDisconnect:
        manager.disconnect(websocket, room_id)


# === OAuth Endpoints === #

@app.get("/oauth/providers")
async def list_oauth_providers():
    """List all available OAuth providers
    
    Returns list of AI providers that support OAuth authentication
    """
    providers = oauth_manager.list_providers()
    provider_info = []
    
    for provider_name in providers:
        info = oauth_manager.get_provider_info(provider_name)
        if info:
            # Check if we have a valid token
            has_token = token_store.is_token_valid(provider_name)
            info["authenticated"] = has_token
            provider_info.append(info)
    
    return {"providers": provider_info}


@app.get("/oauth/authorize/{provider}")
async def oauth_authorize(provider: str):
    """Start OAuth flow for a provider
    
    Returns authorization URL for user to visit
    """
    if provider not in oauth_manager.PROVIDERS:
        raise HTTPException(status_code=404, detail=f"Provider '{provider}' not found")
    
    # Redirect URI (Anthropic uses their own, others use our callback)
    if provider == "anthropic":
        redirect_uri = "https://console.anthropic.com/oauth/code/callback"
    else:
        redirect_uri = f"http://localhost:8000/oauth/callback/{provider}"
    
    try:
        auth_url, state, _ = oauth_manager.get_authorization_url(
            provider_name=provider,
            redirect_uri=redirect_uri
        )
        
        return {
            "authorization_url": auth_url,
            "state": state,
            "provider": provider,
            "redirect_uri": redirect_uri,
            "instructions": "Copy the authorization code from the redirect URL" if provider == "anthropic" else "You will be redirected back automatically",
            "message": f"Visit the authorization_url to authenticate with {provider}"
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/oauth/callback/{provider}")
async def oauth_callback(
    provider: str,
    code: Optional[str] = None,
    state: Optional[str] = None,
    error: Optional[str] = None
):
    """OAuth callback endpoint
    
    Called by OAuth provider after user authorizes
    """
    if error:
        raise HTTPException(status_code=400, detail=f"OAuth error: {error}")
    
    if not code or not state:
        raise HTTPException(status_code=400, detail="Missing code or state")
    
    try:
        # Exchange code for token
        token_data = await oauth_manager.exchange_code_for_token(
            provider_name=provider,
            code=code,
            state=state
        )
        
        # Store tokens
        token_store.store_token(
            provider=provider,
            access_token=token_data["access_token"],
            refresh_token=token_data.get("refresh_token"),
            expires_in=token_data.get("expires_in")
        )
        
        return {
            "success": True,
            "provider": provider,
            "message": f"Successfully authenticated with {provider}!",
            "expires_in": token_data.get("expires_in")
        }
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Token exchange failed: {str(e)}")



@app.post("/oauth/exchange-code/{provider}")
async def oauth_exchange_manual_code(
    provider: str,
    code: str,
    state: str
):
    """Manually exchange OAuth code for token (for Anthropic manual flow)
    
    Body:
        code: Authorization code from OAuth provider
        state: State parameter from authorization URL
    """
    try:
        # Exchange code for token
        token_data = await oauth_manager.exchange_code_for_token(
            provider_name=provider,
            code=code,
            state=state
        )
        
        # Store tokens
        token_store.store_token(
            provider=provider,
            access_token=token_data["access_token"],
            refresh_token=token_data.get("refresh_token"),
            expires_in=token_data.get("expires_in")
        )
        
        return {
            "success": True,
            "provider": provider,
            "message": f"Successfully authenticated with {provider}!",
            "expires_in": token_data.get("expires_in")
        }
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/oauth/refresh/{provider}")
async def oauth_refresh(provider: str):
    """Manually refresh OAuth token for a provider"""
    refresh_token = token_store.get_refresh_token(provider)
    
    if not refresh_token:
        raise HTTPException(status_code=404, detail=f"No refresh token found for {provider}")
    
    try:
        token_data = await oauth_manager.refresh_access_token(
            provider_name=provider,
            refresh_token=refresh_token
        )
        
        # Update stored tokens
        token_store.store_token(
            provider=provider,
            access_token=token_data["access_token"],
            refresh_token=token_data.get("refresh_token", refresh_token),
            expires_in=token_data.get("expires_in")
        )
        
        return {
            "success": True,
            "provider": provider,
            "message": f"Token refreshed for {provider}"
        }
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Token refresh failed: {str(e)}")


@app.delete("/oauth/disconnect/{provider}")
async def oauth_disconnect(provider: str):
    """Disconnect (remove token) for a provider"""
    token_store.remove_token(provider)
    
    return {
        "success": True,
        "provider": provider,
        "message": f"Disconnected from {provider}"
    }


@app.get("/oauth/status")
async def oauth_status():
    """Get OAuth status for all providers"""
    all_providers = oauth_manager.list_providers()
    authenticated_providers = token_store.list_providers()
    
    status = []
    for provider in all_providers:
        is_authed = provider in authenticated_providers
        status.append({
            "provider": provider,
            "authenticated": is_authed,
            "token_valid": token_store.is_token_valid(provider) if is_authed else False
        })
    
    return {
        "providers": status,
        "authenticated_providers": authenticated_providers
    }


# === DEMO ROUTES === #
# Import demo router
from routes.demo import router as demo_router
app.include_router(demo_router)


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
