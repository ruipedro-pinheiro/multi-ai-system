# 🎯 Chika V1 - Configuration Freemium

## 💡 Architecture Multi-Tier

### FREEMIUM (Gratuit - IA hébergées par nous)
```
✅ Gemini 2.0 Flash (Google AI Studio)
   - 1,500 requêtes/jour gratuit
   - Expert: Factuel, research, multimodal
   
✅ Llama 3.1 70B (Groq)
   - 14,400 requêtes/jour gratuit
   - Expert: Code, général, ultra rapide
   
✅ Mixtral 8x7B (Groq)
   - 14,400 requêtes/jour gratuit
   - Expert: Créatif, multilingue, reasoning
```

**Total: ~30,000 requêtes/jour gratuites avec 3 IA différentes!**

---

### PRO (Payant - Client utilise SES IA)
```
✅ Claude (OAuth ou API key)
✅ ChatGPT (API key)
✅ Gemini Pro (API key)
✅ Ollama (self-hosted)
✅ N'importe quelle IA via LiteLLM
```

**Contexte MCP: ILLIMITÉ**  
**Sessions: ILLIMITÉES**  
**Prix: 20€/mois/user**

---

## 🔑 Setup Freemium (API Keys Gratuites)

### 1. Google AI Studio (Gemini 2.0 Flash)
1. Va sur: https://aistudio.google.com/app/apikey
2. Connecte-toi avec compte Google
3. Clique "Create API Key"
4. Copie la clé

**Limites gratuites:**
- 1,500 requêtes/jour
- 1M tokens/minute
- 15 requêtes/minute

---

### 2. Groq (Llama + Mixtral)
1. Va sur: https://console.groq.com/keys
2. Crée un compte gratuit
3. Clique "Create API Key"
4. Copie la clé

**Limites gratuites:**
- 14,400 requêtes/jour
- 30 requêtes/minute
- Ultra rapide (500+ tokens/sec!)

---

## ⚙️ Configuration Backend

### Fichier `.env`:
```bash
# === FREEMIUM AI (Gratuit) ===
GOOGLE_API_KEY=AIza...  # Gemini 2.0 Flash
GROQ_API_KEY=gsk_...    # Llama + Mixtral

# === PRO USERS (Optionnel) ===
ANTHROPIC_API_KEY=      # Claude (si tu testes PRO tier)
OPENAI_API_KEY=         # ChatGPT (si tu testes PRO tier)
```

---

## 🧠 SmartRouter - Sélection Automatique

Le backend analyse automatiquement le message et route vers les bonnes IA:

### Exemples:

**Message: "Script Python avec crontab"**
→ Sélection: Llama (code) + Gemini (factuel/sysadmin)

**Message: "Écris un article créatif en français"**
→ Sélection: Mixtral (créatif + multilingue)

**Message: "Legal check RGPD compliance"**
→ Sélection: Gemini (factuel/legal)

**Message: "Python code + RGPD check + alternatives créatives"**
→ Sélection: Llama + Gemini + Mixtral (les 3!)

---

## 📊 Monitoring Freemium

### Limites quotidiennes:
- Gemini: 1,500 users max/jour
- Groq: 14,400 users max/jour
- **Total: ~15,000 users actifs/jour possible**

### Passage PRO trigger:
- Contexte limité: 50 messages (freemium) vs ILLIMITÉ (PRO)
- Sessions: 1h/jour (freemium) vs ILLIMITÉES (PRO)
- Upgrade CTA: "Connecte TES IA et débride tout!"

---

## 🚀 Next Steps

1. ✅ Backend configured (SmartRouter + Groq/Gemini)
2. 🚧 Frontend Zen: Thread multi-IA (en cours)
3. 🚧 Frontend Settings: OAuth/API keys setup
4. 🚧 Test flow complet freemium

---

## 💰 Business Model

**Freemium → PRO conversion:**
- Freemium: Limite contexte/sessions → Frustration
- Message: "Tes IA oublient? Passe PRO et connecte TES IA!"
- PRO: Contexte illimité + Sessions illimitées
- Prix: 20€/mois = acceptable vs Claude Pro (20€) + ChatGPT Plus (20€)

**ROI:**
- Coût freemium: 0€ (Google + Groq gratuits)
- Conversion 5%: 50 PRO users sur 1000 freemium
- Revenu: 50 × 20€ = 1,000€/mois
- Profit: 100% (pas de coût infra)

---

**Dernière mise à jour:** 2025-11-08  
**Version:** V1 Freemium Ready
