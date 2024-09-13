# test_db_connection.py
from db import db

# Test if collections can be accessed
def test_connection():
    # Access a collection (it will be created if it doesn't exist)
    test_collection = db.test_collection
    # Insert a test document
    test_doc = {"name": "Test", "description": "Testing MongoDB connection."}
    result = test_collection.insert_one(test_doc)
    print(f"Inserted document ID: {result.inserted_id}")

    # Fetch the document back
    fetched_doc = test_collection.find_one({"_id": result.inserted_id})
    print(f"Fetched document: {fetched_doc}")

if __name__ == "__main__":
    test_connection()
