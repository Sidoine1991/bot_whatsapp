import chromadb
import os

# Configuration directe sans variables d'environnement
try:
    print("🔗 Connexion à ChromaDB Cloud...")
    
    client = chromadb.CloudClient(
        api_key='ck-3NwusCGa5u3aJB5oZnqQkbehoh5uDCNUdUnBmjvqGN7P',
        tenant='0dc087aa-1492-4485-b346-35546f1fa1ac',
        database='sido'
    )
    
    print("✅ Connexion réussie!")
    
    # Créer ou récupérer la collection
    collection = client.get_or_create_collection(
        name="ccrb_knowledge_base",
        metadata={"description": "Base de connaissances CCR-B AgroEco IA Pro"}
    )
    
    print(f"📚 Collection '{collection.name}' créée/récupérée")
    print(f"📊 Nombre de documents actuels : {collection.count()}")
    
    # Test d'insertion simple
    test_doc = """
    Sidoine Kolaolé YEBADOKPO - Expert Data Science & Agroécologie
    
    Profil professionnel:
    - Conseiller Global Suivi, Évaluation & Apprentissage (MEAL) au CCR-Bénin
    - Data Analyst avec plus de 4 ans d'expérience
    - Développeur Fullstack et expert en IA
    - Spécialisé en agroécologie et filière riz
    
    Compétences techniques:
    - Python: Pandas, NumPy, Scikit-learn, Streamlit
    - R: tidyverse, ggplot2, dplyr
    - SQL: PostgreSQL, MySQL
    - Power BI, Tableau, APIs
    - Développement IA: LangChain, RAG, LLM
    
    Projets réalisés:
    - Interactive Data Analysis Tool (Streamlit)
    - AgriLens AI (diagnostic maladies plantes)
    - Chatbot CV (RAG + LLM)
    - Presence CCRB (app full-stack)
    - Biblio IA / CoranIA / KolaChatBot
    
    Contact: syebadokpo@gmail.com | +229 01 96 91 13 46
    Portfolio: https://huggingface.co/spaces/Sidoineko/portfolio
    """
    
    collection.add(
        documents=[test_doc],
        ids=["sidoine_profile_001"],
        metadatas=[{
            "source": "profile", 
            "type": "cv",
            "author": "sidoine_yebadokpo",
            "date": "2025-01-15"
        }]
    )
    
    print(f"✅ Document de profil ajouté avec succès")
    print(f"📊 Nouveau nombre de documents : {collection.count()}")
    
    # Test de recherche
    print("\n🔍 Tests de recherche:")
    
    test_queries = [
        "compétences Python Sidoine",
        "projets IA réalisés",
        "CCR-Bénin MEAL",
        "agroécologie riz"
    ]
    
    for query in test_queries:
        results = collection.query(
            query_texts=[query],
            n_results=2
        )
        
        print(f"\n   📝 Recherche : '{query}'")
        for i, (doc, distance) in enumerate(zip(results['documents'][0], results['distances'][0])):
            score = 1 - distance
            print(f"      {i+1}. (score: {score:.3f}) {doc[:100]}...")
    
    print("\n🎯 Configuration ChromaDB terminée avec succès!")
    print("📋 Votre base de connaissances est prête pour le bot WhatsApp")
    
except Exception as e:
    print(f"❌ Erreur: {e}")
    print("Veuillez vérifier votre connexion internet et vos clés API")
