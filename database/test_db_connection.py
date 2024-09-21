# test_db_connection.py
from pymongo import MongoClient

def test_connection():
    client = MongoClient('mongodb://localhost:27017/')
    db = client['museum_ticket_bot']
    try:
        db.command("ping")
        print("Connected to MongoDB successfully.")
    except Exception as e:
        print(f"Failed to connect to MongoDB: {e}")

if __name__ == '__main__':
    test_connection()
