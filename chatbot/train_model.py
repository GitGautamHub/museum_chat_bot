import json
import numpy as np
from sklearn.preprocessing import LabelEncoder
from tensorflow.keras.models import Sequential
from tensorflow.keras.layers import Dense, Dropout
from tensorflow.keras.optimizers import SGD
from tensorflow.keras.callbacks import EarlyStopping, ReduceLROnPlateau  # Import necessary callbacks
import nltk
from nltk.stem import WordNetLemmatizer
import pickle
import os

# Download necessary NLTK data
nltk.download('punkt')
nltk.download('wordnet')

# Function to train the model for a specific language
def train_model(intents_file, model_name):
    lemmatizer = WordNetLemmatizer()

    with open(intents_file, encoding='utf-8') as file:
        intents = json.load(file)

    words = []
    classes = []
    documents = []
    ignore_letters = ['!', '?', ',', '.']

    for intent in intents['intents']:
        for pattern in intent['patterns']:
            word_list = nltk.word_tokenize(pattern)
            words.extend(word_list)
            documents.append((word_list, intent['tag']))
        if intent['tag'] not in classes:
            classes.append(intent['tag'])

    words = [lemmatizer.lemmatize(w.lower()) for w in words if w not in ignore_letters]
    words = sorted(set(words))
    classes = sorted(set(classes))

    training = []
    output_empty = [0] * len(classes)

    for document in documents:
        bag = []
        word_patterns = document[0]
        word_patterns = [lemmatizer.lemmatize(word.lower()) for word in word_patterns]

        for word in words:
            bag.append(1) if word in word_patterns else bag.append(0)

        output_row = list(output_empty)
        output_row[classes.index(document[1])] = 1

        training.append([bag, output_row])

    train_x = np.array([entry[0] for entry in training])
    train_y = np.array([entry[1] for entry in training])

    model = Sequential()
    model.add(Dense(256, input_shape=(len(train_x[0]),), activation='relu'))  # Increased units
    model.add(Dropout(0.7))
    model.add(Dense(128, activation='relu'))  # Increased units
    model.add(Dropout(0.5))
    model.add(Dense(len(train_y[0]), activation='softmax'))

    sgd = SGD(learning_rate=0.01, momentum=0.9, nesterov=True)  # Removed 'decay' parameter
    model.compile(loss='categorical_crossentropy', optimizer=sgd, metrics=['accuracy'])

    # Callbacks
    callbacks = [
        EarlyStopping(monitor='loss', patience=10, restore_best_weights=True),
        ReduceLROnPlateau(monitor='loss', factor=0.2, patience=5, min_lr=0.0001)
    ]

    # Updated epochs and batch size
    model.fit(train_x, train_y, epochs=300, batch_size=64, verbose=1, callbacks=callbacks)

    # Save model and related files with the language-specific name
    if not os.path.exists('chatbot/models'):
        os.makedirs('chatbot/models')
        
    model.save(f'chatbot/models/{model_name}.h5')

    # Save words and classes as pickle files
    with open(f'chatbot/models/words_{model_name}.pkl', 'wb') as f:
        pickle.dump(words, f)
        print(f"[INFO] words_{model_name}.pkl saved successfully.")
    with open(f'chatbot/models/classes_{model_name}.pkl', 'wb') as f:
        pickle.dump(classes, f)
        print(f"[INFO] classes_{model_name}.pkl saved successfully.")

    print(f"Model trained and saved as {model_name}.h5")


if __name__ == "__main__":
    # Example usage: train_model for Hindi, English, Bengali, and Marathi
    train_model('chatbot/intents/hindi/intents_hindi.json', 'hindi_model')
    train_model('chatbot/intents/english/intents_english.json', 'english_model')
    train_model('chatbot/intents/bengali/intents_bengali.json', 'bengali_model')
    train_model('chatbot/intents/marathi/intents_marathi.json', 'marathi_model')
