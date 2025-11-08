# 🇨🇭 CHIKA - Multi-AI Collaboration Platform

> **Utiliser plusieurs IA sans chichi. Elles collaborent, se souviennent de tout, et tu gardes le contrôle.**

---

## 🔥 Le Problème

**Aujourd'hui, utiliser plusieurs IA = bordel:**

- Tu utilises Claude pour le code
- ChatGPT pour la créativité
- Gemini pour le factuel

**Mais:**
- ❌ Elles ne se parlent PAS
- ❌ Tu dois copier-coller partout
- ❌ Elles oublient ton historique
- ❌ Tu payes 40€/mois pour des outils fragmentés

---

## 💡 La Solution: CHIKA

**Une plateforme qui fait collaborer tes IA comme une vraie équipe.**

### Comment ça marche:

```
Toi: "J'ai besoin d'un script Python avec crontab pour backup DB"

CHIKA analyse automatiquement:
→ "script Python" = besoin expert CODE
→ "crontab" = besoin expert SYSADMIN  
→ "backup" = besoin vérif RGPD

CHIKA fait collaborer:

🤖 Claude (Expert Code):
"Ok! Je fais le script. @Gemini vérifie RGPD? @ChatGPT alternatives créatives?"

✨ Gemini (Expert Legal):
"RGPD OK si chiffrement AES-256 + rétention <30j"

🧠 ChatGPT (Expert Créatif):
"Alternative: utilise systemd timer au lieu de cron (meilleur logging)"

🤖 Claude:
"@Pedro Voici ton script:
✅ Backup auto chiffré (RGPD compliant)
✅ systemd timer (plus moderne)
Code prêt!"
```

**Résultat:** 1 question → 3 IA collaborent → Meilleure solution possible!

---

## 🎯 Ce Qui Rend CHIKA Unique

### **1. 🧠 SmartRouter - Sélection Automatique**

Tu ne choisis PAS quelle IA utiliser. CHIKA analyse ton message et sélectionne les meilleures automatiquement:

- **"Code Python bug"** → Claude (expert code)
- **"RGPD compliance"** → Gemini (expert legal)
- **"Blog post créatif"** → ChatGPT (expert créatif)
- **"Script + RGPD + alternatives"** → Les 3 ensemble!

### **2. 🤝 Collaboration Native**

Les IA discutent entre elles:
- Claude propose du code
- Gemini vérifie la sécurité
- ChatGPT suggère améliorations
- Si désaccord → discussion privée jusqu'à consensus
- Tu reçois la solution validée par toute l'équipe

### **3. 💾 Mémoire Illimitée**

**ChatGPT/Claude:** Oublient après X messages

**CHIKA PRO:** N'oublie JAMAIS!

```
Lundi: "Script backup DB"
→ Claude + Gemini répondent

30 jours après: "Améliore le script"
→ CHIKA SE SOUVIENT! ✅
```

Pas de rooms, pas de sessions séparées. **1 chat global qui garde TOUT.**

### **4. 🔐 Tu Gardes le Contrôle**

**Freemium:** Nos IA gratuites (Gemini, Llama, Mixtral)

**PRO:** TES IA!
- Connecte ton Claude Max (OAuth)
- Connecte ton ChatGPT Plus (API key)
- Connecte n'importe quelle IA

**Privacy:** Tes clés = tes données. On ne stocke RIEN chez nous en prod.

---

## 💰 Pricing

### **FREEMIUM - 0€**
```
✅ Gemini 2.0 Flash (gratuit Google)
✅ Llama 3.1 70B (gratuit Groq)
✅ Mixtral 8x7B (gratuit Groq)
✅ Multi-IA collaboration
❌ Contexte limité: 50 messages
```

### **PRO - 20€/mois**
```
✅ Connecte TES IA (OAuth/API keys)
   - Claude (Anthropic)
   - ChatGPT (OpenAI)
   - Gemini (Google)
   - N'importe quelle IA via LiteLLM

✅ Mémoire ILLIMITÉE (n'oublie jamais)
✅ Sessions illimitées
✅ Settings avancés
```

### **ENTERPRISE - Custom**
```
✅ Self-hosted (ta propre infra)
✅ SSO/SAML
✅ Custom branding
✅ Support dédié
```

---

## 🚀 Différence vs Concurrence

| Feature | ChatGPT Plus | Claude Pro | **CHIKA PRO** |
|---------|-------------|-----------|---------------|
| Prix | 20€/mois | 20€/mois | **20€/mois** |
| Multi-IA | ❌ GPT seul | ❌ Claude seul | ✅ **TES IA** |
| Collaboration | ❌ | ❌ | ✅ **Native** |
| Contexte | ~32K tokens | ~200K tokens | ✅ **ILLIMITÉ** |
| Mémoire | ❌ Oublie | ⚠️ Par projet | ✅ **Globale** |
| Privacy | ❌ Cloud | ❌ Cloud | ✅ **TES clés** |

---

## 🏗️ Stack Technique

**Backend:**
- FastAPI (Python)
- SQLAlchemy + SQLite/PostgreSQL
- LiteLLM (100+ providers supportés)
- OAuth2 (Anthropic reverse-engineered)
- WebSocket (real-time)

**Frontend:**
- Vanilla JS (performance max)
- Design system custom
- Interfaces: Zen, Arena, Cards

**AI Orchestration:**
- SmartRouter (intent analysis)
- AICollaborator (multi-AI coordination)
- AI Personas (chaque IA sait qui elle est)
- Context Manager (mémoire illimitée)

**Infra:**
- Docker Compose
- Qdrant (vector DB - RAG futur)
- Self-hostable

---

## 🎯 Use Cases

### **Devs / PowerUsers**
```
- Code review multi-angles (code + security + perf)
- Architecture discussions (plusieurs experts)
- Debug complexe (code + infra + legal)
- Documentation auto (technique + vulgarisée)
```

### **Petites Équipes**
```
- Brainstorm produit (créatif + technique + business)
- Veille techno (research + analysis + synthesis)
- Rédaction contenu (writing + fact-check + SEO)
```

### **Freelances**
```
- Propositions clients (technique + pricing + legal)
- Gestion projets (code + planning + communication)
- Mémoire illimitée = base de connaissances privée
```

---

## 🔐 Sécurité & Privacy

**Input Protection:**
- XSS sanitization
- SQL injection prevention
- Prompt injection filters

**Rate Limiting:**
- 10 req/min par IP
- DDoS protection

**OAuth Security:**
- PKCE flow
- Token refresh auto
- Encrypted storage

**Privacy:**
- API keys jamais loggées
- User-owned credentials
- Self-host option (Enterprise)

---

## 📊 Roadmap

### **V1 - Now (2 semaines)**
- ✅ SmartRouter intelligent
- ✅ Multi-IA collaboration
- ✅ Freemium (Gemini + Groq)
- 🚧 Frontend Zen Mode
- 🚧 OAuth flow complet
- 🚧 Contexte global illimité

### **V2 - M1-M3**
- RAG (upload docs/code)
- Session management
- TUI (terminal interface)
- Plugins système

### **V3 - M6-M12**
- Mobile app
- API publique
- Marketplace plugins
- Enterprise features (SSO, audit)

---

## 🎬 Démo Rapide

**Exemple 1 - Code + Legal:**
```
User: "Script Python backup DB avec crontab"
→ Claude: Code Python
→ Gemini: "RGPD check → chiffrement requis"
→ Claude: "Intègre chiffrement AES-256"
→ User reçoit script production-ready
```

**Exemple 2 - Créatif + Factuel:**
```
User: "Article blog sur l'IA, vérifier les facts"
→ ChatGPT: Rédaction créative
→ Gemini: Fact-checking stats et études
→ User reçoit article vérifié
```

**Exemple 3 - Mémoire:**
```
Jour 1: "Explique-moi les closures JavaScript"
Jour 30: "Donne exemple closure comme l'autre fois"
→ CHIKA SE SOUVIENT de l'explication jour 1! ✅
```

---

## 🚀 Essayer CHIKA

**Freemium (0€):**
1. Va sur chika.app (quand déployé)
2. Commence à chatter
3. IA gratuites répondent automatiquement

**PRO (20€/mois):**
1. Settings → Connecte tes IA (OAuth/API)
2. CHIKA utilise TES abonnements
3. Mémoire illimitée activée

**Enterprise:**
1. Contact: pedro@chika.app
2. Self-host sur ton infra
3. Custom setup

---

## 🇨🇭 Made in Switzerland

**Philosophie:**
- 🎯 Simple, pas de chichi
- 🔐 Privacy-first
- 🛠️ Open source core
- 💪 Self-hostable
- 🧠 Vraiment intelligent (pas juste du marketing)

---

## 📞 Contact

- **GitHub:** github.com/votre-repo/chika
- **Email:** pedro@chika.app
- **Twitter:** @chika_ai

---

## ⚖️ License

- **Core:** MIT (open source)
- **Enterprise:** Commercial license

---

**CHIKA - Utiliser dix IA sans chichi.** 🇨🇭
