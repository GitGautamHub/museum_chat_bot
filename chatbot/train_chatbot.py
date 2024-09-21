from train_model import train_model  # Importing from train_model.py

if __name__ == "__main__":
    print("Training the chatbot models...")
    # Training models for different languages
    train_model('chatbot/intents/hindi/intents_hindi.json', 'hindi_model')
    train_model('chatbot/intents/english/intents_english.json', 'english_model')
    train_model('chatbot/intents/bengali/intents_bengali.json', 'bengali_model')
    train_model('chatbot/intents/marathi/intents_marathi.json', 'marathi_model')
