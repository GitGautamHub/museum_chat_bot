# chatbot/nlp_utils.py
import nltk
import numpy as np
from tensorflow.keras.models import load_model
from nltk.stem import WordNetLemmatizer
import json
import pickle

lemmatizer = WordNetLemmatizer()

# Load model
try:
    model = load_model('chatbot/chatbot_model.h5')
    print("[INFO] Model loaded successfully.")
except Exception as e:
    print(f"[ERROR] Error loading model: {e}")

# Load intents with UTF-8 encoding
try:
    with open('chatbot/intents.json', encoding='utf-8') as file:
        intents = json.load(file)
    print("[INFO] Intents loaded successfully.")
except Exception as e:
    print(f"[ERROR] Error loading intents.json: {e}")

# Load words and classes
with open('chatbot/words.pkl', 'rb') as f:
    words = pickle.load(f)
with open('chatbot/classes.pkl', 'rb') as f:
    classes = pickle.load(f)

def clean_up_sentence(sentence):
    sentence_words = nltk.word_tokenize(sentence)
    sentence_words = [lemmatizer.lemmatize(word.lower()) for word in sentence_words]
    return sentence_words

def bag_of_words(sentence, words):
    sentence_words = clean_up_sentence(sentence)
    bag = [0] * len(words)
    for s in sentence_words:
        for i, w in enumerate(words):
            if w == s:
                bag[i] = 1
    return np.array(bag)

def predict_class(sentence):
    try:
        bow = bag_of_words(sentence, words)
        print(f"[DEBUG] Bag of words for input '{sentence}': {bow}")  # Debugging line
        res = model.predict(np.array([bow]))[0]
        print(f"[DEBUG] Raw model predictions for '{sentence}': {res}")  # Debugging line
        ERROR_THRESHOLD = 0.10  # Lowered threshold to catch more intents
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

def get_response(intents_list, intents_json):
    if intents_list:
        tag = intents_list[0]['intent']
        print(f"[DEBUG] Detected intent: {tag}")  # Debugging line
        for i in intents_json['intents']:
            if i['tag'] == tag:
                response = np.random.choice(i['responses'])
                print(f"[DEBUG] Selected response for intent '{tag}': {response}")  # Debugging line
                return response
    print("[DEBUG] Fallback response: I'm not sure how to respond to that.")  # Debugging line
    return "I'm not sure how to respond to that."
