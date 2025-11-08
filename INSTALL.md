# 🚀 Chika Installation Guide

Three ways to install Chika:

---

## 1️⃣ One-Click Install (Recommended)

```bash
curl -fsSL https://raw.githubusercontent.com/ruipedro-pinheiro/multi-ai-system/main/install.sh | bash
```

**That's it!** Open http://localhost:3000

---

## 2️⃣ Manual Install

```bash
# Clone
git clone https://github.com/ruipedro-pinheiro/multi-ai-system.git
cd multi-ai-system

# Configure (optional - works without keys)
cp .env.example .env
# Edit .env with your API keys if you want cloud AIs

# Deploy
./deploy.sh

# Open
open http://localhost:3000
```

---

## 3️⃣ Development Install

```bash
# Clone
git clone https://github.com/ruipedro-pinheiro/multi-ai-system.git
cd multi-ai-system

# Backend
cd backend
pip install -r requirements.txt
python main.py

# Frontend (new terminal)
cd frontend
npm install
npm run dev

# Open
open http://localhost:3000
```

---

## ⚙️ Configuration

Edit `.env` to add API keys (all optional):

```bash
# Optional cloud AIs
ANTHROPIC_API_KEY=sk-ant-...
OPENAI_API_KEY=sk-...
GOOGLE_API_KEY=AI...

# Local AI (free, no keys needed!)
OLLAMA_BASE_URL=http://localhost:11434
OLLAMA_MODEL=llama2
```

**Note:** Chika works with local Ollama by default. No API keys needed!

---

## 🐳 Docker Commands

```bash
# Start
docker-compose up -d

# Stop
docker-compose down

# Logs
docker-compose logs -f

# Restart
docker-compose restart

# Update
git pull && docker-compose up -d --build
```

---

## 🧪 Testing

```bash
# Backend tests
cd backend
pip install -r requirements-dev.txt
pytest

# Check security
pytest tests/test_security.py -v
```

---

## 🔧 Troubleshooting

### Port already in use
```bash
# Change ports in docker-compose.yml
ports:
  - "3001:80"  # Frontend
  - "8001:8000"  # Backend
```

### Docker not running
```bash
# Start Docker
sudo systemctl start docker

# Or on Mac
open -a Docker
```

### Permission denied
```bash
# Add user to docker group
sudo usermod -aG docker $USER
# Logout and login again
```

---

## 🎯 Quick Start

1. Open http://localhost:3000
2. Click **+** to create room
3. Select AIs (Claude, GPT, etc.)
4. Send: `Hello @claude and @gpt!`
5. Watch them collaborate! 🎉

---

## 📝 System Requirements

- **OS:** Linux, macOS, Windows (WSL2)
- **Docker:** 20.10+
- **RAM:** 2GB minimum, 4GB recommended
- **Disk:** 1GB for Docker images

---

## 🆘 Support

- **Issues:** https://github.com/ruipedro-pinheiro/multi-ai-system/issues
- **Docs:** See README.md
- **Email:** ruipedro.pinheiro@proton.me
