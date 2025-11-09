# 🤖 CHIKA - Multi-AI Collaboration Platform

**One question. Multiple AIs discuss. One superior answer.**

[![Live Demo](https://img.shields.io/badge/demo-live-brightgreen)](https://chika.page)
[![Status](https://img.shields.io/badge/status-beta-yellow)](https://chika.page)
[![License](https://img.shields.io/badge/license-MIT-blue.svg)](LICENSE)
[![Python](https://img.shields.io/badge/python-3.13-blue.svg)](https://www.python.org/)

---

## 🚀 **TRY IT NOW**

**👉 [https://chika.page](https://chika.page) 👈**

**Free demo:** 10 questions per day (no signup required)

---

## 🎯 What is CHIKA?

CHIKA makes multiple AI models (GPT-4, Claude, Gemini) **collaborate autonomously** to give you one synthesized, high-quality answer.

### The Problem
- Switching between ChatGPT → Claude → Gemini
- Copying context manually
- No collaboration between AIs
- Hallucinations not cross-checked

### The Solution
```
Your Question
     ↓
┌────────────────────────────┐
│  GPT-4 proposes answer     │
│  Claude challenges it      │
│  Gemini adds perspective   │
│  AIs reach consensus       │
└────────────────────────────┘
     ↓
One Superior Answer
```

**Key Features:**
- ✅ **Autonomous discussion:** AIs decide when they've reached consensus
- ✅ **Shared context:** No token waste repeating information
- ✅ **Hard safeguards:** MAX 5 rounds (prevents infinite loops)
- ✅ **Daily reset:** 10 queries/day (resets at midnight UTC)
- ✅ **Real AI names:** See which model said what (GPT-4, Claude, Gemini)

---

## 🛡️ Production Safeguards

### Critical Circuit Breakers (Added 2025-11-09)

1. **MAX_DISCUSSION_ROUNDS = 5**
   - Hard limit prevents infinite loops
   - Guarantees completion in <30 seconds
   - Protects against API cost explosion

2. **Multiple Consensus Keywords**
   - Detects: CONSENSUS, AGREE, AGREED, FINAL, CONCLUDED, COMPLETE
   - Fuzzy matching (case-insensitive)
   - Prevents missed signals

3. **Daily Rate Limit Reset**
   - 10 queries per day (not forever)
   - Resets at midnight UTC
   - Users can return daily

4. **Health Monitoring**
   - `/health` endpoint for uptime checks
   - Real-time AI availability status

5. **Transparency**
   - Real AI names shown (GPT-4, Claude, Gemini)
   - No "smoke and mirrors"

**See:** [SAFEGUARDS_APPLIED.md](SAFEGUARDS_APPLIED.md) for full details

---

## 🏗️ Architecture

```
┌─────────────────────────────────────────┐
│         Frontend (Vanilla JS)            │
│  - Real-time status                      │
│  - Collapsible AI discussion view        │
│  - Query counter UI                      │
└─────────────────┬────────────────────────┘
                  │
                  ↓ HTTPS (Nginx)
┌─────────────────────────────────────────┐
│      Backend (FastAPI + LiteLLM)        │
│                                          │
│  /demo/chat                              │
│  ├─ Check rate limit (daily reset)      │
│  ├─ Multi-AI discussion (max 5 rounds)  │
│  ├─ Consensus detection (6 keywords)    │
│  └─ Synthesize final answer             │
│                                          │
│  /demo/session                           │
│  └─ Restore conversation (F5 support)   │
│                                          │
│  /demo/session/reset                     │
│  └─ Clear messages (keep query count)   │
│                                          │
│  /health                                 │
│  └─ Backend status + available AIs      │
│                                          │
└─────────────────┬────────────────────────┘
                  │
      ┌───────────┼───────────┐
      ↓           ↓           ↓
   GPT-4      Claude      Gemini
```

---

## 🚀 Quick Start

### Production (VPS)

**Live Site:** https://chika.page

```bash
# Check status
ssh root@64.226.98.60 "systemctl status chika.service"

# View logs
ssh root@64.226.98.60 "journalctl -u chika.service -f"

# Restart
ssh root@64.226.98.60 "systemctl restart chika.service"
```

### Local Development

```bash
# 1. Clone repo
git clone https://github.com/ruipedro-pinheiro/CHIKA.git
cd CHIKA

# 2. Setup backend
cd backend
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt

# 3. Configure .env
cp .env.example .env
# Add your API keys:
# OPENAI_API_KEY=sk-...
# ANTHROPIC_API_KEY=sk-ant-...
# GOOGLE_API_KEY=AI...

# 4. Start backend
python3 main.py

# 5. Open frontend
# Serve frontend-v1/index.html on local server
```

---

## 📊 Tech Stack

**Frontend:**
- HTML5 + Vanilla JavaScript
- No frameworks (lightweight, fast)
- Collapsible UI for AI discussions

**Backend:**
- FastAPI (Python 3.13)
- LiteLLM (multi-provider AI gateway)
- SQLite (demo sessions + rate limiting)
- Pydantic V2 (data validation)

**Infrastructure:**
- VPS: DigitalOcean (64.226.98.60)
- Nginx reverse proxy
- Systemd service management
- SQLite database (migrated with last_query_date)

**AI Providers:**
- OpenAI (GPT-4)
- Anthropic (Claude)
- Google (Gemini)

---

## 🧪 Testing

### Run Safeguards Verification

```bash
./test_safeguards_simple.sh
```

**Output:**
```
✅ All Python files have valid syntax
✅ Rollback tag: v0.1-pre-safeguards
✅ Current tag: v0.2-with-safeguards
✅ MAX_DISCUSSION_ROUNDS = 5
✅ CONSENSUS_KEYWORDS defined
✅ check_consensus() function
✅ AI_DISPLAY_NAMES mapping
✅ last_query_date column added
✅ reset_if_new_day() method
✅ Daily limit message
✅ /health endpoint added
✅ Database migrated
```

### Manual Testing

```bash
# 1. Health check
curl https://chika.page/health

# 2. Demo query
curl -X POST https://chika.page/demo/chat \
  -H "Content-Type: application/json" \
  -d '{"content":"What is 2+2?"}'

# 3. Reset conversation
curl -X DELETE https://chika.page/demo/session/reset \
  -b "chika_demo_session=YOUR_SESSION_ID"
```

---

## 📁 Project Structure

```
chika/
├── backend/
│   ├── main.py                      # FastAPI app + /health endpoint
│   ├── models/
│   │   └── room.py                  # DemoSession with daily reset
│   ├── routes/
│   │   ├── demo.py                  # Demo endpoints + safeguards
│   │   └── waitlist.py              # Waitlist management
│   ├── providers/
│   │   └── llm_router.py            # Multi-AI routing
│   ├── security/
│   │   ├── input_sanitizer.py      # XSS prevention
│   │   └── prompt_filter.py        # Injection detection
│   └── chika.db                     # SQLite database
├── frontend-v1/
│   └── index.html                   # Main demo interface
├── SAFEGUARDS_APPLIED.md            # Full safeguards documentation
├── DEPLOYMENT_READY.md              # Deployment guide
├── test_safeguards_simple.sh        # Verification script
└── README.md                        # This file
```

---

## 🔐 Security & Rate Limiting

### Rate Limiting
- **10 queries per day** (resets at midnight UTC)
- Cookie-based session tracking (30-day expiry)
- IP address + User-Agent logged

### Input Validation
- XSS sanitization (InputSanitizer)
- Prompt injection detection (PromptSecurityFilter)
- Content length limits (1-5000 chars)

### Production Safeguards
- MAX_DISCUSSION_ROUNDS = 5 (prevents infinite loops)
- Database migration with last_query_date column
- Graceful error handling
- Health monitoring endpoint

---

## 📈 Roadmap

### ✅ Phase 0: MVP + Safeguards (COMPLETE)
- [x] Multi-AI collaboration backend
- [x] Autonomous consensus detection
- [x] Production safeguards (MAX_ROUNDS, daily reset, real AI names)
- [x] Demo UI with collapsible discussion view
- [x] Health monitoring endpoint
- [x] VPS deployment (https://chika.page)

### 🚧 Phase 1: Beta Features (December 2025)
- [ ] User authentication (OAuth)
- [ ] Persistent chat history
- [ ] Streaming responses (SSE)
- [ ] Advanced AI routing (cost optimization)
- [ ] Analytics dashboard

### 📅 Phase 2: Production Launch (Q1 2026)
- [ ] Freemium pricing model
- [ ] API for developers
- [ ] CLI tool
- [ ] Context memory (Mem0 integration)
- [ ] Mobile app

---

## 🐛 Known Issues

- [x] ~~Frontend: `messagesDiv` duplicate declaration~~ (FIXED 2025-11-09)
- [x] ~~Backend: Missing /health endpoint~~ (FIXED 2025-11-09)
- [x] ~~Rate limiting: No daily reset~~ (FIXED 2025-11-09)
- [x] ~~Consensus detection: Single keyword~~ (FIXED 2025-11-09)
- [x] ~~AI names: Generic "AI-1, AI-2"~~ (FIXED 2025-11-09)

**Report bugs:** [GitHub Issues](https://github.com/ruipedro-pinheiro/CHIKA/issues)

---

## 🔄 Deployment

### Rollback (if needed)

```bash
# Checkout previous stable version
git checkout v0.1-pre-safeguards

# Copy to VPS
scp backend/main.py root@64.226.98.60:/home/chika/app/backend/
ssh root@64.226.98.60 "systemctl restart chika.service"
```

### Deploy New Version

```bash
# 1. Tag new version
git tag -a v0.3-feature-name -m "Description"

# 2. Copy to VPS
scp backend/main.py root@64.226.98.60:/home/chika/app/backend/
scp frontend-v1/index.html root@64.226.98.60:/home/chika/app/frontend-v1/

# 3. Restart
ssh root@64.226.98.60 "systemctl restart chika.service"

# 4. Verify
curl https://chika.page/health
```

---

## 📊 Production Metrics

**Site:** https://chika.page  
**Backend:** 64.226.98.60:8000  
**Database:** SQLite (demo_sessions, rooms, messages)  
**Uptime:** Monitored via /health endpoint  
**Last Deploy:** 2025-11-09 16:41 UTC  
**Version:** v0.2-with-safeguards  

---

## 📄 License

MIT License - See [LICENSE](LICENSE)

---

## 🤝 Contributing

We're building in public!

- **Try the demo:** [https://chika.page](https://chika.page)
- **Report bugs:** [GitHub Issues](https://github.com/ruipedro-pinheiro/CHIKA/issues)
- **Suggest features:** [Discussions](https://github.com/ruipedro-pinheiro/CHIKA/discussions)
- **Read safeguards:** [SAFEGUARDS_APPLIED.md](SAFEGUARDS_APPLIED.md)

---

**Built with production-grade safeguards 🛡️**

**Last updated:** 2025-11-09 16:45 UTC  
**Status:** LIVE on https://chika.page
