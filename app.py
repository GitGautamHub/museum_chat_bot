from flask import Flask, request, jsonify, render_template, send_file, url_for
from chatbot.nlp_utils import predict_class, get_response
from tickets.generate_ticket import generate_ticket
from tickets.send_email import send_email_with_pdf
from pymongo import MongoClient
import json
import os
from datetime import datetime

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
try:
    client = MongoClient('mongodb://localhost:27017/')
    db = client['museum_ticket_bot']
    bookings_collection = db['bookings']
    print("[INFO] Connected to MongoDB successfully.")
except Exception as e:
    print(f"[ERROR] Error connecting to MongoDB: {e}")

def calculate_ticket_price(adult_count, child_count, senior_count, foreigner_count, visit_date):
    """Calculate the total price of tickets based on the counts for each category and date type."""
    # Prices for weekdays and weekends
    weekday_prices = {'adult': 15.00, 'child': 10.00, 'senior': 12.00, 'foreigner': 25.00}
    weekend_prices = {'adult': 20.00, 'child': 15.00, 'senior': 18.00, 'foreigner': 30.00}
    
    # Check if the selected date is a weekend
    visit_datetime = datetime.strptime(visit_date, '%Y-%m-%d')
    if visit_datetime.weekday() >= 5:  # 5 = Saturday, 6 = Sunday
        prices = weekend_prices
    else:
        prices = weekday_prices
    
    total_price = (adult_count * prices['adult']) + (child_count * prices['child']) + \
                  (senior_count * prices['senior']) + (foreigner_count * prices['foreigner'])
    return total_price

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
        'step': 'selecting_state',
        'details': {}
    }
    
    # Prompt the user to select a state
    state_options = (
        "Please select a state to see available cities:\n\n"
        "🌐 1. Delhi\n"
        "🌐 2. Maharashtra\n"
        "🌐 3. West Bengal\n"
        "🌐 4. Rajasthan\n"
        "🌐 5. Telangana\n\n"
        "Enter the number corresponding to your choice."
    )
    return jsonify({"response": state_options})

@app.route('/continue-booking', methods=['POST'])
def continue_booking():
    session_id = request.remote_addr
    user_response = request.json.get("message")

    if session_id in booking_sessions:
        session = booking_sessions[session_id]

        # Step 1: Selecting a state
        if session['step'] == 'selecting_state':
            state_map = {
                '1': 'Delhi',
                '2': 'Maharashtra',
                '3': 'West Bengal',
                '4': 'Rajasthan',
                '5': 'Telangana'
            }

            selected_state = state_map.get(user_response)
            if not selected_state:
                return jsonify({"response": "Please enter a valid number to select a state."})
            
            session['details']['state'] = selected_state
            session['step'] = 'selecting_city'

            # Prompt user to select a city based on the selected state
            cities_by_state = {
                'Delhi': "Available cities in Delhi:\n\n🏙️ 1. New Delhi\n\nEnter the number corresponding to your choice.",
                'Maharashtra': "Available cities in Maharashtra:\n\n🏙️ 1. Mumbai\n🏙️ 2. Pune\n\nEnter the number corresponding to your choice.",
                'West Bengal': "Available cities in West Bengal:\n\n🏙️ 1. Kolkata\n\nEnter the number corresponding to your choice.",
                'Rajasthan': "Available cities in Rajasthan:\n\n🏙️ 1. Jaipur\n\nEnter the number corresponding to your choice.",
                'Telangana': "Available cities in Telangana:\n\n🏙️ 1. Hyderabad\n\nEnter the number corresponding to your choice."
            }

            return jsonify({"response": cities_by_state[selected_state]})

        # Step 2: Selecting a city based on state
        if session['step'] == 'selecting_city':
            state = session['details']['state']
            city_map = {
                'Delhi': {'1': 'New Delhi'},
                'Maharashtra': {'1': 'Mumbai', '2': 'Pune'},
                'West Bengal': {'1': 'Kolkata'},
                'Rajasthan': {'1': 'Jaipur'},
                'Telangana': {'1': 'Hyderabad'}
            }

            selected_city = city_map[state].get(user_response)
            if not selected_city:
                return jsonify({"response": "Please enter a valid number to select a city."})
            
            session['details']['city'] = selected_city
            session['step'] = 'selecting_museum'

            # Prompt user to select a museum based on the selected city
            museums_by_city = {
                'New Delhi': "Available museums in New Delhi:\n\n🏛️ 1. National Museum\n🏛️ 2. Rail Museum\n🏛️ 3. Crafts Museum\n\nEnter the number corresponding to your choice.",
                'Mumbai': "Available museums in Mumbai:\n\n🏛️ 1. Chhatrapati Shivaji Maharaj Vastu Sangrahalaya\n🏛️ 2. Dr. Bhau Daji Lad Museum\n\nEnter the number corresponding to your choice.",
                'Pune': "Available museums in Pune:\n\n🏛️ 1. Raja Dinkar Kelkar Museum\n\nEnter the number corresponding to your choice.",
                'Kolkata': "Available museums in Kolkata:\n\n🏛️ 1. Indian Museum\n🏛️ 2. Victoria Memorial\n\nEnter the number corresponding to your choice.",
                'Jaipur': "Available museums in Jaipur:\n\n🏛️ 1. City Palace Museum\n🏛️ 2. Albert Hall Museum\n\nEnter the number corresponding to your choice.",
                'Hyderabad': "Available museums in Hyderabad:\n\n🏛️ 1. Salar Jung Museum\n🏛️ 2. Telangana State Museum\n\nEnter the number corresponding to your choice."
            }

            return jsonify({"response": museums_by_city[selected_city]})

        # Step 3: Selecting a museum based on city
        if session['step'] == 'selecting_museum':
            city = session['details']['city']
            museum_map = {
                'New Delhi': {
                    '1': 'National Museum',
                    '2': 'Rail Museum',
                    '3': 'Crafts Museum'
                },
                'Mumbai': {
                    '1': 'Chhatrapati Shivaji Maharaj Vastu Sangrahalaya',
                    '2': 'Dr. Bhau Daji Lad Museum'
                },
                'Pune': {
                    '1': 'Raja Dinkar Kelkar Museum'
                },
                'Kolkata': {
                    '1': 'Indian Museum',
                    '2': 'Victoria Memorial'
                },
                'Jaipur': {
                    '1': 'City Palace Museum',
                    '2': 'Albert Hall Museum'
                },
                'Hyderabad': {
                    '1': 'Salar Jung Museum',
                    '2': 'Telangana State Museum'
                }
            }

            selected_museum = museum_map[city].get(user_response)
            if not selected_museum:
                return jsonify({"response": "Please enter a valid number to select a museum."})
            
            session['details']['museum'] = selected_museum
            session['step'] = 'selecting_date'
            return jsonify({
                "response": "Please enter the date for your visit in the format YYYY-MM-DD (e.g., 2024-09-22)."
            })

        # Step 4: Selecting a visit date
        if session['step'] == 'selecting_date':
            try:
                # Validate the user-provided date
                visit_date = datetime.strptime(user_response, '%Y-%m-%d')
                session['details']['visit_date'] = user_response
                session['step'] = 'collecting_name'
                return jsonify({"response": "You selected the date. Let's start booking your ticket. What's your name?"})
            except ValueError:
                return jsonify({
                    "response": "Please enter a valid date in the format YYYY-MM-DD (e.g., 2024-09-22)."
                })

        # Continue with collecting user details, calculating prices, and completing the booking as before
        if session['step'] == 'collecting_name':
            session['details']['name'] = user_response
            session['step'] = 'collecting_email'
            return jsonify({"response": "Great! What's your email address?"})

        elif session['step'] == 'collecting_email':
            session['details']['email'] = user_response
            session['step'] = 'collecting_adult_tickets'
            return jsonify({"response": "How many tickets would you like to book for Adults? (Enter 0 if none)"})

        elif session['step'] == 'collecting_adult_tickets':
            try:
                session['details']['adult_count'] = int(user_response)
                session['step'] = 'collecting_child_tickets'
                return jsonify({"response": "How many tickets would you like to book for Children (below 12 years old)? (Enter 0 if none)"})
            except ValueError:
                return jsonify({"response": "Please enter a valid number for adult tickets."})

        elif session['step'] == 'collecting_child_tickets':
            try:
                session['details']['child_count'] = int(user_response)
                session['step'] = 'collecting_senior_tickets'
                return jsonify({"response": "How many tickets would you like to book for Seniors (above 60 years old)? (Enter 0 if none)"})
            except ValueError:
                return jsonify({"response": "Please enter a valid number for child tickets."})

        elif session['step'] == 'collecting_senior_tickets':
            try:
                session['details']['senior_count'] = int(user_response)
                session['step'] = 'collecting_foreigner_tickets'
                return jsonify({"response": "How many tickets would you like to book for Foreigners? (Enter 0 if none)"})
            except ValueError:
                return jsonify({"response": "Please enter a valid number for senior tickets."})

        elif session['step'] == 'collecting_foreigner_tickets':
            try:
                session['details']['foreigner_count'] = int(user_response)

                # Calculate total price
                adult_count = session['details']['adult_count']
                child_count = session['details']['child_count']
                senior_count = session['details']['senior_count']
                foreigner_count = session['details']['foreigner_count']
                visit_date = session['details']['visit_date']
                total_price = calculate_ticket_price(adult_count, child_count, senior_count, foreigner_count, visit_date)
                session['details']['total_price'] = total_price

                session['step'] = 'collecting_payment'

                # Provide payment instructions
                # Provide payment instructions with an image
                response_message = (
                    f"🎟️ The total price is ₹ {total_price:.2f}.\nPlease make the payment using the given 💳 UPI id:---"
                    "'museum@upi'\n\n"
                    "🎟️ After completing the payment, please enter your UTR number below. 📧"
                )

                # URL for the image to render
                image_url = url_for('static', filename='images/albert.jpg')  # Ensure the filename matches exactly

                # Send the response with the image URL
                return jsonify({
                    "response": response_message,
                    "image_url": image_url
                })

            except ValueError:
                return jsonify({"response": "Please enter a valid number for foreigner tickets."})

        elif session['step'] == 'collecting_payment':
            # Directly collect UTR number
            session['details']['utr_number'] = user_response

            # Retrieve details for booking
            booking_details = {
                "booking_ref": "RANDOM123",  # In production, generate a unique reference
                "museum": session['details']['museum'],
                "visit_date": session['details'].get('visit_date', 'Not specified'),
                "visitors": [
                    {
                        "name": session['details']['name'],
                        "ticket_number": "123456",  # Generate a unique ticket number
                        "ticket_price": session['details']['total_price'],  # Use calculated total price
                        "category": {
                            "Adults": session['details']['adult_count'],
                            "Children": session['details']['child_count'],
                            "Seniors": session['details']['senior_count'],
                            "Foreigners": session['details']['foreigner_count']
                        }
                    }
                ],
                "recipient_email": session['details']['email'],
                "utr_number": session['details']['utr_number']  # Store UTR number
            }

            # Generate ticket and send email
            attachment_path = generate_ticket(booking_details)
            send_email_with_pdf(
                session['details']['email'],
                "Your Museum Ticket",
                f"Please find your museum ticket attached for {session['details']['museum']}. The total price is Rs {session['details']['total_price']:.2f}.",
                attachment_path
            )

            # Insert booking details into MongoDB with error handling
            try:
                print(f"[DEBUG] Inserting booking details into MongoDB: {booking_details}")
                result = bookings_collection.insert_one({
                    "booking_ref": booking_details["booking_ref"],
                    "museum": booking_details["museum"],
                    "visit_date": booking_details["visit_date"],
                    "visitors": booking_details["visitors"],
                    "recipient_email": booking_details["recipient_email"],
                    "utr_number": booking_details["utr_number"],
                    "status": "Completed"
                })
                print(f"[INFO] Booking inserted with ID: {result.inserted_id}")
            except Exception as e:
                print(f"[ERROR] Error inserting booking into MongoDB: {e}")

            # Reset the session after booking is complete
            del booking_sessions[session_id]
            return jsonify({"response": f"Your tickets for {session['details']['museum']} have been booked for Rs {session['details']['total_price']:.2f} and sent to your email! Your UTR number is recorded."})

    # Handle cases where there's no active booking session
    return jsonify({"response": "It seems we're not in a booking session. Please start again."})

if __name__ == '__main__':
    app.secret_key = os.urandom(24)  # Set a secret key for sessions
    app.run(debug=True)