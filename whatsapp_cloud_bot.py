"""
📱 Bot WhatsApp Cloud API (Meta) - Intégration RAG
Connecte votre bot à WhatsApp Business via l'API officielle de Meta
"""

import requests
import logging
import json
from datetime import datetime
from flask import Flask, request, jsonify
from bot_reply_policy import notify_bot_api_send
from bot_whatsapp_rag import WhatsAppRAGBot
import os
from dotenv import load_dotenv

load_dotenv()

# Configuration
app = Flask(__name__)
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# Variables Meta WhatsApp Cloud API
WHATSAPP_TOKEN = os.getenv('WHATSAPP_TOKEN', '')
PHONE_NUMBER_ID = os.getenv('PHONE_NUMBER_ID', '')
VERIFY_TOKEN = os.getenv('WEBHOOK_VERIFY_TOKEN', 'sidoine_bot_token_2025')

# Initialisation du bot RAG
bot = WhatsAppRAGBot()

def send_whatsapp_message(recipient_phone: str, message_text: str) -> bool:
    """Envoyer un message WhatsApp via la Cloud API Meta"""
    url = f"https://graph.facebook.com/v21.0/{PHONE_NUMBER_ID}/messages"
    
    headers = {
        "Authorization": f"Bearer {WHATSAPP_TOKEN}",
        "Content-Type": "application/json"
    }
    
    # Découper les messages longs (limite WhatsApp ~4096 chars)
    if len(message_text) > 4000:
        message_text = message_text[:3997] + "..."
    
    data = {
        "messaging_product": "whatsapp",
        "recipient_type": "individual",
        "to": recipient_phone,
        "type": "text",
        "text": {
            "preview_url": False,
            "body": message_text
        }
    }
    
    try:
        response = requests.post(url, headers=headers, json=data, timeout=30)
        
        if response.status_code == 200:
            notify_bot_api_send(recipient_phone)
            logger.info(f"✅ Message envoyé à {recipient_phone}")
            return True
        else:
            logger.error(f"❌ Erreur envoi: {response.status_code} - {response.text}")
            return False
            
    except Exception as e:
        logger.error(f"❌ Exception envoi: {e}")
        return False

def send_interactive_message(recipient_phone: str, body_text: str, buttons: list) -> bool:
    """Envoyer un message interactif avec boutons"""
    url = f"https://graph.facebook.com/v21.0/{PHONE_NUMBER_ID}/messages"
    
    headers = {
        "Authorization": f"Bearer {WHATSAPP_TOKEN}",
        "Content-Type": "application/json"
    }
    
    # Limiter à 3 boutons (limite WhatsApp)
    buttons = buttons[:3]
    
    action_buttons = []
    for i, btn in enumerate(buttons):
        action_buttons.append({
            "type": "reply",
            "reply": {
                "id": f"btn_{i}",
                "title": btn[:20]  # Max 20 caractères
            }
        })
    
    data = {
        "messaging_product": "whatsapp",
        "recipient_type": "individual",
        "to": recipient_phone,
        "type": "interactive",
        "interactive": {
            "type": "button",
            "body": {
                "text": body_text[:1024]  # Max 1024 caractères
            },
            "action": {
                "buttons": action_buttons
            }
        }
    }
    
    try:
        response = requests.post(url, headers=headers, json=data, timeout=30)
        return response.status_code == 200
    except Exception as e:
        logger.error(f"❌ Erreur boutons: {e}")
        return False

@app.route('/webhook', methods=['GET'])
def verify_webhook():
    """Vérification du webhook par Meta"""
    mode = request.args.get('hub.mode')
    token = request.args.get('hub.verify_token')
    challenge = request.args.get('hub.challenge')
    
    if mode == 'subscribe' and token == VERIFY_TOKEN:
        logger.info("✅ Webhook vérifié par Meta")
        return challenge, 200
    
    logger.warning("⚠️ Vérification webhook échouée")
    return jsonify({'error': 'Invalid verify token'}), 403

@app.route('/webhook', methods=['POST'])
def webhook():
    """Recevoir les messages WhatsApp via Cloud API"""
    try:
        data = request.get_json()
        
        # Vérifier que c'est un message WhatsApp
        if data.get('object') != 'whatsapp_business_account':
            return jsonify({'status': 'ignored'}), 200
        
        for entry in data.get('entry', []):
            for change in entry.get('changes', []):
                value = change.get('value', {})
                
                # Ignorer les statuts (livré, lu, etc.)
                if 'statuses' in value:
                    continue
                
                # Traiter les messages
                messages = value.get('messages', [])
                contacts = value.get('contacts', [])
                
                for message in messages:
                    # Extraire les infos
                    sender_phone = message.get('from', '')
                    message_type = message.get('type', '')
                    
                    # Nom du contact
                    sender_name = contacts[0]['wa_id'] if contacts else sender_phone
                    if contacts and 'profile' in contacts[0]:
                        sender_name = contacts[0]['profile'].get('name', sender_phone)
                    
                    # Extraire le texte du message
                    message_text = ''
                    
                    if message_type == 'text':
                        message_text = message.get('text', {}).get('body', '')
                    elif message_type == 'interactive':
                        interactive = message.get('interactive', {})
                        if interactive.get('type') == 'button_reply':
                            message_text = interactive.get('button_reply', {}).get('title', '')
                        elif interactive.get('type') == 'list_reply':
                            message_text = interactive.get('list_reply', {}).get('title', '')
                    elif message_type == 'audio':
                        # Pour l'audio, indiquer que ce n'est pas supporté
                        send_whatsapp_message(sender_phone, "🎤 Désolé, je ne traite pas encore les messages vocaux. Veuillez écrire votre question.")
                        continue
                    elif message_type == 'image':
                        caption = message.get('image', {}).get('caption', '')
                        if caption:
                            message_text = caption
                        else:
                            send_whatsapp_message(sender_phone, "🖼️ J'ai bien reçu votre image, mais je préfère les questions écrites !")
                            continue
                    
                    if not message_text:
                        continue
                    
                    # Marquer le message comme lu
                    message_id = message.get('id', '')
                    if message_id:
                        mark_as_read(message_id)
                    
                    # Traiter avec le bot RAG
                    logger.info(f"📨 Message de {sender_name} ({sender_phone}): {message_text[:50]}...")
                    
                    response = bot.process_message(message_text, sender_phone)
                    
                    # Envoyer la réponse
                    send_whatsapp_message(sender_phone, response)
        
        return jsonify({'status': 'success'}), 200
        
    except Exception as e:
        logger.error(f"❌ Erreur webhook: {e}")
        return jsonify({'status': 'error'}), 200

def mark_as_read(message_id: str):
    """Marquer un message comme lu"""
    url = f"https://graph.facebook.com/v21.0/{PHONE_NUMBER_ID}/messages"
    
    headers = {
        "Authorization": f"Bearer {WHATSAPP_TOKEN}",
        "Content-Type": "application/json"
    }
    
    data = {
        "messaging_product": "whatsapp",
        "status": "read",
        "message_id": message_id
    }
    
    try:
        requests.post(url, headers=headers, json=data, timeout=10)
    except:
        pass

@app.route('/health', methods=['GET'])
def health_check():
    """Vérification de santé"""
    return jsonify({
        'status': 'healthy',
        'bot': 'active' if bot.collection else 'no_chromadb',
        'whatsapp': 'configured' if WHATSAPP_TOKEN else 'not_configured',
        'documents': bot.collection.count() if bot.collection else 0,
        'timestamp': datetime.now().isoformat()
    })

@app.route('/test', methods=['POST'])
def test_bot():
    """Tester le bot localement"""
    data = request.get_json()
    message = data.get('message', '')
    phone = data.get('phone', 'test_user')
    
    if not message:
        return jsonify({'error': 'Message requis'}), 400
    
    response = bot.process_message(message, phone)
    
    return jsonify({
        'message': message,
        'response': response,
        'timestamp': datetime.now().isoformat()
    })

if __name__ == '__main__':
    if not WHATSAPP_TOKEN:
        print("⚠️ WHATSAPP_TOKEN non configuré dans .env")
        print("📋 Étapes de configuration:")
        print("1. Allez sur https://developers.facebook.com")
        print("2. Créez une App Business")
        print("3. Ajoutez le produit WhatsApp")
        print("4. Copiez le Token et Phone Number ID dans .env")
    else:
        print(f"🚀 Bot WhatsApp Cloud API démarré")
        print(f"📱 Phone Number ID: {PHONE_NUMBER_ID}")
        print(f"📚 Documents ChromaDB: {bot.collection.count() if bot.collection else 0}")
    
    port = int(os.getenv('PORT', 5000))
    app.run(host='0.0.0.0', port=port, debug=True)
