import chromadb
import os
from dotenv import load_dotenv

# Charger les variables d'environnement
load_dotenv()

# Configuration ChromaDB Cloud
client = chromadb.CloudClient(
    host='api.trychroma.com',
    api_key='REMOVED_API_KEY',
    tenant='0dc087aa-1492-4485-b346-35546f1fa1ac',
    database='sido'
)

# Créer ou récupérer la collection
collection = client.get_or_create_collection(
    name="ccrb_knowledge_base",
    metadata={"description": "Base de connaissances CCR-B AgroEco IA Pro"}
)

print("✅ Connexion ChromaDB établie")
print(f"📚 Collection '{collection.name}' prête")
print(f"📊 Nombre de documents actuels : {collection.count()}")

# Afficher les informations sur la base de données
print("\n🔍 Informations sur la collection :")
print(f"   - ID : {collection.id}")
print(f"   - Name : {collection.name}")
print(f"   - Metadata : {collection.metadata}")

# Test d'insertion simple
try:
    # Ajouter un document de test
    test_doc = """
    Sidoine Kolaolé YEBADOKPO est un expert en Data Science et Agroécologie.
    Il travaille comme Conseiller Global Suivi, Évaluation & Apprentissage (MEAL) 
    au Conseil de Concertation des Riziculteurs du Bénin (CCR-Bénin).
    Ses compétences incluent Python, R, SQL, Power BI et le développement d'applications IA.
    """
    
    collection.add(
        documents=[test_doc],
        ids=["test_document_001"],
        metadatas=[{"source": "setup_test", "type": "profile"}]
    )
    
    print(f"\n✅ Document de test ajouté avec succès")
    print(f"📊 Nouveau nombre de documents : {collection.count()}")
    
    # Test de recherche
    results = collection.query(
        query_texts=["Data Science CCR-B"],
        n_results=2
    )
    
    print("\n🔍 Test de recherche :")
    for i, (doc, distance) in enumerate(zip(results['documents'][0], results['distances'][0])):
        print(f"   Résultat {i+1} (distance: {distance:.4f}):")
        print(f"   {doc[:100]}...")
    
except Exception as e:
    print(f"❌ Erreur lors du test : {e}")

print("\n🎯 Configuration ChromaDB terminée !")
