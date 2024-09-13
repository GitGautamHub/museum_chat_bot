# models.py
from pymongo import ASCENDING
from db import db

# Define collections
users_collection = db.users
tickets_collection = db.tickets

# Create indexes for fast queries (optional but recommended)
users_collection.create_index([('email', ASCENDING)], unique=True)

# Function to add a user
def add_user(name, email, phone=None):
    user = {
        "name": name,
        "email": email,
        "phone": phone
    }
    return users_collection.insert_one(user)

# Function to find a user by email
def find_user_by_email(email):
    return users_collection.find_one({"email": email})

# Function to create a ticket
def create_ticket(booking_ref, user_email, visit_date, ticket_type, quantity, price):
    user = find_user_by_email(user_email)
    if not user:
        print(f"User with email {user_email} not found.")
        return None
    
    ticket = {
        "booking_ref": booking_ref,
        "user_id": user['_id'],
        "visit_date": visit_date,
        "ticket_type": ticket_type,
        "quantity": quantity,
        "price": price
    }
    return tickets_collection.insert_one(ticket)
