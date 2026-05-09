"""
📱 Serveur Webhook pour Evolution API
Reçoit les messages WhatsApp et répond avec le Bot RAG
"""

from flask import Flask, request, jsonify
import logging
import os
from datetime import datetime
from bot_whatsapp_rag import WhatsAppRAGBot
from evolution_api_setup import send_message, check_connection
from dotenv import load_dotenv

load_dotenv()

app = Flask(__name__)
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# Bot RAG
bot = WhatsAppRAGBot()

@app.route('/evolution-webhook', methods=['POST'])
def evolution_webhook():
    """Recevoir les messages WhatsApp via Evolution API"""
    try:
        data = request.get_json()
        
        # Événement de connexion
        if data.get('event') == 'connection.update':
            state = data.get('data', {}).get('state', '')
            if state == 'CONNECTED':
                logger.info("✅ WhatsApp connecté")
            elif state == 'DISCONNECTED':
                logger.warning("⚠️ WhatsApp déconnecté")
            return jsonify({'status': 'ok'}), 200
        
        # Message entrant
        if data.get('event') == 'messages.upsert':
            message_data = data.get('data', {})
            
            # Ignorer les messages envoyés par nous-mêmes
            key = message_data.get('key', {})
            if key.get('fromMe', False):
                return jsonify({'status': 'ignored'}), 200
            
            # Extraire les infos
            remote_jid = key.get('remoteJid', '')
            sender_phone = remote_jid.split('@')[0]
            
            # Extraire le texte du message
            message_types = message_data.get('message', {})
            message_text = ''
            
            if 'conversation' in message_types:
                message_text = message_types['conversation']
            elif 'extendedTextMessage' in message_types:
                message_text = message_types['extendedTextMessage'].get('text', '')
            elif 'imageMessage' in message_types:
                message_text = message_types['imageMessage'].get('caption', '')
                if not message_text:
                    send_message(sender_phone, "🖼️ J'ai bien reçu votre image. Veuillez écrire votre question !")
                    return jsonify({'status': 'ok'}), 200
            
            if not message_text:
                return jsonify({'status': 'ignored'}), 200
            
            # Ignorer les messages de groupe (optionnel - décommenter pour activer)
            # if '@g.us' in remote_jid:
            #     return jsonify({'status': 'ignored'}), 200
            
            logger.info(f"📨 Message de {sender_phone}: {message_text[:50]}...")
            
            # Traiter avec le bot RAG
            response = bot.process_message(message_text, sender_phone)
            
            # Envoyer la réponse
            send_message(sender_phone, response)
            
            logger.info(f"✅ Réponse envoyée à {sender_phone}")
        
        return jsonify({'status': 'ok'}), 200
        
    except Exception as e:
        logger.error(f"❌ Erreur webhook: {e}")
        return jsonify({'status': 'error'}), 200

@app.route('/health', methods=['GET'])
def health_check():
    """Vérification de santé"""
    status = check_connection()
    return jsonify({
        'status': 'healthy',
        'whatsapp': status,
        'bot': 'active' if bot.collection else 'no_chromadb',
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
    print("🚀 Serveur Webhook Evolution API démarré")
    print(f"📚 Documents ChromaDB: {bot.collection.count() if bot.collection else 0}")
    print(f"🔗 Webhook: http://localhost:5000/evolution-webhook")
    
    port = int(os.getenv('PORT', 5000))
    app.run(host='0.0.0.0', port=port, debug=True)
