import datetime
import firebase_admin
from firebase_admin import credentials, firestore

from backend.logger import get_logger

cred = credentials.Certificate("firebase_cred.json")
firebase_admin.initialize_app(cred)

logger = get_logger()


def init_db():
    db = firestore.client()
    return db
