# chatbot/model.py
import json
import numpy as np
from sklearn.preprocessing import LabelEncoder
from tensorflow.keras.models import Sequential
from tensorflow.keras.layers import Dense, Dropout
from tensorflow.keras.optimizers import SGD
import nltk
from nltk.stem import WordNetLemmatizer
import pickle  # Add this to save the words and classes

# Download necessary NLTK data
nltk.download('punkt')
nltk.download('wordnet')

# Load intents with UTF-8 encoding
lemmatizer = WordNetLemmatizer()
with open('chatbot/intents.json', encoding='utf-8') as file:
    intents = json.load(file)

# Initialize data structures
words = []
classes = []
documents = []
ignore_letters = ['!', '?', ',', '.']

# Preparing data
for intent in intents['intents']:
    for pattern in intent['patterns']:
        word_list = nltk.word_tokenize(pattern)
        words.extend(word_list)
        documents.append((word_list, intent['tag']))
    if intent['tag'] not in classes:
        classes.append(intent['tag'])

# Lemmatize and sort words
words = [lemmatizer.lemmatize(w.lower()) for w in words if w not in ignore_letters]
words = sorted(set(words))
classes = sorted(set(classes))

# Preparing training data
training = []
output_empty = [0] * len(classes)

for document in documents:
    bag = []
    word_patterns = document[0]
    word_patterns = [lemmatizer.lemmatize(word.lower()) for word in word_patterns]
    
    # Creating bag of words
    for word in words:
        bag.append(1) if word in word_patterns else bag.append(0)

    # Creating output row
    output_row = list(output_empty)
    output_row[classes.index(document[1])] = 1

    training.append([bag, output_row])

# Separate the data into features (X) and labels (Y)
train_x = np.array([entry[0] for entry in training])  # Features
train_y = np.array([entry[1] for entry in training])  # Labels

# Build the model
model = Sequential()
model.add(Dense(128, input_shape=(len(train_x[0]),), activation='relu'))
model.add(Dropout(0.5))
model.add(Dense(64, activation='relu'))
model.add(Dropout(0.5))
model.add(Dense(len(train_y[0]), activation='softmax'))

# Compile the model
sgd = SGD(learning_rate=0.01, decay=1e-6, momentum=0.9, nesterov=True)
model.compile(loss='categorical_crossentropy', optimizer=sgd, metrics=['accuracy'])

# Train the model with increased epochs
model.fit(train_x, train_y, epochs=300, batch_size=5, verbose=1)  # Increased epochs
model.save('chatbot/chatbot_model.h5')

# Save the words and classes for use in prediction
with open('chatbot/words.pkl', 'wb') as f:
    pickle.dump(words, f)
with open('chatbot/classes.pkl', 'wb') as f:
    pickle.dump(classes, f)

print("Model trained and saved as chatbot_model.h5")
