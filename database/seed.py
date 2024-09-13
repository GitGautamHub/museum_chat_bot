# seed.py
from pymongo import MongoClient

# Connect to MongoDB
client = MongoClient('mongodb://localhost:27017/')
db = client['museum_ticket_bot']
collection = db['bookings']

# Sample data
sample_data = [
    {
        "booking_ref": "DEF456",
        "visit_date": "2024-09-02",
        "visitors": [
            {"name": "Alice Smith", "ticket_number": "223456", "ticket_price": 15.00, "category": "Adult"},
            {"name": "Bob Smith", "ticket_number": "223457", "ticket_price": 10.00, "category": "Child"}
        ],
        "recipient_email": "anilsehgal108@gmail.com"
    },
    {
        "booking_ref": "GHI789",
        "visit_date": "2024-09-03",
        "visitors": [
            {"name": "Charlie Brown", "ticket_number": "323456", "ticket_price": 20.00, "category": "Adult"},
            {"name": "Lucy Brown", "ticket_number": "323457", "ticket_price": 20.00, "category": "Adult"}
        ],
        "recipient_email": "divyanshs1810@gmail.com"
    }
]

# Insert sample data into MongoDB
collection.insert_many(sample_data)
print("Sample data inserted into MongoDB successfully.")
