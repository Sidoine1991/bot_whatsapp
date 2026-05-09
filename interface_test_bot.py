"""
🧪 Interface de Test pour le Bot WhatsApp RAG
Interface Streamlit pour tester et interagir avec le bot
"""

import streamlit as st
import sys
import os
from datetime import datetime

# Ajouter le répertoire courant au path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from bot_whatsapp_rag import WhatsAppRAGBot

# Configuration de la page
st.set_page_config(
    page_title="Assistant CCR-B AgroEco IA Pro",
    page_icon="🤖",
    layout="wide",
    initial_sidebar_state="expanded"
)

# CSS personnalisé
st.markdown("""
<style>
    .main-header {
        background: linear-gradient(90deg, #667eea 0%, #764ba2 100%);
        padding: 2rem;
        border-radius: 10px;
        color: white;
        text-align: center;
        margin-bottom: 2rem;
    }
    
    .message-user {
        background: #e3f2fd;
        padding: 1rem;
        border-radius: 10px;
        margin: 0.5rem 0;
        border-left: 4px solid #2196f3;
    }
    
    .message-bot {
        background: #f3e5f5;
        padding: 1rem;
        border-radius: 10px;
        margin: 0.5rem 0;
        border-left: 4px solid #9c27b0;
    }
    
    .sidebar-info {
        background: #f5f5f5;
        padding: 1rem;
        border-radius: 10px;
        margin: 1rem 0;
    }
    
    .skill-tag {
        display: inline-block;
        background: #e8f5e8;
        padding: 0.3rem 0.8rem;
        border-radius: 20px;
        margin: 0.2rem;
        font-size: 0.9rem;
        border: 1px solid #4caf50;
    }
    
    .project-card {
        background: white;
        padding: 1rem;
        border-radius: 10px;
        margin: 0.5rem 0;
        border: 1px solid #e0e0e0;
        box-shadow: 0 2px 4px rgba(0,0,0,0.1);
    }
</style>
""", unsafe_allow_html=True)

def initialize_bot():
    """Initialiser le bot"""
    if 'bot' not in st.session_state:
        with st.spinner("🤖 Initialisation de l'assistant IA..."):
            st.session_state.bot = WhatsAppRAGBot()
            st.session_state.messages = []
        st.success("✅ Assistant prêt !")

def display_header():
    """Afficher l'en-tête"""
    st.markdown("""
    <div class="main-header">
        <h1>🤖 Assistant Intelligent CCR-B / AgroEco IA Pro</h1>
        <p>Bot personnel de Sidoine Kolaolé YEBADOKPO - Expert Data Science & Agroécologie</p>
        <p>📧 syebadokpo@gmail.com | 📱 +229 01 96 91 13 46 | 🌐 Cotonou, Bénin</p>
    </div>
    """, unsafe_allow_html=True)

def display_sidebar():
    """Afficher la barre latérale"""
    st.sidebar.title("🔧 Configuration")
    
    # Informations sur le bot
    st.sidebar.markdown("""
    <div class="sidebar-info">
        <h4>📊 Statistiques du Bot</h4>
        <p>📚 Documents: <strong>Base ChromaDB</strong></p>
        <p>🤖 Modèle: <strong>RAG + LLM</strong></p>
        <p>📱 Plateforme: <strong>WhatsApp</strong></p>
    </div>
    """, unsafe_allow_html=True)
    
    # Domaines d'expertise
    st.sidebar.markdown("### 🌟 Domaines d'Expertise")
    
    expertise = [
        "📊 Data Science & Analyse",
        "🌱 Agroécologie",
        "🌾 Filière Riz",
        "📈 Suivi-Évaluation (MEAL)",
        "🤖 IA & Machine Learning",
        "🔧 Automatisation",
        "📱 Développement Web"
    ]
    
    for item in expertise:
        st.sidebar.markdown(f"• {item}")
    
    # Actions rapides
    st.sidebar.markdown("### ⚡ Actions Rapides")
    
    if st.sidebar.button("🗑️ Vider l'historique"):
        st.session_state.messages = []
        st.session_state.bot.conversation_history = {}
        st.rerun()
    
    if st.sidebar.button("📊 Statistiques"):
        show_statistics()
    
    if st.sidebar.button("📝 Documentation"):
        show_documentation()

def show_statistics():
    """Afficher les statistiques"""
    st.markdown("### 📊 Statistiques d'utilisation")
    
    if hasattr(st.session_state.bot, 'conversation_history'):
        total_conversations = len(st.session_state.bot.conversation_history)
        total_messages = sum(len(messages) for messages in st.session_state.bot.conversation_history.values())
        
        col1, col2 = st.columns(2)
        with col1:
            st.metric("Conversations", total_conversations)
        with col2:
            st.metric("Messages total", total_messages)
        
        st.info(f"📚 Base de connaissances: {st.session_state.bot.collection.count() if st.session_state.bot.collection else 'Non connectée'} documents")

def show_documentation():
    """Afficher la documentation"""
    st.markdown("### 📝 Documentation du Bot")
    
    st.markdown("""
    #### 🎯 Objectif
    Assistant intelligent spécialisé dans l'agroécologie, la data science et le développement IA pour Sidoine YEBADOKPO.
    
    #### 🔧 Fonctionnalités
    - **RAG**: Recherche sémantique dans la base de connaissances
    - **LLM**: Génération de réponses contextuelles
    - **Historique**: Maintien du contexte conversationnel
    - **WhatsApp**: Intégration avec Evolution API
    
    #### 📚 Sources de connaissances
    - Profil professionnel complet
    - Compétences techniques
    - Projets réalisés
    - Expériences professionnelles
    - Publications scientifiques
    
    #### 🎨 Style de réponse
    - Professionnel et structuré
    - Basé sur les données disponibles
    - Format: Contexte → Analyse → Recommandations
    """)

def display_chat_interface():
    """Afficher l'interface de chat"""
    st.markdown("### 💬 Discussion avec l'Assistant")
    
    # Afficher l'historique des messages
    for message in st.session_state.messages:
        with st.chat_message(message["role"]):
            st.markdown(message["content"])
    
    # Zone de saisie avec st.chat_input (évite la boucle infinie)
    user_input = st.chat_input("💭 Posez votre question...")
    
    # Traitement du message
    if user_input and user_input.strip():
        # Ajouter le message de l'utilisateur
        st.session_state.messages.append({
            "role": "user",
            "content": user_input
        })
        
        # Générer la réponse du bot
        with st.spinner("🤖 Réflexion en cours..."):
            bot_response = st.session_state.bot.process_message(
                user_input, 
                "streamlit_user"
            )
        
        # Ajouter la réponse du bot
        st.session_state.messages.append({
            "role": "assistant",
            "content": bot_response
        })
        
        # Rafraîchir la page
        st.rerun()

def display_quick_questions():
    """Afficher des questions rapides"""
    st.markdown("### 🎯 Questions Rapides")
    
    quick_questions = [
        "Quelles sont les compétences techniques de Sidoine ?",
        "Quels projets IA a-t-il réalisés ?",
        "Quel est son parcours au CCR-Bénin ?",
        "Comment puis-je le contacter ?",
        "Quelles sont ses expertises en agroécologie ?",
        "Quels outils maîtrise-t-il en data science ?"
    ]
    
    cols = st.columns(3)
    for i, question in enumerate(quick_questions):
        with cols[i % 3]:
            if st.button(question, key=f"quick_{i}"):
                st.session_state.messages.append({
                    "role": "user",
                    "content": question
                })
                
                with st.spinner("🤖 Réflexion en cours..."):
                    response = st.session_state.bot.process_message(
                        question, 
                        "streamlit_user"
                    )
                
                st.session_state.messages.append({
                    "role": "assistant",
                    "content": response
                })
                
                st.rerun()

def display_projects_showcase():
    """Afficher les projets en vedette"""
    st.markdown("### 🚀 Projets en Vedette")
    
    projects = [
        {
            "title": "🤖 Interactive Data Analysis Tool",
            "description": "Application web d'analyse exploratoire automatisée",
            "tech": "Streamlit, Pandas, Plotly",
            "link": "https://huggingface.co/spaces/Sidoineko/portfolio"
        },
        {
            "title": "🌾 AgriLens AI",
            "description": "Diagnostic maladies de plantes avec IA multimodale",
            "tech": "Gemma 3N, Computer Vision",
            "link": "Portfolio"
        },
        {
            "title": "💬 Chatbot CV",
            "description": "Système conversationnel intelligent (RAG + LLM)",
            "tech": "LangChain, RAG, LLM",
            "link": "Portfolio"
        }
    ]
    
    cols = st.columns(3)
    for i, project in enumerate(projects):
        with cols[i]:
            st.markdown(f"""
            <div class="project-card">
                <h4>{project['title']}</h4>
                <p>{project['description']}</p>
                <p><strong>Tech:</strong> {project['tech']}</p>
                <a href="{project['link']}" target="_blank">🔗 Voir la démo</a>
            </div>
            """, unsafe_allow_html=True)

def main():
    """Fonction principale"""
    # Initialisation
    initialize_bot()
    
    # Affichage des composants
    display_header()
    display_sidebar()
    
    # Onglets
    tab1, tab2, tab3 = st.tabs(["💬 Chat", "🎯 Questions Rapides", "🚀 Projets"])
    
    with tab1:
        display_chat_interface()
    
    with tab2:
        display_quick_questions()
    
    with tab3:
        display_projects_showcase()
    
    # Footer
    st.markdown("""
    ---
    <div style='text-align: center; color: #666;'>
        <p>🤖 Assistant Intelligent CCR-B / AgroEco IA Pro</p>
        <p>📧 syebadokpo@gmail.com | 🌐 https://huggingface.co/spaces/Sidoineko/portfolio</p>
    </div>
    """, unsafe_allow_html=True)

if __name__ == "__main__":
    main()
