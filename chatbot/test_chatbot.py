# test_chatbot.py
import requests

# Define the endpoint for the chatbot
CHATBOT_URL = 'http://127.0.0.1:5000/chat'  # Adjust if your Flask server is running on a different port

# Test cases: a list of dictionaries with 'input' and 'expected' keys
test_cases = [
    {
        'input': 'Hi',
        'expected': [
            'Hello!', 
            'Hi there!', 
            'Greetings!', 
            'How can I assist you today?',
            "Greetings! I'm Musebot 🤖, your virtual assistant for the National Museum. How may I help you today?"
        ]
    },
    {
        'input': 'Tell me about the museum',
        'expected': ['The National Museum, New Delhi, began with a blueprint prepared by the Maurice Gwyer Committee in May 1946. It houses over 200,000 objects, covering a time span of over five thousand years of Indian cultural heritage.']
    },
    {
        'input': 'book a ticket',
        'expected': ['To book tickets for the National Museum, you can pre-book online via our official website or contact us directly. Pre-booking is required for school visits and can be done by emailing yuvasaathi.nm@gmail.com at least 7 days in advance.']
    },
    {
        'input': 'What snacks are available?',
        'expected': ['The National Museum offers a variety of snacks that can be pre-booked along with your visit. Available snacks include Sandwiches (Veg/Non-Veg), Samosas, Fresh Fruit Juice, Biscuits and Cookies, and Tea and Coffee.']
    },
    {
        'input': 'Where is the museum located?',
        'expected': ['The National Museum is located at Janpath, New Delhi - 110011. It is easily accessible via the Central Secretariat and Udyog Bhawan metro stations. Nearby bus stops include National Museum and Nirman Bhawan with routes 505, 521, 522, and others servicing the area.']
    }
]

def test_chatbot():
    success = 0
    failed = 0

    for i, case in enumerate(test_cases):
        response = requests.post(CHATBOT_URL, json={'message': case['input']})
        response_data = response.json()
        bot_response = response_data.get('response', '')

        # Check if the bot response matches any of the expected responses
        if bot_response in case['expected']:
            print(f"Test case {i + 1} PASSED: Input: '{case['input']}' - Response: '{bot_response}'")
            success += 1
        else:
            print(f"Test case {i + 1} FAILED: Input: '{case['input']}' - Expected: {case['expected']} - Got: '{bot_response}'")
            failed += 1

    print(f"\nTesting completed: {success} passed, {failed} failed.")

if __name__ == "__main__":
    test_chatbot()
