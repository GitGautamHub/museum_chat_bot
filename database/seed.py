# seed.py
from pymongo import MongoClient

# Connect to MongoDB
client = MongoClient('mongodb://localhost:27017/')
db = client['museum_ticket_bot']
shows_collection = db['shows']

# Sample show data
sample_shows = [
    {
        "museum": "National Museum",
        "show_name": "Ancient Artifacts Show",
        "timings": ["10:00 AM", "12:00 PM", "3:00 PM", "5:00 PM"],
        "duration": "1 hour"
    },
    {
        "museum": "Rail Museum",
        "show_name": "Vintage Train Tour",
        "timings": ["9:30 AM", "11:30 AM", "2:30 PM", "4:30 PM"],
        "duration": "1.5 hours"
    }
]

# Insert sample data into MongoDB
shows_collection.insert_many(sample_shows)
print("Sample show data inserted into MongoDB successfully.")
