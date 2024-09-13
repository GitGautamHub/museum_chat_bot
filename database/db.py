# db.py
from pymongo import MongoClient

# MongoDB connection URI
MONGO_URI = "mongodb://localhost:27017"

# Create a MongoDB client
client = MongoClient(MONGO_URI)

# Connect to the database (create one if it doesn't exist)
db = client.museum_ticketing

print("Connected to MongoDB successfully.")
