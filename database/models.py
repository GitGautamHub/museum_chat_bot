# models.py
from pymongo import ASCENDING
from database.db import db

# Define collections
users_collection = db.users
tickets_collection = db.tickets
shows_collection = db.shows
snacks_collection = db.snacks  # Define a new collection for snacks

# Create indexes for fast queries (optional but recommended)
users_collection.create_index([('email', ASCENDING)], unique=True)

# Function to add a user (no phone field)
def add_user(name, email):
    user = {
        "name": name,
        "email": email
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

# Function to get show timings for a museum
def get_show_timings(museum_name):
    return shows_collection.find_one({"museum": museum_name})

# Function to store snack booking details
def store_snack_booking(order_id, user_email, snacks_selected, total_price):
    user = find_user_by_email(user_email)
    if not user:
        print(f"User with email {user_email} not found.")
        return None

    snack_booking = {
        "order_id": order_id,
        "user_id": user['_id'],
        "snacks_selected": snacks_selected,
        "total_price": total_price,
        "booking_date": datetime.now()
    }
    return snacks_collection.insert_one(snack_booking)
