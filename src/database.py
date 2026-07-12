import os
from pymongo import MongoClient
from dotenv import load_dotenv

load_dotenv()

def get_db(): # Pastikan namanya get_db
    mongo_uri = os.getenv("MONGO_URI")
    client = MongoClient(mongo_uri, tlsAllowInvalidCertificates=True)
    db = client["archichat_db"]
    return db

# Test koneksi
if __name__ == "__main__":
    db = get_db()
    print("Berhasil terhubung ke MongoDB Atlas!")