"""
🚀 Configuration Evolution API - Alternative simple à Meta Cloud API
Pas besoin de compte Meta Business ! Scan QR code → Connecté

Étapes:
1. Installer Docker Desktop: https://docker.com/products/docker-desktop
2. Lancer Evolution API: docker run ...
3. Scanner le QR code avec votre WhatsApp
4. Lancer ce script pour connecter le bot
"""

import requests
import json
import time
import logging
import os
from dotenv import load_dotenv
from bot_whatsapp_rag import WhatsAppRAGBot

load_dotenv()

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# Configuration Evolution API
EVOLUTION_API_URL = os.getenv('EVOLUTION_API_URL', 'http://localhost:8080')
EVOLUTION_API_KEY = os.getenv('EVOLUTION_API_KEY', '')
INSTANCE_NAME = os.getenv('INSTANCE_NAME', 'ccrb-bot')

# Bot RAG
bot = WhatsAppRAGBot()

def create_instance():
    """Créer une instance WhatsApp dans Evolution API"""
    url = f"{EVOLUTION_API_URL}/instance/create"
    
    headers = {
        "Content-Type": "application/json",
        "apikey": EVOLUTION_API_KEY
    }
    
    data = {
        "instanceName": INSTANCE_NAME,
        "qrcode": True,
        "integration": "WHATSAPP-BAILEYS"
    }
    
    try:
        response = requests.post(url, headers=headers, json=data, timeout=30)
        
        if response.status_code in [200, 201]:
            result = response.json()
            logger.info(f"✅ Instance '{INSTANCE_NAME}' créée")
            return result
        else:
            logger.error(f"❌ Erreur création instance: {response.text}")
            return None
            
    except Exception as e:
        logger.error(f"❌ Erreur connexion Evolution API: {e}")
        logger.info("💡 Assurez-vous que Evolution API est lancé (Docker)")
        return None

def get_qr_code():
    """Obtenir le QR code pour connecter WhatsApp"""
    url = f"{EVOLUTION_API_URL}/instance/connect/{INSTANCE_NAME}"
    
    headers = {
        "Content-Type": "application/json",
        "apikey": EVOLUTION_API_KEY
    }
    
    try:
        response = requests.get(url, headers=headers, timeout=30)
        
        if response.status_code == 200:
            result = response.json()
            
            if 'base64' in result:
                # Sauvegarder le QR code comme image
                import base64
                qr_data = result['base64']
                
                # Enlever le préfixe data:image si présent
                if ',' in qr_data:
                    qr_data = qr_data.split(',')[1]
                
                with open('qr_code.png', 'wb') as f:
                    f.write(base64.b64decode(qr_data))
                
                logger.info("📱 QR code sauvegardé: qr_code.png")
                logger.info("📱 Ouvrez qr_code.png et scannez avec WhatsApp")
                logger.info("📱 WhatsApp → Appareils connectés → Scanner le QR code")
                return result
            elif result.get('instance', {}).get('status') == 'CONNECTED':
                logger.info("✅ WhatsApp déjà connecté !")
                return result
            else:
                logger.info(f"📊 Statut: {result}")
                return result
        else:
            logger.error(f"❌ Erreur QR code: {response.text}")
            return None
            
    except Exception as e:
        logger.error(f"❌ Erreur: {e}")
        return None

def check_connection():
    """Vérifier le statut de connexion"""
    url = f"{EVOLUTION_API_URL}/instance/fetchInstances?instanceName={INSTANCE_NAME}"
    
    headers = {
        "Content-Type": "application/json",
        "apikey": EVOLUTION_API_KEY
    }
    
    try:
        response = requests.get(url, headers=headers, timeout=10)
        
        if response.status_code == 200:
            instances = response.json()
            
            if instances:
                for inst in instances:
                    status = inst.get('instance', {}).get('status', 'UNKNOWN')
                    name = inst.get('instance', {}).get('instanceName', '')
                    logger.info(f"📊 Instance '{name}': {status}")
                    return status
            else:
                logger.info("📭 Aucune instance trouvée")
                return "NOT_FOUND"
        else:
            return "ERROR"
            
    except Exception as e:
        logger.error(f"❌ Erreur vérification: {e}")
        return "ERROR"

def send_message(phone_number: str, message: str) -> bool:
    """Envoyer un message WhatsApp via Evolution API"""
    url = f"{EVOLUTION_API_URL}/message/sendText/{INSTANCE_NAME}"
    
    headers = {
        "Content-Type": "application/json",
        "apikey": EVOLUTION_API_KEY
    }
    
    # Formater le numéro (ajouter @s.whatsapp.net si nécessaire)
    if '@' not in phone_number:
        phone_number = f"{phone_number}@s.whatsapp.net"
    
    data = {
        "number": phone_number,
        "textMessage": {
            "text": message
        }
    }
    
    try:
        response = requests.post(url, headers=headers, json=data, timeout=30)
        
        if response.status_code in [200, 201]:
            logger.info(f"✅ Message envoyé à {phone_number}")
            return True
        else:
            logger.error(f"❌ Erreur envoi: {response.text}")
            return False
            
    except Exception as e:
        logger.error(f"❌ Exception: {e}")
        return False

def start_webhook_listener():
    """
    Configurer le webhook dans Evolution API pour recevoir les messages
    Evolution API enverra les messages entrants vers notre serveur Flask
    """
    url = f"{EVOLUTION_API_URL}/instance/setWebhook/{INSTANCE_NAME}"
    
    headers = {
        "Content-Type": "application/json",
        "apikey": EVOLUTION_API_KEY
    }
    
    webhook_url = os.getenv('WEBHOOK_URL', 'http://localhost:5000/evolution-webhook')
    
    data = {
        "enabled": True,
        "url": webhook_url,
        "webhookByEvents": True,
        "events": [
            "MESSAGES_UPSERT",
            "CONNECTION_UPDATE"
        ]
    }
    
    try:
        response = requests.post(url, headers=headers, json=data, timeout=30)
        
        if response.status_code in [200, 201]:
            logger.info(f"✅ Webhook configuré: {webhook_url}")
            return True
        else:
            logger.error(f"❌ Erreur webhook: {response.text}")
            return False
            
    except Exception as e:
        logger.error(f"❌ Exception webhook: {e}")
        return False

def setup():
    """Configuration complète"""
    print("=" * 60)
    print("🚀 Configuration Evolution API - Bot WhatsApp RAG")
    print("=" * 60)
    
    # 1. Créer l'instance
    print("\n1️⃣ Création de l'instance WhatsApp...")
    result = create_instance()
    
    if not result:
        print("❌ Impossible de créer l'instance")
        print("💡 Vérifiez que Docker et Evolution API sont lancés")
        return False
    
    # 2. Obtenir le QR code
    print("\n2️⃣ Obtention du QR code...")
    qr_result = get_qr_code()
    
    if qr_result:
        print("\n📱 SCANNEZ LE QR CODE AVEC WHATSAPP:")
        print("   1. Ouvrez WhatsApp sur votre téléphone")
        print("   2. Allez dans Paramètres → Appareils connectés")
        print("   3. Appuyez sur 'Connecter un appareil'")
        print("   4. Scannez le QR code (qr_code.png)")
        print("\n⏳ En attente de connexion...")
        
        # Attendre la connexion
        for i in range(60):
            time.sleep(3)
            status = check_connection()
            
            if status == 'CONNECTED':
                print("\n✅ WHATSAPP CONNECTÉ AVEC SUCCÈS !")
                break
            elif status == 'NOT_FOUND':
                print("❌ Instance non trouvée")
                break
        else:
            print("\n⏰ Délai expiré. Relancez le script.")
            return False
    else:
        # Vérifier si déjà connecté
        status = check_connection()
        if status == 'CONNECTED':
            print("✅ WhatsApp déjà connecté !")
        else:
            print("❌ Impossible d'obtenir le QR code")
            return False
    
    # 3. Configurer le webhook
    print("\n3️⃣ Configuration du webhook...")
    start_webhook_listener()
    
    print("\n" + "=" * 60)
    print("🎉 Configuration terminée !")
    print(f"📚 Documents ChromaDB: {bot.collection.count() if bot.collection else 0}")
    print(f"🤖 Bot prêt à répondre sur WhatsApp !")
    print("=" * 60)
    
    return True

if __name__ == '__main__':
    setup()
