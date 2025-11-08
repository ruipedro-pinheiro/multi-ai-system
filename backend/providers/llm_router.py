"""LiteLLM Router - Universal LLM Gateway with Mock Fallback + OAuth Support"""
from typing import List, Dict, Optional, AsyncGenerator, TYPE_CHECKING
import litellm
from config import settings
from providers.mock_llm import MockLLM

if TYPE_CHECKING:
    from auth.token_store import TokenStore
    from auth.oauth_refresh import OAuthRefresher

class LLMRouter:
    """Universal LLM router with fallback to mock (for dev/testing) + OAuth support"""
    
    def __init__(
        self, 
        token_store: Optional['TokenStore'] = None,
        oauth_refresher: Optional['OAuthRefresher'] = None
    ):
        litellm.set_verbose = False
        self.token_store = token_store  # OAuth token store
        self.oauth_refresher = oauth_refresher  # Auto-refresh helper
        self.deployments = self._build_deployments()
        self.mock = MockLLM()  # Always available fallback
    
    def _build_deployments(self) -> List[Dict]:
        """Build list of available LLM deployments (API keys OR OAuth tokens)
        
        Priority Strategy:
        - PRIORITY 1: Gemini 2.0 Flash (gratuit freemium)
        - PRIORITY 2: PRO users' configured AIs (OAuth/API keys)
        - PRIORITY 999: Mock fallback (dev/testing)
        """
        deployments = []
        
        # Ollama (local) - Only if configured
        if settings.ollama_base_url and settings.ollama_model:
            deployments.append({
                "name": "ollama",
                "model": f"ollama/{settings.ollama_model}",
                "api_base": settings.ollama_base_url,
                "priority": 2,
                "enabled": True
            })
        
        # Claude (API key OR OAuth) - PRO users
        claude_key = settings.anthropic_api_key
        if not claude_key and self.token_store:
            claude_key = self.token_store.get_token("anthropic")
        
        if claude_key:
            deployments.append({
                "name": "claude",
                "model": "claude-3-5-sonnet-20241022",
                "api_key": claude_key,
                "priority": 2,
                "enabled": True,
                "oauth": self.token_store and self.token_store.is_token_valid("anthropic")
            })
        
        # GPT-4 (API key OR OAuth) - PRO users
        openai_key = settings.openai_api_key
        if not openai_key and self.token_store:
            openai_key = self.token_store.get_token("openai")
        
        if openai_key:
            deployments.append({
                "name": "gpt",
                "model": "gpt-4-turbo-preview",
                "api_key": openai_key,
                "priority": 2,
                "enabled": True,
                "oauth": self.token_store and self.token_store.is_token_valid("openai")
            })
        
        # FREEMIUM: Gemini 2.0 Flash (gratuit 1500 req/jour)
        google_key = settings.google_api_key
        if not google_key and self.token_store:
            google_key = self.token_store.get_token("google")
        
        if google_key:
            deployments.append({
                "name": "gemini",
                "model": "gemini/gemini-2.0-flash-exp",
                "api_key": google_key,
                "priority": 1,
                "enabled": True,
                "oauth": self.token_store and self.token_store.is_token_valid("google")
            })
        
        # FREEMIUM: Groq Llama 3.1 (gratuit 14,400 req/jour, ultra rapide)
        groq_key = settings.groq_api_key
        if groq_key:
            deployments.append({
                "name": "llama",  # SmartRouter mapping
                "model": "groq/llama-3.1-70b-versatile",
                "api_key": groq_key,
                "priority": 1,
                "enabled": True,
                "oauth": False
            })
        
        # FREEMIUM: Groq Mixtral (gratuit, créatif/multilingue)
        if groq_key:
            deployments.append({
                "name": "mixtral",
                "model": "groq/mixtral-8x7b-32768",
                "api_key": groq_key,
                "priority": 1,
                "enabled": True,
                "oauth": False
            })
        
        # MOCK (ALWAYS AVAILABLE - Last fallback)
        deployments.append({
            "name": "mock",
            "model": "mock-ai",
            "priority": 999,
            "enabled": True,
            "oauth": False
        })
        
        return sorted([d for d in deployments if d["enabled"]], 
                     key=lambda x: x["priority"])
    
    async def chat(
        self, 
        messages: List[Dict], 
        preferred_provider: Optional[str] = None,
        stream: bool = False
    ) -> str:
        """Route chat request to best available LLM"""
        
        deployments = self.deployments
        if preferred_provider:
            deployments = sorted(
                deployments,
                key=lambda x: (0 if x["name"] == preferred_provider else 1, x["priority"])
            )
        
        # Try each deployment
        for deployment in deployments:
            try:
                # MOCK provider (error message - no real AI configured)
                if deployment["name"] == "mock":
                    return await self.mock.chat(messages)
                
                # OAuth token refresh if needed
                api_key = deployment.get("api_key")
                if deployment.get("oauth") and self.oauth_refresher:
                    provider_name = deployment["name"]
                    # Map provider name to OAuth provider
                    oauth_map = {
                        "claude": "anthropic",
                        "gpt": "openai",
                        "gemini": "google"
                    }
                    oauth_provider = oauth_map.get(provider_name)
                    if oauth_provider:
                        refreshed_token = await self.oauth_refresher.get_valid_token(oauth_provider)
                        if refreshed_token:
                            api_key = refreshed_token
                            print(f"🔑 Using refreshed OAuth token for {provider_name}")
                
                # Real LLM provider
                if stream:
                    return self._stream_response(deployment, messages)
                else:
                    response = await litellm.acompletion(
                        model=deployment["model"],
                        messages=messages,
                        api_base=deployment.get("api_base"),
                        api_key=api_key,
                        stream=False,
                        timeout=120,  # 120s timeout for local models (DeepSeek-R1 is slow)
                        max_tokens=150,  # SHORT responses for landing page demo!
                        temperature=0.7
                    )
                    return response.choices[0].message.content
            
            except Exception as e:
                print(f"❌ {deployment['name']} failed: {e}")
                continue
        
        # Should never reach (mock is always last)
        return await self.mock.chat(messages)
    
    async def _stream_response(
        self, 
        deployment: Dict, 
        messages: List[Dict]
    ) -> AsyncGenerator[str, None]:
        """Stream response from LLM"""
        response = await litellm.acompletion(
            model=deployment["model"],
            messages=messages,
            api_base=deployment.get("api_base"),
            api_key=deployment.get("api_key"),
            stream=True
        )
        
        async for chunk in response:
            if chunk.choices[0].delta.content:
                yield chunk.choices[0].delta.content
    
    def get_available_providers(self) -> List[str]:
        """Get list of available AI providers"""
        return [d["name"] for d in self.deployments]

router = LLMRouter()
