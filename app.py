from flask import Flask, request, jsonify, render_template, send_file, url_for
from chatbot.nlp_utils import predict_class, get_response
from tickets.generate_ticket import generate_ticket
from tickets.send_email import send_email_with_pdf
from pymongo import MongoClient
from database.models import add_user, find_user_by_email, create_ticket, store_snack_booking, get_show_timings
import json
import os
from datetime import datetime
from langdetect import detect
import random
import string
import logging

# Set up logging
logging.basicConfig(level=logging.DEBUG)

app = Flask(__name__)

# Load intents file for fallback response
try:
    with open('chatbot/intents/english/intents_english.json', encoding='utf-8') as file:
        default_intents = json.load(file)
    print("[INFO] Default intents loaded in Flask app.")
except Exception as e:
    print(f"[ERROR] Error loading default intents.json in Flask app: {e}")
    default_intents = []

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

def calculate_ticket_price(adult_count, child_count, senior_count, foreigner_count, visit_date, wheelchair, snacks, tour_guide):
    """Calculate the total price of tickets based on the counts for each category and date type, including additional services."""
    # Prices for weekdays and weekends
    weekday_prices = {'adult': 15.00, 'child': 10.00, 'senior': 12.00, 'foreigner': 25.00}
    weekend_prices = {'adult': 20.00, 'child': 15.00, 'senior': 18.00, 'foreigner': 30.00}

    # Additional service prices
    service_prices = {'wheelchair': 5.00, 'snacks': 10.00, 'tour_guide': 20.00}
    
    # Check if the selected date is a weekend
    visit_datetime = datetime.strptime(visit_date, '%Y-%m-%d')
    if visit_datetime.weekday() >= 5:  # 5 = Saturday, 6 = Sunday
        prices = weekend_prices
    else:
        prices = weekday_prices
    
    total_price = (adult_count * prices['adult']) + (child_count * prices['child']) + \
                  (senior_count * prices['senior']) + (foreigner_count * prices['foreigner'])

    # Adding service prices if selected
    if wheelchair:
        total_price += service_prices['wheelchair']
    if snacks:
        total_price += service_prices['snacks']
    if tour_guide:
        total_price += service_prices['tour_guide']

    return total_price

@app.route('/')
def index():
    return render_template('index.html')

LANGUAGE_CODE_MAP = {
    'en': 'english',
    'hi': 'hindi',
    'bn': 'bengali',
    'mr': 'marathi',
    # Add other language mappings as needed
}

def detect_language(text):
    try:
        detected_lang = detect(text)
        # Map the detected language code to your supported language code
        return LANGUAGE_CODE_MAP.get(detected_lang, "english")  # Default to English if unsupported language is detected
    except:
        return "english"  # Default to English if language detection fails

@app.route('/chat', methods=['POST'])
def chat():
    user_message = request.json.get("message")
    language_code = request.json.get("language_code", None)  # None by default to trigger language detection
    session_id = request.remote_addr

    # Check if the user is in a booking session
    if session_id in booking_sessions:
        return continue_booking()

    # Handle normal conversation
    try:
        if not user_message:
            return jsonify({"response": "Sorry, I didn't get that. Could you please repeat?"})

        # If language_code is not provided, detect language dynamically
        if not language_code:
            language_code = detect_language(user_message)
            print(f"[INFO] Detected Language: {language_code}")

        intents_prediction = predict_class(user_message, language_code)
        response = get_response(intents_prediction, language_code)

        return jsonify({"response": response})
    except Exception as e:
        print(f"[ERROR] Error handling request: {e}")
        return jsonify({"response": "Sorry, something went wrong. Please try again."})

@app.route('/start-booking', methods=['POST'])
def start_booking():
    session_id = request.remote_addr  # Use IP as session ID (simple implementation)
    booking_sessions[session_id] = {
        'step': 'selecting_state',
        'details': {
            'wheelchair': False,
            'snacks': False,
            'tour_guide': False,
            'snacks_order_id': None
        }
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
def continue_booking_route():
    return continue_booking()

def continue_booking():
    session_id = request.remote_addr
    user_response = request.json.get("message").strip()  # Use strip() to handle any whitespace issues
    logging.debug(f"Session ID: {session_id}, User Response: {user_response}")

    if session_id in booking_sessions:
        session = booking_sessions[session_id]
        logging.debug(f"Session Step: {session['step']}")

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
            logging.debug(f"Selected State: {selected_state}")
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
                session['details']['total_price'] = calculate_ticket_price(
                        adult_count=adult_count,
                        child_count=child_count,
                        senior_count=senior_count,
                        foreigner_count=foreigner_count,
                        visit_date=visit_date,
                        wheelchair=session['details'].get('wheelchair', False),
                        tour_guide=session['details'].get('tour_guide', False),
                        snacks=False  # Snacks option removed
                    )

                session['step'] = 'selecting_services'
                return jsonify({
                    "response": f"🎟️ The total price is ₹ {session['details']['total_price']:.2f}.\nWould you like to add any additional services?\n\n"
                                "1. Wheelchair Assistance\n"
                                "2. Tour Guide\n\n"
                                "Please enter the number corresponding to your choice or 0 to skip."
                })

            except ValueError:
                return jsonify({"response": "Please enter a valid number for foreigner tickets."})

        # Step 5: Selecting additional services
        elif session['step'] == 'selecting_services':
            services_map = {
                '1': 'Wheelchair Assistance',
                '2': 'Tour Guide',
                '0': 'No additional services'
            }

            selected_service = services_map.get(user_response)
            if not selected_service:
                return jsonify({"response": "Please enter a valid number to select a service."})

            if selected_service == 'Wheelchair Assistance':
                session['details']['wheelchair'] = True
                session['step'] = 'selecting_additional_service'  # Skip confirmation step for a smoother experience
                return jsonify({
                    "response": "Wheelchair Assistance added. Would you like to add more services?\n\n"
                                "1. Tour Guide\n\n"
                                "Enter the number corresponding to your choice or 0 to skip."
                })

            elif selected_service == 'Tour Guide':
                session['details']['tour_guide'] = True
                session['step'] = 'selecting_additional_service'
                return jsonify({
                    "response": "Tour Guide added. Would you like to add more services?\n\n"
                                "1. Wheelchair Assistance\n\n"
                                "Enter the number corresponding to your choice or 0 to skip."
                })

            elif selected_service == 'No additional services':
                session['step'] = 'collecting_payment'
                return jsonify({
                    "response": f"🎟️ The total price is ₹ {session['details']['total_price']:.2f}.\nPlease make the payment using the given 💳 UPI id: 'museum@upi'\n\n"
                                "🎟️ After completing the payment, please enter your UTR number below. 📧"
                })

        # Step 6: Finalizing additional services or skipping
        # Step 7: Finalizing additional services or skipping
        elif session['step'] == 'selecting_additional_service':
            additional_services_map = {
                '1': 'Tour Guide',
                '0': 'No additional services'
            }

            additional_service = additional_services_map.get(user_response)
            if not additional_service:
                return jsonify({"response": "Please enter a valid number to select a service."})

            if additional_service == 'Tour Guide':
                if not session['details'].get('tour_guide'):
                    session['details']['tour_guide'] = True  # Set tour guide service
                session['step'] = 'selecting_additional_service'  # Remain on the same step to add more services
                return jsonify({
                    "response": "Tour Guide added. Would you like to add more services?\n\n"
                                "1. Wheelchair Assistance\n"
                                "Enter the number corresponding to your choice or 0 to skip."
                })

            elif additional_service == 'No additional services':
                session['step'] = 'collecting_payment'
                return jsonify({
                    "response": f"🎟️ The total price is ₹ {session['details']['total_price']:.2f}.\nPlease make the payment using the given 💳 UPI id: 'museum@upi'\n\n"
                                "🎟️ After completing the payment, please enter your UTR number below. 📧"
                })

        elif session['step'] == 'selecting_additional_service':
            additional_services_map = {
                '1': 'Wheelchair Assistance',
                '0': 'No additional services'
            }

            additional_service = additional_services_map.get(user_response)
            if not additional_service:
                return jsonify({"response": "Please enter a valid number to select a service."})

            if additional_service == 'Wheelchair Assistance':
                if not session['details'].get('wheelchair'):
                    session['details']['wheelchair'] = True
                session['step'] = 'selecting_additional_service'
                return jsonify({
                    "response": "Wheelchair Assistance added. Would you like to add more services?\n\n"
                                "1. Tour Guide\n\n"
                                "Enter the number corresponding to your choice or 0 to skip."
                })

            elif additional_service == 'No additional services':
                session['step'] = 'collecting_payment'
                return jsonify({
                    "response": f"🎟️ The total price is ₹ {session['details']['total_price']:.2f}.\nPlease make the payment using the given 💳 UPI id: 'museum@upi'\n\n"
                                "🎟️ After completing the payment, please enter your UTR number below. 📧"
                })

        # Step 7: Collecting payment
        elif session['step'] == 'collecting_payment':
            session['details']['utr_number'] = user_response

            # Retrieve details for booking
            booking_details = {
                "booking_ref": generate_unique_order_id(),  # Use the unique ID as reference
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
                        },
                        "additional_service": {
                            "Wheelchair": session['details'].get('wheelchair', False),
                            "Tour Guide": session['details'].get('tour_guide', False)
                        }
                    }
                ],
                "recipient_email": session['details']['email'],
                "utr_number": session['details']['utr_number']
            }

            # Generate ticket and send email
            try:
                attachment_path = generate_ticket(booking_details)
                send_email_with_pdf(
                    session['details']['email'],
                    "Your Museum Ticket",
                    f"Please find your museum ticket attached for {session['details']['museum']}. The total price is Rs {session['details']['total_price']:.2f}.",
                    attachment_path
                )
            except Exception as e:
                return jsonify({"response": f"Error generating or sending ticket: {e}"})

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

            # Reset booking session and switch back to normal chat mode
            del booking_sessions[session_id]

            response_message = (
                f"Your tickets for {session['details']['museum']} have been booked for Rs {session['details']['total_price']:.2f} "
                "and sent to your email! Your UTR number is recorded. "
                "You can now ask me about museum timings, ticket prices, or any other information!"
            )
            return jsonify({"response": response_message})

    # Handle cases where there's no active booking session, switch to normal chat mode
    return chat()

# Helper function to generate unique order ID
def generate_unique_order_id():
    """Generate a unique order ID for snacks booking."""
    return ''.join(random.choices(string.ascii_uppercase + string.digits, k=10))


if __name__ == '__main__':
    app.secret_key = os.urandom(24)  # Set a secret key for sessions
    app.run(debug=True)
