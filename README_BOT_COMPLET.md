# 🤖 Bot WhatsApp RAG - Assistant CCR-B / AgroEco IA Pro

Bot personnel intelligent pour Sidoine Kolaolé YEBADOKPO avec base de connaissances ChromaDB.

## 🎯 Fonctionnalités

### 🧠 Intelligence Artificielle
- **RAG (Retrieval-Augmented Generation)** : Réponses basées sur la base de connaissances
- **LLM Integration** : Génération de réponses contextuelles
- **Memory** : Historique de conversation maintenu
- **Semantic Search** : Recherche sémantique dans les documents

### 📱 WhatsApp Integration
- **Evolution API** : Intégration professionnelle
- **Webhook** : Réception et traitement des messages
- **Auto-response** : Réponses automatiques intelligentes
- **Media support** : Gestion des différents types de messages

### 📊 Base de Connaissances
- **Profil complet** : CV, compétences, expériences
- **Projets** : Réalisations techniques et IA
- **Expertise** : Agroécologie, data science, MEAL
- **Documentation** : Publications, formations, certifications

## 🏗️ Architecture

```
WhatsApp → Evolution API → Webhook Flask → Bot RAG → ChromaDB → LLM → Réponse
```

### Composants
1. **whatsapp_webhook.py** : Serveur Flask pour les webhooks WhatsApp
2. **bot_whatsapp_rag.py** : Cœur du bot avec logique RAG
3. **interface_test_bot.py** : Interface Streamlit pour les tests
4. **ChromaDB Cloud** : Base de données vectorielle
5. **LLM** : Modèle de langage pour la génération

## 🚀 Installation et Configuration

### 1. Installation des dépendances
```bash
pip install -r requirements_bot.txt
```

### 2. Configuration des variables d'environnement
Créer un fichier `.env` :
```env
# ChromaDB Configuration
CHROMA_HOST=api.trychroma.com
CHROMA_API_KEY=ck-3NwusCGa5u3aJB5oZnqQkbehoh5uDCNUdUnBmjvqGN7P
CHROMA_TENANT=0dc087aa-1492-4485-b346-35546f1fa1ac
CHROMA_DATABASE=sido
COLLECTION_NAME=ccrb_knowledge_base

# WhatsApp Configuration
WHATSAPP_API_URL=https://api.evolution-api.com
WHATSAPP_TOKEN=votre_token_evolution
WHATSAPP_INSTANCE_ID=votre_instance_id
WEBHOOK_VERIFY_TOKEN=sidoine_bot_token_2025

# LLM Configuration
OPENAI_API_KEY=votre_cle_openai
GEMINI_API_KEY=votre_cle_gemini
LLM_MODEL=gpt-3.5-turbo

# Flask Configuration
PORT=5000
```

### 3. Configuration de la base de connaissances
Exécuter le notebook Jupyter :
```bash
jupyter notebook setup_chromadb_notebook.ipynb
```

Ou utiliser le script Python :
```bash
python test_chromadb_simple.py
```

## 🧪 Tests

### 1. Test du bot en ligne de commande
```bash
python bot_whatsapp_rag.py
```

### 2. Interface web de test
```bash
streamlit run interface_test_bot.py
```

### 3. Test du webhook
```bash
python whatsapp_webhook.py
```

## 📱 Déploiement WhatsApp

### 1. Configuration Evolution API
1. Créer un compte sur [Evolution API](https://evolution-api.com)
2. Créer une instance WhatsApp
3. Configurer le webhook URL : `https://votre-domaine.com/webhook`
4. Obtenir le token et l'instance ID

### 2. Configuration du webhook
```bash
# Démarrer le serveur webhook
python whatsapp_webhook.py

# Ou avec Gunicorn pour la production
gunicorn -w 4 -b 0.0.0.0:5000 whatsapp_webhook:app
```

### 3. Vérification du webhook
```bash
curl "https://votre-domaine.com/webhook?hub.mode=subscribe&hub.verify_token=sidoine_bot_token_2025&hub.challenge=test_challenge"
```

## 🔧 Personnalisation

### Ajouter de nouvelles connaissances
1. Ajouter des documents dans `knowledge_base/`
2. Exécuter l'ingestion :
```bash
python ingest_documents.py
```

### Modifier le style de réponse
Éditer la fonction `generate_llm_response` dans `bot_whatsapp_rag.py`

### Ajouter de nouvelles fonctionnalités
- Créer de nouvelles méthodes dans la classe `WhatsAppRAGBot`
- Ajouter des endpoints dans `whatsapp_webhook.py`
- Étendre l'interface Streamlit

## 📊 Monitoring

### Statistiques en temps réel
```bash
curl https://votre-domaine.com/stats
```

### Santé du service
```bash
curl https://votre-domaine.com/health
```

### Logs
Les logs sont configurés pour afficher :
- Connexions WhatsApp
- Requêtes ChromaDB
- Réponses générées
- Erreurs éventuelles

## 🔒 Sécurité

### Tokens et clés API
- Utiliser des variables d'environnement
- Ne jamais exposer les clés dans le code
- Utiliser HTTPS pour le webhook

### Validation des entrées
- Validation des messages entrants
- Filtrage des contenus malveillants
- Limitation de taux (rate limiting)

## 🚀 Déploiement Production

### 1. Serveur web
```bash
# Avec Gunicorn
gunicorn -w 4 -b 0.0.0.0:5000 whatsapp_webhook:app

# Avec Docker
docker build -t whatsapp-bot .
docker run -p 5000:5000 whatsapp-bot
```

### 2. Reverse Proxy (Nginx)
```nginx
server {
    listen 80;
    server_name votre-domaine.com;
    
    location / {
        proxy_pass http://localhost:5000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
    }
}
```

### 3. SSL/TLS
Utiliser Let's Encrypt pour HTTPS :
```bash
certbot --nginx -d votre-domaine.com
```

## 📈 Performance

### Optimisations
- **Caching** : Mise en cache des réponses fréquentes
- **Batch processing** : Traitement par lot des requêtes
- **Connection pooling** : Réutilisation des connexions ChromaDB
- **Async processing** : Traitement asynchrone des messages

### Monitoring
- **Response time** : Temps de réponse moyen
- **Error rate** : Taux d'erreurs
- **Memory usage** : Utilisation mémoire
- **API calls** : Nombre d'appels API

## 🆘 Support et Dépannage

### Problèmes courants
1. **Connexion ChromaDB échouée**
   - Vérifier les clés API
   - Confirmer la connectivité internet

2. **Webhook non reçu**
   - Vérifier l'URL du webhook
   - Confirmer le token de vérification

3. **Réponses vides**
   - Vérifier la base de connaissances
   - Confirmer la configuration LLM

### Logs de debug
```python
import logging
logging.basicConfig(level=logging.DEBUG)
```

## 📝 Documentation Complémentaire

### Guide d'utilisation
1. [Configuration initiale](#installation-et-configuration)
2. [Test du bot](#tests)
3. [Déploiement WhatsApp](#déploiement-whatsapp)
4. [Personnalisation](#personnalisation)

### API Reference
- **GET /health** : Vérification de santé
- **GET /stats** : Statistiques du bot
- **POST /test** : Test du bot
- **POST /webhook** : Webhook WhatsApp

## 👤 À Propos

**Développé par** : Sidoine Kolaolé YEBADOKPO  
**Email** : syebadokpo@gmail.com  
**Portfolio** : https://huggingface.co/spaces/Sidoineko/portfolio  
**GitHub** : https://github.com/Sidoineko

---

*Bot WhatsApp intelligent avec RAG pour l'assistance professionnelle en Data Science et Agroécologie*
