# 🤖 Bot WhatsApp RAG - Assistant CCR-B / AgroEco IA Pro

Bot WhatsApp intelligent basé sur une architecture **RAG** (Retrieval-Augmented Generation), connecté à **ChromaDB Cloud** pour fournir des réponses contextualisées, professionnelles et utiles.

## 🎯 Fonctionnalités

### 🧠 Intelligence Artificielle
- **RAG** : réponses enrichies par recherche sémantique dans la base documentaire
- **Contexte conversationnel** : historique utilisateur pris en compte
- **Réponses structurées** : ton professionnel orienté terrain

### 📱 Intégration WhatsApp
- **Webhook Flask** pour réception et traitement des messages
- **Réponse automatique** via API provider (Evolution API / UltraMSG selon setup)
- **Endpoints de test** pour valider le bot localement

### 📚 Base de connaissances
- Connexion à **ChromaDB Cloud**
- Ingestion de documents métier (texte, PDF, données structurées)
- Recherche des passages les plus pertinents avant génération

## 🏗️ Architecture

```text
WhatsApp -> API Provider -> Webhook Flask -> Bot RAG -> ChromaDB -> Réponse
```

## 📁 Fichiers essentiels

- `whatsapp_personal_bot.py` - Serveur principal recommandé
- `bot_whatsapp_rag.py` - Cœur du moteur RAG
- `whatsapp_webhook.py` - Variante webhook
- `whatsapp_cloud_bot.py` - Variante cloud
- `ingest_documents.py` - Ingestion des documents
- `setup_chromadb.py` - Test de connexion ChromaDB
- `requirements_bot.txt` - Dépendances du bot
- `docker-compose.yml` - Option Docker
- `render.yaml` - Option déploiement Render

## 🚀 Installation rapide

### 1. Installer les dépendances
```bash
pip install -r requirements_bot.txt
```

### 2. Configurer les variables d'environnement
Créer un fichier `.env` :

```env
# ChromaDB
CHROMA_HOST=api.trychroma.com
CHROMA_API_KEY=your_chroma_api_key
CHROMA_TENANT=your_chroma_tenant_id
CHROMA_DATABASE=your_database_name
COLLECTION_NAME=ccrb_knowledge_base

# WhatsApp
WHATSAPP_API_URL=https://api.evolution-api.com
WHATSAPP_TOKEN=your_whatsapp_token
WHATSAPP_INSTANCE_ID=your_instance_id
WEBHOOK_VERIFY_TOKEN=your_verify_token

# LLM (optionnel)
OPENAI_API_KEY=
GEMINI_API_KEY=
LLM_MODEL=gpt-3.5-turbo

# Flask
PORT=5000
```

### 3. Démarrer le bot (Windows PowerShell)
```powershell
$env:PYTHONUTF8='1'
py -3.14 whatsapp_personal_bot.py
```

## 🧪 Vérification rapide

### 1. Santé du service
```bash
curl http://127.0.0.1:5000/health
```

### 2. Test du bot en local
```bash
curl -X POST "http://127.0.0.1:5000/test" \
  -H "Content-Type: application/json" \
  -d "{\"phone\":\"test_user\",\"message\":\"Bonjour\"}"
```

## 📥 Ingestion de connaissances

```bash
py -3.14 ingest_documents.py
py -3.14 setup_chromadb.py
```

## 🌐 Déploiement

### Option 1. Gunicorn
```bash
gunicorn -w 4 -b 0.0.0.0:5000 whatsapp_personal_bot:app
```

### Option 2. Render
Le fichier `render.yaml` est prêt pour un déploiement sur Render.

### Option 3. Docker
Utiliser `docker-compose.yml` en adaptant les variables d'environnement.

## 🔒 Sécurité

- Ne jamais commiter `.env` ni les clés API
- Utiliser HTTPS en production pour les webhooks
- Régénérer les tokens en cas de fuite

## 🆘 Dépannage

1. **Le bot ne démarre pas sur Windows**
   - Relancer avec `PYTHONUTF8=1`

2. **Connexion ChromaDB échouée**
   - Vérifier `CHROMA_API_KEY`, `CHROMA_TENANT`, `CHROMA_DATABASE`

3. **Réponses peu pertinentes**
   - Refaire l’ingestion des documents et vérifier la collection

4. **Webhook non reçu**
   - Vérifier URL publique, token de vérification et configuration provider
