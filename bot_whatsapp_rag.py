"""
🤖 Bot WhatsApp avec RAG pour Sidoine YEBADOKPO
Assistant Intelligent CCR-B / AgroEco IA Pro
"""

import chromadb
import html
import os
import json
import asyncio
import logging
from datetime import datetime
from typing import List, Dict, Any
import requests
from dotenv import load_dotenv

# Configuration du logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


def normalize_whatsapp_outgoing(text: str) -> str:
    """Évite l'affichage littéral de &#039; / &amp; si la passerelle applique html.escape sur le texte."""
    if not text:
        return text
    t = html.unescape(text)
    return t.replace("'", "\u2019")


class WhatsAppRAGBot:
    def __init__(self):
        """Initialisation du bot WhatsApp avec RAG"""
        load_dotenv()
        
        # Configuration ChromaDB
        self.chroma_client = None
        self.collection = None
        
        # Configuration WhatsApp (Evolution API)
        self.whatsapp_api_url = os.getenv('WHATSAPP_API_URL', 'https://api.evolution-api.com')
        self.whatsapp_token = os.getenv('WHATSAPP_TOKEN')
        self.instance_id = os.getenv('WHATSAPP_INSTANCE_ID')
        
        # Configuration LLM
        self.llm_api_key = os.getenv('OPENAI_API_KEY') or os.getenv('GEMINI_API_KEY')
        self.llm_model = os.getenv('LLM_MODEL', 'gpt-3.5-turbo')
        
        # Informations du propriétaire
        self.owner_info = {
            "name": "Sidoine Kolaolé YEBADOKPO",
            "title": "Data Analyst & Web Developer Fullstack",
            "email": "syebadokpo@gmail.com",
            "phone": "+229 01 96 91 13 46",
            "location": "Cotonou, Bénin",
            "portfolio": "https://huggingface.co/spaces/Sidoineko/portfolio"
        }
        
        # Historique de conversation
        self.conversation_history = {}
        
        # Initialisation
        self.init_chromadb()
        
    def init_chromadb(self):
        """Initialisation de la connexion ChromaDB"""
        try:
            self.chroma_client = chromadb.CloudClient(
                api_key='REMOVED_API_KEY',
                tenant='0dc087aa-1492-4485-b346-35546f1fa1ac',
                database='sido'
            )
            
            self.collection = self.chroma_client.get_collection("ccrb_knowledge_base")
            logger.info("✅ Connexion ChromaDB établie")
            
        except Exception as e:
            logger.error(f"❌ Erreur connexion ChromaDB: {e}")
            self.collection = None
    
    def search_knowledge_base(self, query: str, n_results: int = 3) -> List[Dict]:
        """Recherche dans la base de connaissances"""
        if not self.collection:
            return []
        
        try:
            results = self.collection.query(
                query_texts=[query],
                n_results=n_results
            )
            
            # Formater les résultats
            formatted_results = []
            for i, (doc, distance, metadata) in enumerate(zip(
                results['documents'][0], 
                results['distances'][0],
                results['metadatas'][0] if results['metadatas'] else [{}] * len(results['documents'][0])
            )):
                formatted_results.append({
                    'content': doc,
                    'score': 1 - distance,
                    'metadata': metadata,
                    'rank': i + 1
                })
            
            return formatted_results
            
        except Exception as e:
            logger.error(f"❌ Erreur recherche: {e}")
            return []
    
    def generate_llm_response(self, query: str, context: List[Dict], user_id: str = None) -> str:
        """Générer une réponse avec le LLM en utilisant le contexte RAG"""
        
        # Préparer le contexte
        context_text = "\n\n".join([
            f"[Source {result['rank']} - Score: {result['score']:.3f}]\n{result['content']}"
            for result in context
        ])
        
        # Historique avant le message courant (rempli dans process_message après génération)
        history = self.conversation_history.get(user_id, [])
        history_text = "\n".join(
            [f"{msg['role']}: {msg['content']}" for msg in history[-10:]]
        )
        
        # Prompt système basé sur le document d'entraînement
        system_prompt = f"""
Tu es l'Assistant Intelligent CCR-B / AgroEco IA Pro, un assistant spécialisé pour Sidoine Kolaolé YEBADOKPO.

PROFIL DU PROPRIÉTAIRE:
- Nom: {self.owner_info['name']}
- Titre: {self.owner_info['title']}
- Email: {self.owner_info['email']}
- Téléphone: {self.owner_info['phone']}
- Localisation: {self.owner_info['location']}
- Portfolio: {self.owner_info['portfolio']}

EXPERTISE PRINCIPALE:
- Agroécologie et filière riz au Bénin
- Suivi-évaluation de projets (MEAL)
- Data Science et analyse de données
- Développement d'applications IA et web
- Automatisation et digitalisation

STYLE DE RÉPONSE:
- Professionnel, clair, structuré, pédagogique
- Basé sur les données et faits disponibles
- Structure: Contexte → Analyse → Résultats → Recommandations
- Langue: Français principal, peut traduire si nécessaire

RÈGLES IMPORTANTES:
- Utiliser uniquement les informations du contexte fourni
- Ne pas inventer d'informations non présentes dans le contexte
- Si l'information n'est pas disponible, l'indiquer clairement
- Maintenir un ton professionnel et bienveillant
- Prioriser l'impact terrain et la durabilité

CONTEXTE DISPONIBLE:
{context_text}

HISTORIQUE RÉCENT:
{history_text}

QUESTION UTILISATEUR:
{query}

Réponds de manière structurée et professionnelle en utilisant les informations disponibles.
"""
        
        try:
            # Simulation de réponse LLM (remplacer par vrai appel API)
            response = self._simulate_llm_response(query, context, system_prompt, user_id)
            return response
            
        except Exception as e:
            logger.error(f"❌ Erreur génération LLM: {e}")
            return "Désolé, je rencontre une difficulté technique. Veuillez réessayer ultérieurement."
    
    def _is_greeting_query(self, query: str) -> bool:
        query_lower = query.lower().strip()
        greetings = ['bonjour', 'salut', 'hello', 'hi', 'hey', 'coucou', 'bonsoir', 'yo', 'bjr', 'slt']
        return query_lower in greetings or (
            len(query_lower) < 12 and any(g in query_lower for g in greetings)
        )
    
    def _is_thanks_query(self, query: str) -> bool:
        query_lower = query.lower().strip()
        thanks = ['merci', 'thank', 'au revoir', 'bye', 'ciao', 'bonne journée']
        return any(t in query_lower for t in thanks)
    
    def _has_prior_exchange(self, user_id: str) -> bool:
        if not user_id:
            return False
        return any(m.get('role') == 'assistant' for m in self.conversation_history.get(user_id, []))
    
    def _last_substantive_user_message(self, user_id: str) -> str:
        """Dernier message utilisateur utile (hors simples salutations)."""
        if not user_id:
            return ""
        hist = self.conversation_history.get(user_id, [])
        greetings = {'bonjour', 'salut', 'hello', 'hi', 'hey', 'coucou', 'bonsoir', 'yo', 'bjr', 'slt'}
        for msg in reversed(hist):
            if msg.get('role') != 'user':
                continue
            t = (msg.get('content') or '').strip()
            tl = t.lower()
            if len(t) < 5:
                continue
            if tl in greetings:
                continue
            if len(t) < 14 and any(g in tl for g in greetings) and sum(c.isalpha() for c in t) < 10:
                continue
            return t
        return ""
    
    def _build_courteous_greeting(self, user_id: str = None) -> str:
        name = self.owner_info['name']
        prior_assistant_count = sum(
            1 for m in self.conversation_history.get(user_id, [])
            if m.get('role') == 'assistant'
        )
        if prior_assistant_count == 0:
            return (
                f"Bonjour,\n\n"
                f"Merci pour votre message. Je suis l\u2019assistant de **{name}** ; "
                f"je réponds avec attention lorsqu\u2019il n\u2019est pas disponible.\n\n"
                f"Indiquez simplement ce dont vous avez besoin — parcours, compétences, projets, "
                f"coordonnées ou sujets agroécologie / données — et j\u2019y répondrai volontiers."
            )
        last_topic = self._last_substantive_user_message(user_id)
        if last_topic:
            short = last_topic[:140] + ("…" if len(last_topic) > 140 else "")
            return (
                f"Bonjour,\n\n"
                f"Je suis heureux de vous retrouver. Nous avions notamment évoqué : « {short} ».\n\n"
                f"Souhaitez-vous approfondir ce point ou aborder un autre sujet au sujet de **{name}** ? "
                f"Je reste à votre disposition."
            )
        return (
            f"Bonjour,\n\n"
            f"Ravi de vous lire à nouveau. Que puis-je préciser pour vous aujourd\u2019hui "
            f"au sujet de **{name}** ?"
        )
    
    def _build_thanks_response(self, user_id: str = None) -> str:
        if user_id and self._has_prior_exchange(user_id):
            return (
                "Je vous en prie. Ce fut un plaisir d\u2019échanger avec vous.\n\n"
                "Revenez quand vous voulez — je me souviendrai de notre conversation pour rester cohérent."
            )
        return (
            "Je vous en prie. N\u2019hésitez pas à revenir si vous avez d\u2019autres questions. "
            "Excellente journée !"
        )
    
    def _continuity_intro(self, user_id: str = None) -> str:
        if not user_id or not self._has_prior_exchange(user_id):
            return ""
        topic = self._last_substantive_user_message(user_id)
        if topic and len(topic) > 12:
            snippet = topic[:90] + ("…" if len(topic) > 90 else "")
            return f"📎 En lien avec « {snippet} », voici des précisions :\n\n"
        return "📎 Pour compléter notre échange :\n\n"
    
    def _prepend_continuity(self, user_id: str, body: str) -> str:
        intro = self._continuity_intro(user_id)
        return intro + body if intro else body
    
    def _simulate_llm_response(
        self, query: str, context: List[Dict], system_prompt: str, user_id: str = None
    ) -> str:
        """Simulation de réponse LLM (remplacer par vrai appel API)"""
        
        query_lower = query.lower().strip()
        
        if self._is_greeting_query(query):
            return self._build_courteous_greeting(user_id)
        
        if self._is_thanks_query(query):
            return self._build_thanks_response(user_id)
        
        # Pas de contexte trouvé
        if not context:
            msg = (
                f"Je n\u2019ai pas trouvé d\u2019information précise pour cette formulation dans la base. "
                f"Je suis l\u2019assistant de **{self.owner_info['name']}** (Data Science, agroécologie, MEAL).\n\n"
                f"Reformulez en une phrase, ou essayez des mots-clés : compétences, projets, parcours, contact. "
                f"Si c\u2019est la suite de notre échange, un petit rappel du sujet m\u2019aide à rester cohérent."
            )
            return self._prepend_continuity(user_id, msg)
        
        # Analyse basée sur le contexte
        if any(
            keyword in query_lower
            for keyword in [
                'compétence', 'competence', 'compétences', 'competences',
                'skill', 'expertise', 'maîtrise', 'maitrise', 'outils', 'technologie'
            ]
        ):
            return self._prepend_continuity(user_id, self._format_skills_response(context))
        
        elif any(keyword in query_lower for keyword in ['projet', 'project', 'réalisation', 'achievement', 'app', 'application']):
            return self._prepend_continuity(user_id, self._format_projects_response(context))
        
        elif any(keyword in query_lower for keyword in ['expérience', 'experience', 'parcours', 'carrière', 'travail', 'emploi']):
            return self._prepend_continuity(user_id, self._format_experience_response(context))
        
        elif any(keyword in query_lower for keyword in ['contact', 'coordonnées', 'email', 'téléphone', 'joindre']):
            return self._prepend_continuity(user_id, self._format_contact_response())
        
        elif any(keyword in query_lower for keyword in ['formation', 'diplôme', 'certificat', 'étude', 'académique']):
            return self._prepend_continuity(user_id, self._format_formation_response(context))
        
        elif any(keyword in query_lower for keyword in ['agroécolog', 'riz', 'agricult', 'srp', 'compost', 'vermicompost']):
            return self._prepend_continuity(user_id, self._format_agroecologie_response(context))
        
        else:
            return self._format_general_response(query, context, user_id)
    
    def _format_skills_response(self, context: List[Dict]) -> str:
        """Formater la réponse sur les compétences"""
        response = "🔧 **Compétences Techniques de Sidoine YEBADOKPO**\n\n"
        
        # Extraire les compétences du contexte
        skills_found = []
        for result in context:
            content = result['content'].lower()
            if 'python' in content:
                skills_found.append("🐍 **Python**: Pandas, NumPy, Scikit-learn, Streamlit, LangChain")
            if 'r' in content and 'tidyverse' in content:
                skills_found.append("📊 **R**: tidyverse, ggplot2, dplyr, R Markdown")
            if 'sql' in content:
                skills_found.append("🗄️ **SQL**: PostgreSQL, MySQL, SQLAlchemy")
            if 'power bi' in content:
                skills_found.append("📈 **Power BI et Tableau**: Tableaux de bord interactifs")
            if 'api' in content:
                skills_found.append("🔌 **APIs**: World Bank, FAO, UNDP, REST APIs")
        
        if skills_found:
            response += "\n".join(skills_found)
        else:
            response += "Consultez son portfolio pour la liste complète des compétences."
        
        response += f"\n\n📱 **Portfolio**: {self.owner_info['portfolio']}"
        return response
    
    def _format_projects_response(self, context: List[Dict]) -> str:
        """Formater la réponse sur les projets"""
        response = "🚀 **Principaux Projets Réalisés**\n\n"
        
        projects = [
            "🤖 **Interactive Data Analysis Tool** - Analyse exploratoire automatisée (Streamlit)",
            "🌾 **AgriLens AI** - Diagnostic maladies de plantes (IA multimodale)",
            "💬 **Chatbot CV** - Système conversationnel (RAG + LLM)",
            "📱 **Presence CCRB** - App full-stack de suivi GPS terrain",
            "📚 **Biblio IA / CoranIA** - Systèmes Q&A sémantiques",
            "🌐 **Portfolio interactif** - Site web avec chatbot intégré"
        ]
        
        response += "\n".join(projects)
        response += f"\n\n🔗 **Démonstrations disponibles**: {self.owner_info['portfolio']}"
        
        return response
    
    def _format_experience_response(self, context: List[Dict]) -> str:
        """Formater la réponse sur l'expérience"""
        response = "💼 **Parcours Professionnel**\n\n"
        
        experience = [
            "🏢 **Conseiller Global MEAL** - CCR-Bénin (Juin 2022 – présent)",
            "  • Conception pipelines de données end-to-end",
            "  • Analyse de données complexes (Python, R)",
            "  • Développement tableaux de bord (Power BI, Tableau)",
            "",
            "🔍 **Consultant Gestionnaire de Données** - GAI SARL (Sept 2024 – Déc 2024)",
            "  • Développement applications de collecte",
            "  • Formation agents d'enquête",
            "",
            "🌳 **Expert Junior Aménagement Forestier** - GAI SARL (Nov 2020 – Juin 2021)",
            "  • Collecte et analyse données terrain",
            "  • Élaboration PAGS et cartographie QGIS"
        ]
        
        response += "\n".join(experience)
        return response
    
    def _format_contact_response(self) -> str:
        """Formater la réponse de contact"""
        return f"""📞 **Coordonnées de Sidoine YEBADOKPO**

📧 **Email**: {self.owner_info['email']}
📱 **Téléphone**: {self.owner_info['phone']}
📍 **Localisation**: {self.owner_info['location']}
🌐 **Portfolio**: {self.owner_info['portfolio']}

N'hésitez pas à le contacter pour vos projets en Data Science, Agroécologie ou Développement IA !"""
    
    def _format_formation_response(self, context: List[Dict]) -> str:
        """Formater la réponse sur la formation"""
        response = "🎓 **Formation et certifications de Sidoine YEBADOKPO**\n\n"
        
        formations = [
            "🎓 **MBA Data Science Management** - Tech Institute (2024-2026, en cours)",
            "🌲 **Master 2 Sciences Forestières** - UNA Kétou (2022-2024)",
            "🌾 **Licence en Agronomie** - UNA Kétou (2009-2013)",
            "🇬🇧 **Licence en Anglais** - UAC Adjarra (2011-2014)",
            "",
            "📜 **Certifications:**",
            "• Data Analytics Job Simulation - Deloitte Australia (2025)",
            "• Data Scientist Associate - DataCamp (2024)",
            "• PCAP: Programming Essentials in Python - Cisco (2022)",
            "• Fundamentals of Data Science - Google/Coursera (2023)",
            "• Data Visualization with Excel et Cognos - IBM (2022)"
        ]
        
        response += "\n".join(formations)
        return response
    
    def _format_agroecologie_response(self, context: List[Dict]) -> str:
        """Formater la réponse sur l'agroécologie"""
        response = "🌱 **Expertise Agroécologie et Filière Riz**\n\n"
        
        response += """**Agroécologie:**
• Agriculture durable, compostage, vermicompost
• Thé de vermicompost, biofertilisants
• Gestion durable des sols, agriculture climato-intelligente
• Réduction des GES, résilience climatique
• Pratiques SRP (Sustainable Rice Platform)

**Filière Riz:**
• Systèmes de production, étapes culturales
• Chaînes de valeur, pratiques SRP
• Émissions de GES en riziculture
• Rendements, marges économiques, diagnostics PDA

**Projets CCR-B:**
• PARSAD: Transition agroécologique
• DEFIA: Développement des Filières Agricoles
• Delta Mono, PAAPEF, AP-OSP, TAERA"""
        
        return response
    
    def _format_general_response(self, query: str, context: List[Dict], user_id: str = None) -> str:
        """Formater une réponse générale"""
        if context:
            best_result = context[0]
            content = best_result['content']
            lines = content.split('\n')
            relevant_lines = [l for l in lines if l.strip() and not l.startswith('---')][:8]
            response = f"📋 **Éléments utiles pour votre question :**\n\n" + "\n".join(relevant_lines)
            response += f"\n\n💡 Dites-moi si vous voulez creuser un aspect précis — je m\u2019appuie aussi sur notre fil de discussion."
        else:
            response = f"""Voici ce sur quoi je peux vous orienter au sujet de **{self.owner_info['name']}** :

📊 Data Science et analyse de données
🌱 Agroécologie et filière riz
📈 Suivi-évaluation (MEAL)
🤖 Développement d\u2019applications IA
🔧 Automatisation et digitalisation

Posez votre question en une phrase : j\u2019utiliserai le contexte de nos échanges quand c\u2019est pertinent."""
        
        return self._prepend_continuity(user_id, response)
    
    def process_message(self, message: str, user_id: str = None) -> str:
        """Traiter un message entrant"""
        try:
            if user_id not in self.conversation_history:
                self.conversation_history[user_id] = []
            
            # Recherche et génération avant d'enregistrer le tour courant
            # → l'historique lu par le modèle ne contient que les échanges *passés*
            context = self.search_knowledge_base(message)
            response = normalize_whatsapp_outgoing(
                self.generate_llm_response(message, context, user_id)
            )
            
            self.conversation_history[user_id].append({
                'role': 'user',
                'content': message,
                'timestamp': datetime.now().isoformat()
            })
            self.conversation_history[user_id].append({
                'role': 'assistant',
                'content': response,
                'timestamp': datetime.now().isoformat()
            })
            
            # Limiter l'historique
            if len(self.conversation_history[user_id]) > 20:
                self.conversation_history[user_id] = self.conversation_history[user_id][-20:]
            
            return response
            
        except Exception as e:
            logger.error(f"❌ Erreur traitement message: {e}")
            return normalize_whatsapp_outgoing(
                "Désolé, une erreur est survenue. Veuillez réessayer."
            )
    
    def send_whatsapp_message(self, phone_number: str, message: str):
        """Envoyer un message via WhatsApp Evolution API"""
        if not self.whatsapp_token:
            logger.warning("⚠️ Token WhatsApp non configuré")
            return False
        
        try:
            url = f"{self.whatsapp_api_url}/message/sendText/{self.instance_id}"
            
            payload = {
                "number": phone_number,
                "text": message
            }
            
            headers = {
                "Content-Type": "application/json",
                "apikey": self.whatsapp_token
            }
            
            response = requests.post(url, json=payload, headers=headers)
            
            if response.status_code == 200:
                logger.info(f"✅ Message envoyé à {phone_number}")
                return True
            else:
                logger.error(f"❌ Erreur envoi message: {response.status_code}")
                return False
                
        except Exception as e:
            logger.error(f"❌ Erreur envoi WhatsApp: {e}")
            return False

# Point d'entrée principal
if __name__ == "__main__":
    # Test du bot
    bot = WhatsAppRAGBot()
    
    # Messages de test
    test_messages = [
        "Quelles sont les compétences de Sidoine ?",
        "Quels projets a-t-il réalisés ?",
        "Quel est son parcours professionnel ?",
        "Comment puis-je le contacter ?"
    ]
    
    print("🤖 Test du Bot WhatsApp RAG\n")
    
    for msg in test_messages:
        print(f"👤 Utilisateur: {msg}")
        response = bot.process_message(msg, "test_user")
        print(f"🤖 Bot: {response}")
        print("-" * 50)
