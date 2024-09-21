# chatbot/nlp_utils.py
import nltk
import numpy as np
from tensorflow.keras.models import load_model
from nltk.stem import WordNetLemmatizer
import json
import pickle

lemmatizer = WordNetLemmatizer()

# Function to load language-specific models and data
def load_language_model(language_code):
    try:
        # Ensure the file path is correct, considering the current working directory
        model_path = f'chatbot/models/{language_code}_model.h5'
        model = load_model(model_path)
        print(f"[INFO] {language_code} model loaded successfully.")
    except Exception as e:
        print(f"[ERROR] Error loading {language_code} model: {e}")
        return None, None, None

    try:
        intents_path = f'chatbot/intents/{language_code}/intents_{language_code}.json'
        with open(intents_path, encoding='utf-8') as file:
            intents = json.load(file)
        print(f"[INFO] {language_code} intents loaded successfully.")
    except Exception as e:
        print(f"[ERROR] Error loading {language_code} intents: {e}")
        return None, None, None

    try:
        words_path = f'chatbot/models/words_{language_code}_model.pkl'
        classes_path = f'chatbot/models/classes_{language_code}_model.pkl'
        with open(words_path, 'rb') as f:
            words = pickle.load(f)
        with open(classes_path, 'rb') as f:
            classes = pickle.load(f)
        print(f"[INFO] {language_code} words and classes loaded successfully.")
    except Exception as e:
        print(f"[ERROR] Error loading {language_code} words or classes: {e}")
        return None, None, None

    return model, words, classes

# Preprocess user input
def clean_up_sentence(sentence):
    sentence_words = nltk.word_tokenize(sentence)
    sentence_words = [lemmatizer.lemmatize(word.lower()) for word in sentence_words]
    return sentence_words

# Convert sentence into bag of words representation
def bag_of_words(sentence, words):
    sentence_words = clean_up_sentence(sentence)
    bag = [0] * len(words)
    for s in sentence_words:
        for i, w in enumerate(words):
            if w == s:
                bag[i] = 1
    return np.array(bag)

# Predict intent using the model
def predict_class(sentence, language_code):
    model, words, classes = load_language_model(language_code)
    if not model:
        return []
    try:
        bow = bag_of_words(sentence, words)
        print(f"[DEBUG] Bag of words for input '{sentence}': {bow}")  # Debugging line
        res = model.predict(np.array([bow]))[0]
        print(f"[DEBUG] Raw model predictions for '{sentence}': {res}")  # Debugging line
        ERROR_THRESHOLD = 0.10
        results = [[i, r] for i, r in enumerate(res) if r > ERROR_THRESHOLD]
        results.sort(key=lambda x: x[1], reverse=True)
        print(f"[DEBUG] Filtered prediction results: {results}")  # Debugging line
        return_list = []
        for r in results:
            return_list.append({"intent": classes[r[0]], "probability": str(r[1])})
        print(f"[DEBUG] Predicted intents: {return_list}")  # Debugging line
        return return_list
    except Exception as e:
        print(f"[ERROR] Error predicting class: {e}")
        return []

# Get response based on predicted intent
def get_response(intents_list, language_code):
    model, _, _ = load_language_model(language_code)
    if intents_list:
        tag = intents_list[0]['intent']
        print(f"[DEBUG] Detected intent: {tag}")  # Debugging line
        with open(f'chatbot/intents/{language_code}/intents_{language_code}.json', encoding='utf-8') as file:
            intents = json.load(file)
        for i in intents['intents']:
            if i['tag'] == tag:
                response = np.random.choice(i['responses'])
                print(f"[DEBUG] Selected response for intent '{tag}': {response}")  # Debugging line
                return response
    print("[DEBUG] Fallback response: I'm not sure how to respond to that.")  # Debugging line
    return "Sorry, I can't assist you with that."
