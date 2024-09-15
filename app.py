from flask import Flask, request, jsonify, render_template
from chatbot.nlp_utils import predict_class, get_response
from tickets.generate_ticket import generate_ticket
from tickets.send_email import send_email_with_pdf
from pymongo import MongoClient
import json
import os

app = Flask(__name__)

# Load intents file
try:
    with open('chatbot/intents.json', encoding='utf-8') as file:
        intents = json.load(file)
    print("[INFO] Intents loaded in Flask app.")
except Exception as e:
    print(f"[ERROR] Error loading intents.json in Flask app: {e}")
    intents = []

# In-memory booking session storage
booking_sessions = {}

# MongoDB client setup
client = MongoClient('mongodb://localhost:27017/')
db = client['museum_ticket_bot']
bookings_collection = db['bookings']

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/chat', methods=['POST'])
def chat():
    user_message = request.json.get("message")
    session_id = request.remote_addr

    # Check if the user is in a booking session
    if session_id in booking_sessions:
        return continue_booking()

    # Handle normal conversation
    try:
        if not user_message:
            return jsonify({"response": "Sorry, I didn't get that. Could you please repeat?"})

        intents_prediction = predict_class(user_message)
        response = get_response(intents_prediction, intents)

        return jsonify({"response": response})
    except Exception as e:
        print(f"[ERROR] Error handling request: {e}")
        return jsonify({"response": "Sorry, something went wrong. Please try again."})

@app.route('/start-booking', methods=['POST'])
def start_booking():
    session_id = request.remote_addr  # Use IP as session ID (simple implementation)
    booking_sessions[session_id] = {
        'step': 'collecting_name',
        'details': {}
    }
    return jsonify({"response": "Let's start booking your ticket. What's your name?"})

@app.route('/continue-booking', methods=['POST'])
def continue_booking():
    session_id = request.remote_addr
    user_response = request.json.get("message")

    if session_id in booking_sessions:
        session = booking_sessions[session_id]

        # Collecting user details step by step
        if session['step'] == 'collecting_name':
            session['details']['name'] = user_response
            session['step'] = 'collecting_email'
            return jsonify({"response": "Great! What's your email address?"})

        elif session['step'] == 'collecting_email':
            session['details']['email'] = user_response
            session['step'] = 'collecting_ticket_count'
            return jsonify({"response": "How many tickets would you like to book?"})

        elif session['step'] == 'collecting_ticket_count':
            try:
                session['details']['ticket_count'] = int(user_response)
                session['step'] = 'collecting_visit_date'
                return jsonify({"response": "When would you like to visit? (Please provide the date in YYYY-MM-DD format)"})
            except ValueError:
                return jsonify({"response": "Please enter a valid number for the ticket count."})

        elif session['step'] == 'collecting_visit_date':
            session['details']['visit_date'] = user_response
            session['step'] = 'collecting_payment'
            return jsonify({"response": "Please proceed with the payment and type 'done' once completed. https://upload.wikimedia.org/wikipedia/commons/d/d0/QR_code_for_mobile_English_Wikipedia.svg"})

        elif session['step'] == 'collecting_payment':
            if user_response.lower() == 'done':
                booking_details = {
                    "booking_ref": "RANDOM123",  # In production, generate a unique ref
                    "visit_date": session['details']['visit_date'],
                    "visitors": [
                        {
                            "name": session['details']['name'],
                            "ticket_number": "123456",  # Generate a unique ticket number
                            "ticket_price": 15.00,  # Add dynamic pricing if needed
                            "category": "Adult"  # Default to Adult; update as needed
                        }
                    ],
                    "recipient_email": session['details']['email']
                }

                # Generate ticket and send email
                attachment_path = generate_ticket(booking_details)
                send_email_with_pdf(
                    session['details']['email'],
                    "Your Museum Ticket",
                    "Please find your museum ticket attached.",
                    attachment_path
                )

                # Insert booking details into MongoDB
                bookings_collection.insert_one({
                    "booking_ref": booking_details["booking_ref"],
                    "visit_date": booking_details["visit_date"],
                    "visitors": booking_details["visitors"],
                    "recipient_email": booking_details["recipient_email"],
                    "status": "Completed"
                })

                # Reset the session after booking is complete
                del booking_sessions[session_id]
                return jsonify({"response": "Your tickets have been booked and sent to your email!"})
            else:
                return jsonify({"response": "Please complete the payment and type 'done'."})

    # Handle cases where there's no active booking session
    return jsonify({"response": "It seems we're not in a booking session. Please start again."})

if __name__ == '__main__':
    app.secret_key = os.urandom(24)  # Set a secret key for sessions
    app.run(debug=True)
