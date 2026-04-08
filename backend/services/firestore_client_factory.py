# firestore_client_factory.py

from google.cloud import firestore
import logging

logger = logging.getLogger(__name__)

def create_firestore_client(enabled: bool, project: str):
    if not enabled:
        logger.info("Firestore disabled.")
        return None

    try:
        client = firestore.AsyncClient(project=project)
        logger.info("✅ Firestore client initialized.")
        return client
    except Exception as e:
        logger.error(f"❌ Firestore init failed: {e}")
        return None