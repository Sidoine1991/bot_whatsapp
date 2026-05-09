"""
📱 Bot WhatsApp Simple - Alternative sans Docker
Utilise Twilio ou autre API simple pour éviter les complications Docker
"""

import os
import logging
from flask import Flask, request, jsonify
from bot_whatsapp_rag import WhatsAppRAGBot
from dotenv import load_dotenv

load_dotenv()

app = Flask(__name__)
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# Initialisation du bot
bot = WhatsAppRAGBot()

@app.route('/test-bot', methods=['POST'])
def test_bot():
    """Tester le bot directement (pas WhatsApp)"""
    data = request.get_json()
    message = data.get('message', '')
    
    if not message:
        return jsonify({'error': 'Message requis'}), 400
    
    response = bot.process_message(message, 'test_user')
    
    return jsonify({
        'message': message,
        'response': response,
        'documents': bot.collection.count() if bot.collection else 0
    })

@app.route('/health', methods=['GET'])
def health_check():
    """Vérification de santé"""
    return jsonify({
        'status': 'healthy',
        'bot': 'active' if bot.collection else 'no_chromadb',
        'documents': bot.collection.count() if bot.collection else 0,
        'whatsapp': 'test_mode'
    })

@app.route('/simulate-whatsapp', methods=['POST'])
def simulate_whatsapp():
    """Simuler une interaction WhatsApp pour tester"""
    data = request.get_json()
    message = data.get('message', '')
    phone = data.get('phone', 'test_user')
    
    if not message:
        return jsonify({'error': 'Message requis'}), 400
    
    # Traiter comme un message WhatsApp
    response = bot.process_message(message, phone)
    
    logger.info(f"📨 Message simulé de {phone}: {message[:50]}...")
    logger.info(f"✅ Réponse générée: {response[:100]}...")
    
    return jsonify({
        'phone': phone,
        'message': message,
        'response': response,
        'timestamp': '2026-05-09T12:20:00Z',
        'whatsapp_simulation': True
    })

if __name__ == '__main__':
    print("=" * 60)
    print("🤖 Bot WhatsApp RAG - Mode Test Simple")
    print("=" * 60)
    print(f"📚 Documents ChromaDB: {bot.collection.count() if bot.collection else 0}")
    print(f"🔗 Test URL: http://localhost:5000/test-bot")
    print(f"📱 Simulation WhatsApp: http://localhost:5000/simulate-whatsapp")
    print("=" * 60)
    
    port = int(os.getenv('PORT', 5000))
    app.run(host='0.0.0.0', port=port, debug=True)
