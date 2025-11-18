import os
import json
import base64
from dotenv import load_dotenv
from firebase_admin import credentials, firestore
import firebase_admin

load_dotenv()

b64_creds = os.getenv("FIREBASE_CREDS_B64")
if not b64_creds:
    raise RuntimeError("Missing FIREBASE_CREDS_B64 environment variable")

# Decode and parse JSON
creds_json = base64.b64decode(b64_creds).decode("utf-8")
creds_dict = json.loads(creds_json)

cred = credentials.Certificate(creds_dict)

try:
    firebase_admin.get_app()
except ValueError:
    firebase_admin.initialize_app(cred)

db = firestore.client()
