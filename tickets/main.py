from pymongo import MongoClient
from generate_ticket import generate_ticket
from send_email import send_email_with_pdf

def process_ticket(booking_details):
    # Generate the ticket
    attachment_path = generate_ticket(booking_details)

    # Check if the ticket was generated successfully
    if not attachment_path:
        print("Failed to generate the ticket. Please check the errors and try again.")
        return

    # Send the email with the ticket attached
    subject = 'Your Museum Ticket'
    body = 'Please find your museum ticket attached.'
    send_email_with_pdf(booking_details["recipient_email"], subject, body, attachment_path)

def fetch_and_process_bookings():
    # Connect to MongoDB
    client = MongoClient('mongodb://localhost:27017/')
    db = client['museum_ticket_bot']
    collection = db['bookings']

    # Fetch all bookings from the database
    bookings = collection.find()

    for booking in bookings:
        print(f"Processing booking: {booking['booking_ref']}")
        process_ticket(booking)

if __name__ == "__main__":
    fetch_and_process_bookings()
