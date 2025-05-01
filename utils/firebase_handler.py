# firebase_handler.py
import os
import json
import tempfile
import firebase_admin
from firebase_admin import credentials, firestore, db

# Initialize Firebase App
firebase_app = None

def init_firebase():
    global firebase_app
    if firebase_app is None:
        print("Initializing Firebase App...")
        firebase_credentials = os.getenv("FIREBASE_CREDENTIALS")
        if not firebase_credentials:
            raise Exception("FIREBASE_CREDENTIALS environment variable not found.")
        
        credentials_dict = json.loads(firebase_credentials)
        with tempfile.NamedTemporaryFile(mode="w+", suffix=".json", delete=False) as temp_file:
            json.dump(credentials_dict, temp_file)
            temp_file.flush()
            cred = credentials.Certificate(temp_file.name)
            firebase_app = firebase_admin.initialize_app(cred, {
                'databaseURL': os.getenv("FIREBASE_DB_URL")
            })
        print("Firebase Initialized Successfully.")

# Get Firestore Client
def get_firestore_client():
    if not firebase_app:
        init_firebase()
    return firestore.client()

# Get Realtime Database Client
def get_realtime_db():
    if not firebase_app:
        init_firebase()
    return db.reference()

# Load Access Token (from Firestore)
def get_access_token():
    client = get_firestore_client()
    doc = client.collection("tokens").document("upstox").get()
    return doc.to_dict().get("access_token")

# Load Stock List (from Realtime DB)
def load_stock_symbols():
    root = get_realtime_db().child("stocks").get()
    all_symbols = []
    for category in ["nifty50", "niftymidcap50", "niftysmallcap50"]:
        for symbol, instrument_key in root.get(category, {}).items():
            all_symbols.append((category, symbol, instrument_key))
    return all_symbols
