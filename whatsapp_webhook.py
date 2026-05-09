"""
📱 Webhook WhatsApp pour le Bot RAG
Reçoit les messages WhatsApp et traite les réponses
"""

from flask import Flask, request, jsonify
import json
import logging
from datetime import datetime
import os
from bot_whatsapp_rag import WhatsAppRAGBot

# Configuration
app = Flask(__name__)

# Configuration du logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Initialisation du bot
bot = WhatsAppRAGBot()

# Token de vérification (à configurer)
WEBHOOK_VERIFY_TOKEN = os.getenv('WEBHOOK_VERIFY_TOKEN', 'sidoine_bot_token_2025')

@app.route('/webhook', methods=['GET'])
def verify_webhook():
    """Vérification du webhook WhatsApp"""
    mode = request.args.get('hub.mode')
    token = request.args.get('hub.verify_token')
    challenge = request.args.get('hub.challenge')
    
    if mode and token:
        if mode == 'subscribe' and token == WEBHOOK_VERIFY_TOKEN:
            logger.info("✅ Webhook vérifié avec succès")
            return challenge, 200
        else:
            logger.warning(f"⚠️ Token de vérification invalide: {token}")
            return jsonify({'status': 'error', 'message': 'Verification token mismatch'}), 403
    
    return jsonify({'status': 'error', 'message': 'Missing parameters'}), 400

@app.route('/webhook', methods=['POST'])
def webhook():
    """Recevoir les messages WhatsApp"""
    try:
        data = request.get_json()
        logger.info(f"📨 Message reçu: {json.dumps(data, indent=2)}")
        
        # Extraire le message et les informations
        message_data = extract_message_data(data)
        
        if message_data:
            # Traiter le message
            response = bot.process_message(
                message_data['message'], 
                message_data['user_id']
            )
            
            # Envoyer la réponse
            success = bot.send_whatsapp_message(
                message_data['phone_number'],
                response
            )
            
            if success:
                logger.info(f"✅ Réponse envoyée à {message_data['phone_number']}")
            else:
                logger.error(f"❌ Échec envoi réponse à {message_data['phone_number']}")
            
            return jsonify({'status': 'success', 'message': 'Response sent'}), 200
        
        return jsonify({'status': 'ignored', 'message': 'No message to process'}), 200
        
    except Exception as e:
        logger.error(f"❌ Erreur traitement webhook: {e}")
        return jsonify({'status': 'error', 'message': str(e)}), 500

def extract_message_data(data):
    """Extraire les données du message WhatsApp"""
    try:
        # Structure pour Evolution API
        if 'key' in data and 'message' in data:
            return {
                'user_id': data['key']['remoteJid'],
                'phone_number': data['key']['remoteJid'].split('@')[0],
                'message': data['message']['conversation'] if 'conversation' in data['message'] else 
                          data['message']['extendedTextMessage']['text'] if 'extendedTextMessage' in data['message'] else
                          data['message'].get('imageMessage', {}).get('caption', ''),
                'timestamp': data['messageTimestamp'],
                'message_type': 'text'
            }
        
        # Structure pour WhatsApp Cloud API
        elif 'entry' in data:
            entry = data['entry'][0]
            changes = entry['changes'][0]
            
            if 'messages' in changes['value']:
                message_data = changes['value']['messages'][0]
                
                return {
                    'user_id': message_data['from'],
                    'phone_number': message_data['from'].split('@')[0],
                    'message': message_data['text']['body'] if 'text' in message_data else '',
                    'timestamp': message_data['timestamp'],
                    'message_type': message_data['type']
                }
        
        return None
        
    except Exception as e:
        logger.error(f"❌ Erreur extraction données: {e}")
        return None

@app.route('/health', methods=['GET'])
def health_check():
    """Vérification de santé du service"""
    return jsonify({
        'status': 'healthy',
        'timestamp': datetime.now().isoformat(),
        'bot_status': 'active' if bot.collection else 'no_chromadb',
        'version': '1.0.0'
    })

@app.route('/stats', methods=['GET'])
def get_stats():
    """Obtenir les statistiques du bot"""
    try:
        stats = {
            'bot_info': {
                'name': 'Assistant CCR-B / AgroEco IA Pro',
                'owner': 'Sidoine Kolaolé YEBADOKPO',
                'version': '1.0.0'
            },
            'chromadb': {
                'connected': bot.collection is not None,
                'documents': bot.collection.count() if bot.collection else 0,
                'collection': 'ccrb_knowledge_base'
            },
            'conversations': {
                'active_users': len(bot.conversation_history),
                'total_messages': sum(len(msgs) for msgs in bot.conversation_history.values())
            },
            'timestamp': datetime.now().isoformat()
        }
        
        return jsonify(stats), 200
        
    except Exception as e:
        logger.error(f"❌ Erreur statistiques: {e}")
        return jsonify({'error': str(e)}), 500

@app.route('/test', methods=['POST'])
def test_bot():
    """Tester le bot avec un message"""
    try:
        data = request.get_json()
        message = data.get('message', 'Test message')
        user_id = data.get('user_id', 'test_user')
        
        response = bot.process_message(message, user_id)
        
        return jsonify({
            'user_message': message,
            'bot_response': response,
            'timestamp': datetime.now().isoformat()
        }), 200
        
    except Exception as e:
        logger.error(f"❌ Erreur test: {e}")
        return jsonify({'error': str(e)}), 500

if __name__ == '__main__':
    logger.info("🚀 Démarrage du webhook WhatsApp Bot RAG")
    logger.info(f"📊 Collection ChromaDB: {bot.collection.name if bot.collection else 'Non connectée'}")
    
    # Démarrage du serveur
    port = int(os.getenv('PORT', 5000))
    app.run(host='0.0.0.0', port=port, debug=True)
