# 🤖 CHIKA - Multi-AI Collaboration Platform

**Stop switching between AIs. Let them work together.**

[![Status](https://img.shields.io/badge/status-pre--launch-yellow)](https://ruipedro-pinheiro.github.io/CHIKA/frontend-v1/)
[![License](https://img.shields.io/badge/license-MIT-blue.svg)](LICENSE)
[![Python](https://img.shields.io/badge/python-3.11+-blue.svg)](https://www.python.org/)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.115+-green.svg)](https://fastapi.tiangolo.com/)

---

## 🎯 What is CHIKA?

CHIKA connects multiple AI models (GPT-4, Claude, Gemini, local models) and makes them **collaborate** to give you one synthesized, high-quality answer.

**The Problem:**
- Using ChatGPT → switch tab → use Claude → copy-paste context → switch again
- No collaboration between AIs
- Context lost every time
- Hallucinations not cross-checked

**The Solution:**
- **One question** → Multiple AIs discuss → **One best answer**
- Context shared automatically
- AIs review each other's responses
- Less hallucinations, better quality

---

## 🚀 Live Demo

**Try it now:** [https://ruipedro-pinheiro.github.io/CHIKA/frontend-v1/](https://ruipedro-pinheiro.github.io/CHIKA/frontend-v1/)

**Features:**
- ✅ Real-time AI collaboration (not a mockup!)
- ✅ Visual status updates showing which AI is processing
- ✅ Single synthesized answer from multiple AIs
- ✅ Fully functional backend (SmartRouter + LLM orchestration)

**Demo Mode:**
- Currently: GPT-4 + Ollama (local)
- Production: GPT-4, Claude, Gemini, + any AI you connect

---

## 📊 Architecture

```
┌─────────────────────────────────────────┐
│         CHIKA Frontend (React)          │
│  - Real-time status updates             │
│  - Chat interface                       │
│  - AI avatars with animations           │
└─────────────────┬───────────────────────┘
                  │
                  ↓
┌─────────────────────────────────────────┐
│      CHIKA Backend (FastAPI)            │
│  ┌───────────────────────────────────┐  │
│  │  SmartRouter (Intent Analysis)    │  │
│  └───────────────┬───────────────────┘  │
│                  ↓                       │
│  ┌───────────────────────────────────┐  │
│  │  LLM Router (Multi-Provider)      │  │
│  │  - GPT-4, Claude, Gemini          │  │
│  │  - Ollama (local models)          │  │
│  │  - Priority-based selection       │  │
│  └───────────────┬───────────────────┘  │
│                  ↓                       │
│  ┌───────────────────────────────────┐  │
│  │  AI Collaborator                  │  │
│  │  - Sequential discussion          │  │
│  │  - Context sharing                │  │
│  │  - Synthesis into one answer      │  │
│  └───────────────────────────────────┘  │
└─────────────────────────────────────────┘
```

---

## 🛠️ Tech Stack

**Frontend:**
- HTML5 + Vanilla JS (landing page MVP)
- Lucide Icons (professional icon library)
- GitHub Pages (hosting)

**Backend:**
- FastAPI (Python 3.11+)
- LiteLLM (universal AI gateway, 100+ providers)
- Pydantic V2 (data validation)
- SlowAPI (rate limiting)

**Infrastructure:**
- Cloudflare Tunnel (public access)
- Nohup + PID tracking (process management)

---

## 🚀 Quick Start

### 1. Start Backend

```bash
# Start backend (persistent)
/home/pedro/chika/scripts/start-backend.sh

# Check status
/home/pedro/chika/scripts/status.sh

# View logs
tail -f /tmp/chika_backend.log
```

### 2. Access Demo

Open: [https://ruipedro-pinheiro.github.io/CHIKA/frontend-v1/](https://ruipedro-pinheiro.github.io/CHIKA/frontend-v1/)

---

## 📝 Configuration

**Environment Variables:**

```bash
# .env file location: /home/pedro/chika/backend/.env

# Required for production
OPENAI_API_KEY=sk-...           # GPT-4
ANTHROPIC_API_KEY=sk-ant-...    # Claude
GOOGLE_API_KEY=AI...            # Gemini

# Optional (local models)
OLLAMA_BASE_URL=http://localhost:11434
OLLAMA_MODEL=llama2
```

**Available AIs:**
- GPT-4 (OpenAI) - Priority 2
- Claude (Anthropic) - Priority 2
- Gemini (Google) - Priority 1 (freemium)
- Ollama (Local) - Priority 2
- Mock (Development) - Priority 999

---

## 🎯 Roadmap

### ✅ Phase 0: Market Validation (CURRENT)
- [x] Landing page with live demo
- [x] Real AI collaboration backend
- [x] Visual status updates
- [x] Transparent demo disclaimer
- [ ] Collect 10+ waitlist signups
- [ ] Get developer feedback

### 🚧 Phase 1: Beta Launch (December 2025)
- [ ] User authentication
- [ ] Session persistence
- [ ] Waitlist backend (email storage)
- [ ] Deploy to permanent hosting (Render/Railway)
- [ ] Full AI roster (GPT-4, Claude, Gemini)

### 📅 Phase 2: Production (Q1 2026)
- [ ] Streaming responses (SSE)
- [ ] Context memory (Mem0 integration)
- [ ] API for developers
- [ ] CLI tool
- [ ] Pricing (freemium model)

---

## 📄 License

MIT License - See [LICENSE](LICENSE)

---

## 🤝 Contributing

**We're building in public!**

- Report bugs: [GitHub Issues](https://github.com/ruipedro-pinheiro/CHIKA/issues)
- Suggest features: [Discussions](https://github.com/ruipedro-pinheiro/CHIKA/discussions)
- Join waitlist: [Landing Page](https://ruipedro-pinheiro.github.io/CHIKA/frontend-v1/)

---

## 📊 Status

- **Backend:** ✅ Running (persistent)
- **Frontend:** ✅ Deployed (GitHub Pages)
- **Demo:** ✅ Live and functional
- **Stage:** Pre-launch validation

**Last updated:** 2025-11-08 11:10

---

**Made with 🧠 by collaborative AIs**
