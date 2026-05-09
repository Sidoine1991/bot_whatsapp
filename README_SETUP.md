# Configuration ChromaDB pour Bot WhatsApp CCR-B

## 🚀 Installation rapide

### 1. Installer les dépendances
```bash
pip install -r requirements.txt
```

### 2. Tester la connexion ChromaDB
```bash
python setup_chromadb.py
```

### 3. Préparer les documents
Placez vos fichiers dans les répertoires appropriés :
```
knowledge_base/
├── pdf/     # Rapports, CV, publications
├── text/    # Documentation, code, markdown
└── csv/     # Données structurées
```

### 4. Ingestion des documents
```bash
python ingest_documents.py
```

## 📁 Structure des fichiers

- `.env` - Configuration ChromaDB (clés API et identifiants)
- `setup_chromadb.py` - Test de connexion et configuration initiale
- `ingest_documents.py` - Script d'ingestion automatique des documents
- `requirements.txt` - Dépendances Python
- `DOCUMENT_ENTRAINEMENT_BOT_WHATSAPP_COMPLET.md` - Document d'entraînement principal

## 🔧 Variables d'environnement

Le fichier `.env` contient :
```
CHROMA_HOST=api.trychroma.com
CHROMA_API_KEY=REMOVED_API_KEY
CHROMA_TENANT=0dc087aa-1492-4485-b346-35546f1fa1ac
CHROMA_DATABASE=sido
COLLECTION_NAME=ccrb_knowledge_base
```

## 📊 Types de fichiers supportés

- **PDF** : Rapports techniques, publications, CV
- **TXT/MD** : Documentation, code, notes
- **CSV** : Données structurées, indicateurs

## 🎯 Prochaines étapes

1. Ajouter le document d'entraînement principal dans `knowledge_base/text/`
2. Ajouter vos rapports CCR-B dans `knowledge_base/pdf/`
3. Lancer l'ingestion avec `python ingest_documents.py`
4. Tester la recherche sémantique
5. Intégrer avec le bot WhatsApp

## 🔍 Test de recherche

Après ingestion, testez avec :
```python
results = collection.query(
    query_texts=["compétences Sidoine YEBADOKPO"],
    n_results=3
)
```
