import firebase_admin
from firebase_admin import credentials, firestore

cred = credentials.Certificate("firebase_cred.json")
firebase_admin.initialize_app(cred)
def init_db():
    db = firestore.client()
    return db
