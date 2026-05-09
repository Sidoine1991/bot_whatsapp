import chromadb
import os
from dotenv import load_dotenv
from langchain.document_loaders import PyPDFLoader, TextLoader, DirectoryLoader
from langchain.text_splitter import RecursiveCharacterTextSplitter
import pandas as pd

# Charger les variables d'environnement
load_dotenv()

# Configuration ChromaDB Cloud
client = chromadb.CloudClient(
    api_key=os.getenv('CHROMA_API_KEY'),
    tenant=os.getenv('CHROMA_TENANT'),
    database=os.getenv('CHROMA_DATABASE')
)

# Créer ou récupérer la collection
collection = client.get_or_create_collection(
    name=os.getenv('COLLECTION_NAME', 'ccrb_knowledge_base'),
    metadata={"description": "Base de connaissances CCR-B AgroEco IA Pro"}
)

def ingest_pdf_files(pdf_directory):
    """Ingestion des fichiers PDF"""
    print(f"📁 Traitement des fichiers PDF dans : {pdf_directory}")
    
    try:
        loader = DirectoryLoader(
            pdf_directory,
            glob="**/*.pdf",
            loader_cls=PyPDFLoader,
            show_progress=True,
            use_multithreading=True
        )
        documents = loader.load()
        print(f"✅ {len(documents)} pages PDF chargées")
        return documents
    except Exception as e:
        print(f"❌ Erreur lors du chargement des PDF : {e}")
        return []

def ingest_text_files(txt_directory):
    """Ingestion des fichiers texte et markdown"""
    print(f"📄 Traitement des fichiers texte dans : {txt_directory}")
    
    try:
        loader = DirectoryLoader(
            txt_directory,
            glob="**/*.{txt,md}",
            loader_cls=TextLoader,
            show_progress=True,
            use_multithreading=True
        )
        documents = loader.load()
        print(f"✅ {len(documents)} fichiers texte chargés")
        return documents
    except Exception as e:
        print(f"❌ Erreur lors du chargement des fichiers texte : {e}")
        return []

def ingest_csv_files(csv_directory):
    """Ingestion des fichiers CSV"""
    print(f"📊 Traitement des fichiers CSV dans : {csv_directory}")
    
    documents = []
    try:
        for file in os.listdir(csv_directory):
            if file.endswith('.csv'):
                file_path = os.path.join(csv_directory, file)
                df = pd.read_csv(file_path)
                
                # Convertir le DataFrame en texte structuré
                content = f"Fichier CSV: {file}\n\n"
                content += "Colonnes: " + ", ".join(df.columns.tolist()) + "\n\n"
                content += "Aperçu des données:\n"
                content += df.head(10).to_string()
                
                documents.append({
                    'content': content,
                    'metadata': {
                        'source': file,
                        'type': 'csv',
                        'columns': df.columns.tolist(),
                        'rows': len(df)
                    }
                })
        
        print(f"✅ {len(documents)} fichiers CSV traités")
        return documents
    except Exception as e:
        print(f"❌ Erreur lors du chargement des CSV : {e}")
        return []

def split_documents(documents, chunk_size=1000, chunk_overlap=200):
    """Découpage des documents en chunks"""
    print(f"✂️  Découpage des documents (chunk_size={chunk_size}, overlap={chunk_overlap})")
    
    splitter = RecursiveCharacterTextSplitter(
        chunk_size=chunk_size,
        chunk_overlap=chunk_overlap,
        separators=["\n\n", "\n", " ", ""]
    )
    
    chunks = splitter.split_documents(documents)
    print(f"✅ {len(chunks)} chunks créés")
    return chunks

def add_to_collection(chunks, batch_size=100):
    """Ajout des chunks à la collection ChromaDB"""
    print(f"💾 Ajout des chunks à la collection (batch_size={batch_size})")
    
    total_added = 0
    for i in range(0, len(chunks), batch_size):
        batch = chunks[i:i+batch_size]
        
        documents = [chunk.page_content for chunk in batch]
        ids = [f"doc_{i+j}_{hash(chunk.page_content[:50])}" for j, chunk in enumerate(batch)]
        metadatas = []
        
        for chunk in batch:
            metadata = chunk.metadata.copy() if chunk.metadata else {}
            metadata.update({
                'chunk_index': i + chunks.index(chunk),
                'source': metadata.get('source', 'unknown'),
                'type': metadata.get('type', 'text')
            })
            metadatas.append(metadata)
        
        try:
            collection.add(
                documents=documents,
                ids=ids,
                metadatas=metadatas
            )
            total_added += len(batch)
            print(f"   ✅ Batch {i//batch_size + 1}: {len(batch)} chunks ajoutés")
        except Exception as e:
            print(f"   ❌ Erreur batch {i//batch_size + 1}: {e}")
    
    print(f"🎯 Total de {total_added} chunks ajoutés à la collection")
    return total_added

def main():
    """Fonction principale d'ingestion"""
    print("🚀 Démarrage de l'ingestion des documents dans ChromaDB")
    
    # Créer les répertoires s'ils n'existent pas
    directories = ['knowledge_base/pdf', 'knowledge_base/text', 'knowledge_base/csv']
    for directory in directories:
        os.makedirs(directory, exist_ok=True)
    
    all_documents = []
    
    # Ingestion des différents types de fichiers
    all_documents.extend(ingest_pdf_files('knowledge_base/pdf'))
    all_documents.extend(ingest_text_files('knowledge_base/text'))
    
    # Traitement des CSV
    csv_docs = ingest_csv_files('knowledge_base/csv')
    for csv_doc in csv_docs:
        from langchain.docstore.document import Document
        all_documents.append(Document(
            page_content=csv_doc['content'],
            metadata=csv_doc['metadata']
        ))
    
    if not all_documents:
        print("⚠️  Aucun document trouvé. Veuillez ajouter des fichiers dans les répertoires knowledge_base/")
        return
    
    # Découpage en chunks
    chunks = split_documents(all_documents)
    
    # Ajout à la collection
    add_to_collection(chunks)
    
    # Afficher les statistiques finales
    print(f"\n📊 Statistiques finales :")
    print(f"   📚 Collection : {collection.name}")
    print(f"   📄 Documents originaux : {len(all_documents)}")
    print(f"   🔢 Chunks dans la base : {collection.count()}")
    
    # Test de recherche
    print(f"\n🔍 Test de recherche :")
    test_queries = [
        "Sidoine YEBADOKPO compétences",
        "agroécologie riz Bénin",
        "suivi évaluation MEAL",
        "Python Power BI CCRB"
    ]
    
    for query in test_queries:
        results = collection.query(
            query_texts=[query],
            n_results=2
        )
        print(f"\n   Recherche : '{query}'")
        for i, (doc, distance) in enumerate(zip(results['documents'][0], results['distances'][0])):
            print(f"      {i+1}. (score: {1-distance:.3f}) {doc[:100]}...")

if __name__ == "__main__":
    main()
