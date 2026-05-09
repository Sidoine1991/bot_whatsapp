"""
📱 Bot WhatsApp Personnel - Connexion directe à votre compte
Utilise une API simple pour connecter votre numéro WhatsApp personnel
"""

import requests
import json
import time
import logging
import os
from flask import Flask, request, jsonify
from bot_whatsapp_rag import WhatsAppRAGBot, normalize_whatsapp_outgoing
from bot_reply_policy import record_owner_outgoing, should_auto_reply_inbound
from dotenv import load_dotenv

load_dotenv()

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

app = Flask(__name__)

# Bot RAG
bot = WhatsAppRAGBot()

# Configuration API WhatsApp (utilise un service tiers simple)
WHATSAPP_API_URL = "https://api.ultramsg.com/instance13333/messages"
WHATSAPP_TOKEN = os.getenv('WHATSAPP_TOKEN', '')

def send_whatsapp_message(phone: str, message: str) -> bool:
    """Envoyer un message via API WhatsApp"""
    try:
        # Formater le numéro (ajouter le code pays si nécessaire)
        if not phone.startswith('+'):
            if phone.startswith('229'):  # Bénin
                phone = '+' + phone
            else:
                phone = '+229' + phone
        
        data = {
            "token": WHATSAPP_TOKEN,
            "to": phone,
            "body": message
        }
        
        response = requests.post(WHATSAPP_API_URL, json=data, timeout=30)
        
        if response.status_code == 200:
            logger.info(f"✅ Message envoyé à {phone}")
            return True
        else:
            logger.error(f"❌ Erreur envoi: {response.text}")
            return False
            
    except Exception as e:
        logger.error(f"❌ Exception envoi: {e}")
        return False

def process_whatsapp_message(from_phone: str, message: str) -> str:
    """Traiter un message WhatsApp et générer une réponse"""
    try:
        # Traiter avec le bot RAG
        response = bot.process_message(message, from_phone)
        
        logger.info(f"📨 Message de {from_phone}: {message[:50]}...")
        logger.info(f"✅ Réponse générée: {response[:100]}...")
        
        return response
        
    except Exception as e:
        logger.error(f"❌ Erreur traitement: {e}")
        return normalize_whatsapp_outgoing(
            "Désolé, je rencontre une difficulté technique. Veuillez réessayer ultérieurement."
        )

def _ultramsg_payload(data: dict):
    """Support format plat ou data.data (UltraMSG)."""
    inner = data.get("data") if isinstance(data.get("data"), dict) else data
    from_phone = inner.get("from", data.get("from", "")) or ""
    message_text = inner.get("body", data.get("body", "")) or ""
    raw_from_me = inner.get("fromMe", data.get("fromMe", False))
    if isinstance(raw_from_me, str):
        from_me = raw_from_me.strip().lower() in ("true", "1", "yes")
    else:
        from_me = bool(raw_from_me)
    # Message sortant : le contact est souvent dans "to"
    peer_for_outgoing = inner.get("to", data.get("to", "")) or from_phone
    return inner, from_phone, message_text, from_me, peer_for_outgoing


@app.route('/webhook', methods=['POST'])
def webhook():
    """Webhook pour recevoir les messages WhatsApp"""
    try:
        data = request.get_json()
        logger.info(f"📨 Webhook reçu: {data}")
        
        _, from_phone, message_text, from_me, peer_for_outgoing = _ultramsg_payload(data or {})
        
        if from_me:
            record_owner_outgoing(peer_for_outgoing)
            return jsonify({'status': 'ignored', 'reason': 'fromMe'}), 200
        
        if message_text and from_phone:
            allow, skip_reason = should_auto_reply_inbound(from_phone)
            if not allow:
                logger.info(f"⏸️ Pas de réponse auto: {skip_reason}")
                return jsonify({'status': 'skipped', 'reason': skip_reason}), 200
            
            logger.info(f"📨 Message de {from_phone}: {message_text}")
            response = process_whatsapp_message(from_phone, message_text)
            send_whatsapp_message(from_phone, response)
        
        return jsonify({'status': 'ok'}), 200
        
    except Exception as e:
        logger.error(f"❌ Erreur webhook: {e}")
        return jsonify({'status': 'error'}), 200

@app.route('/test', methods=['POST'])
def test_bot():
    """Tester le bot localement"""
    data = request.get_json()
    message = data.get('message', '')
    phone = data.get('phone', 'test_user')
    
    if not message:
        return jsonify({'error': 'Message requis'}), 400
    
    response = process_whatsapp_message(phone, message)
    
    return jsonify({
        'message': message,
        'response': response,
        'phone': phone
    })

@app.route('/health', methods=['GET'])
def health_check():
    """Vérification de santé"""
    return jsonify({
        'status': 'healthy',
        'bot': 'active' if bot.collection else 'no_chromadb',
        'documents': bot.collection.count() if bot.collection else 0,
        'whatsapp': 'configured' if WHATSAPP_TOKEN else 'not_configured'
    })

@app.route('/setup', methods=['GET'])
def setup_guide():
    """Guide de configuration"""
    return jsonify({
        'title': 'Configuration Bot WhatsApp Personnel',
        'steps': [
            {
                'step': 1,
                'title': 'Créer un compte UltraMSG',
                'description': 'Allez sur https://ultramsg.com et créez un compte gratuit',
                'url': 'https://ultramsg.com'
            },
            {
                'step': 2,
                'title': 'Créer une instance',
                'description': 'Dans le dashboard, créez une nouvelle instance WhatsApp',
                'note': 'Notez votre instance ID'
            },
            {
                'step': 3,
                'title': 'Scanner le QR code',
                'description': 'Scannez le QR code avec votre WhatsApp personnel',
                'note': 'Votre WhatsApp sera connecté à l\'API'
            },
            {
                'step': 4,
                'title': 'Obtenir le token',
                'description': 'Copiez le token de votre instance',
                'note': 'Ajoutez-le au fichier .env: WHATSAPP_TOKEN=votre_token'
            },
            {
                'step': 5,
                'title': 'Démarrer le bot',
                'description': 'Lancez: py -3.14 whatsapp_personal_bot.py',
                'note': 'Le bot répondra automatiquement aux messages'
            }
        ],
        'webhook_info': {
            'url': 'https://votre-domaine.com/webhook',
            'note': 'Configurez cette URL dans UltraMSG pour recevoir les messages'
        }
    })

if __name__ == '__main__':
    print("=" * 60)
    print("📱 Bot WhatsApp Personnel - Assistant RAG")
    print("=" * 60)
    print(f"📚 Documents ChromaDB: {bot.collection.count() if bot.collection else 0}")
    print(f"🔗 Webhook: http://localhost:5000/webhook")
    print(f"🧪 Test: http://localhost:5000/test")
    print(f"📋 Guide: http://localhost:5000/setup")
    
    if not WHATSAPP_TOKEN:
        print("\n⚠️ WHATSAPP_TOKEN non configuré")
        print("📋 Suivez les étapes sur http://localhost:5000/setup")
    
    print(
        "💡 Prise en main : BOT_OWNER_HANDOFF_HOURS=24 par défaut (bot silencieux sur le contact "
        "où vous avez répondu). Désactiver : BOT_OWNER_HANDOFF_HOURS=0"
    )
    
    print("=" * 60)
    
    port = int(os.getenv('PORT', 5000))
    app.run(host='0.0.0.0', port=port, debug=True)
