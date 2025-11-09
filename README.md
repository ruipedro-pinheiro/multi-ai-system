# CHIKA - Multi-AI Collaboration Platform

> **⚠️ Archived Project** - Market validation experiment (November 2025)

## Overview

CHIKA was an experiment to solve a universal problem: people switch between ChatGPT, Claude, and Gemini constantly, losing context and wasting time comparing answers manually.

**The Vision**: One interface where multiple AIs collaborate automatically, giving you the best answer in seconds instead of manual comparison.

**Reality**: Market validation showed the problem wasn't painful enough. Project archived after honest assessment.

## The Hypothesis

**Problem**: Everyone switches between AIs depending on the task (ChatGPT for general, Claude for reasoning, Gemini for research). Context is lost. Time is wasted.

**Solution**: Ask once → 3 AIs respond → synthesized answer. Stop switching.

**Why It Failed**:
- Major providers solved context management natively (2025)
- Users prefer convenience of "good enough" single AI
- Switching cost > marginal quality benefit
- Timing: competitors closed the window

## Product Vision (3-Tier)

### 🏢 Enterprises
- Self-hosted (Docker/K8s)
- Local AI (Ollama, vLLM)
- Privacy-first, GDPR compliant
- One-time payment model

### 👨‍💻 Developers
- Hybrid: local OR cloud APIs
- CLI/TUI + Web interface
- Full flexibility
- Monthly subscription

### 🌍 General Public
- Hosted SaaS by CHIKA
- Free tier (limited)
- Web interface only
- Freemium model

## Tech Stack

**Backend**: FastAPI, LiteLLM, SQLite  
**Frontend**: Vanilla HTML/CSS/JS (2600 lines, no framework)  
**Infra**: Nginx, SSL, DigitalOcean VPS, systemd

## What I Learned

1. **Validate FIRST** - 3 days of testing saved 6 months of building
2. **Kill fast** - Data > emotions. Sunk cost fallacy is real.
3. **Timing is everything** - Anthropic/OpenAI/Google already solved it
4. **Be honest** - Even if you believe in it, listen to the market

## Stats

- 3 days total investment
- Full production deployment with staging workflow
- 2 waitlist signups
- Honest decision to archive based on validation

---

**Built by Pedro Pinheiro** (École 42 Lausanne) | MIT License | November 2025
