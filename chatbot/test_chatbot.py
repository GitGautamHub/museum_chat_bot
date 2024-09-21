import requests

# Define the endpoint for the chatbot
CHATBOT_URL = 'http://127.0.0.1:5000/chat'  # Adjust if your Flask server is running on a different port

# Test cases for different languages
test_cases = {
    'english': [
        {'input': 'Hi', 'expected': ['Hello!', 'Hi there!', 'Greetings!', 'How can I assist you today?']},
        {'input': 'Tell me about the museum', 'expected': ['The National Museum, New Delhi, began with a blueprint prepared by the Maurice Gwyer Committee in May 1946.']}
    ],
    'hindi': [
        {'input': 'नमस्ते', 'expected': ['नमस्ते! मैं द्वारपाल हूँ, भारत के विभिन्न संग्रहालयों की जानकारी देने और टिकट बुक करने में आपकी सहायता करने के लिए हूँ।']},
        {'input': 'संग्रहालय के बारे में बताएं', 'expected': ['क्या आप दिल्ली, कोलकाता, मुंबई या किसी अन्य शहर के संग्रहालय के बारे में जानना चाहेंगे?']}
    ],
    'bengali': [
        # Add Bengali test cases here
    ],
    'marathi': [
        # Add Marathi test cases here
    ]
}

def test_chatbot(language_code):
    success = 0
    failed = 0

    for i, case in enumerate(test_cases[language_code]):
        response = requests.post(CHATBOT_URL, json={'message': case['input'], 'language_code': language_code})
        response_data = response.json()
        bot_response = response_data.get('response', '')

        if bot_response in case['expected']:
            print(f"Test case {i + 1} PASSED: Input: '{case['input']}' - Response: '{bot_response}'")
            success += 1
        else:
            print(f"Test case {i + 1} FAILED: Input: '{case['input']}' - Expected: {case['expected']} - Got: '{bot_response}'")
            print(f"[DEBUG] Full Response Data: {response_data}")  # Additional debug information
            failed += 1

    print(f"\nTesting for {language_code} completed: {success} passed, {failed} failed.")

if __name__ == "__main__":
    # Test chatbot for each language
    for language in ['english', 'hindi', 'bengali', 'marathi']:
        print(f"\nTesting chatbot in {language.upper()} language...")
        test_chatbot(language)
