import subprocess
import sys
import os

def run_jupyter_notebook():
    """Lancer le notebook Jupyter pour configurer ChromaDB"""
    
    notebook_path = "setup_chromadb_notebook.ipynb"
    
    if not os.path.exists(notebook_path):
        print(f"❌ Fichier {notebook_path} non trouvé")
        return False
    
    print("🚀 Lancement du notebook Jupyter pour configurer ChromaDB...")
    print("📋 Le notebook va:")
    print("   1. Installer les dépendances")
    print("   2. Se connecter à ChromaDB Cloud")
    print("   3. Créer la collection 'ccrb_knowledge_base'")
    print("   4. Ajouter votre profil professionnel")
    print("   5. Tester la recherche sémantique")
    print()
    
    try:
        # Lancer Jupyter Notebook
        subprocess.run([sys.executable, "-m", "jupyter", "notebook", notebook_path], check=True)
        return True
    except subprocess.CalledProcessError as e:
        print(f"❌ Erreur lors du lancement: {e}")
        print("💡 Solution alternative:")
        print("   1. Ouvrez manuellement le fichier 'setup_chromadb_notebook.ipynb'")
        print("   2. Copiez-collez le code dans Jupyter Notebook ou Google Colab")
        return False
    except FileNotFoundError:
        print("❌ Jupyter n'est pas installé")
        print("📦 Installation de Jupyter:")
        print("   pip install jupyter")
        return False

if __name__ == "__main__":
    success = run_jupyter_notebook()
    if success:
        print("✅ Notebook lancé avec succès!")
    else:
        print("⚠️  Veuillez installer Jupyter et réessayer")
