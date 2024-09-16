# MuseumSEVA: Dwarpal - Your Gateway to India's Museums

Dwarpal is a virtual assistant designed to help users explore and book tickets for museums across India. This application uses a chatbot interface built with Flask, integrated with a machine learning model for natural language processing and ticket generation features using FPDF and barcode libraries.

## Features

- Chatbot interface for museum information and ticket booking.
- Multi-language support with intent recognition for both English and Hindi.
- Dynamic ticket generation in PDF format with barcodes.
- Seamless email integration to send tickets directly to users.
- MongoDB for managing bookings and user data.

## Tech Stack

- **Backend**: Python, Flask
- **ML & NLP**: TensorFlow, NLTK, Scikit-learn
- **Database**: MongoDB (PyMongo)
- **PDF & Barcode**: FPDF, Python-Barcode, Pillow
- **Email Service**: Yagmail (SMTP with Gmail)
- **Web Server**: Gunicorn for production

## Prerequisites

- **Python 3.12** installed on your system.
- **MongoDB** running locally or accessible via a connection URI.
- **Gmail Account** with app-specific password enabled (for sending emails).

## Getting Started

Follow these steps to set up and run the project on your local machine.

### 1. Clone the Repository

```bash
git clone <repository_url>
cd <repository_name>
```
### 2. Set Up a Virtual Environment

Create and activate a virtual environment:

```bash
python -m venv venv
# Activate the environment
# On Windows
venv\Scripts\activate
# On macOS/Linux
source venv/bin/activate
```

### 3. Install Dependencies

Install all the required Python packages using requirements.txt:

```bash
Copy code
pip install -r requirements.txt
```

### 4. Configure Environment Variables
Create a .env file in the root directory of your project and add your Gmail app password:

```bash
GMAIL_APP_PASSWORD=your_gmail_app_password
```
Replace your_gmail_app_password with your actual Gmail app-specific password. This is necessary for the email functionality to work correctly.

### 5. Set Up MongoDB
Ensure that MongoDB is running on your machine or accessible via a URI. By default, the application connects to a local MongoDB instance at mongodb://localhost:27017/. If your setup differs, update the MongoDB connection URI in the db.py file or wherever the MongoDB client is instantiated.

### 6. Train the Chatbot Model (If Not Pre-trained)
If the chatbot model is not pre-trained, you need to train it using the provided data and scripts:

```bash
python chatbot/model.py
```
This script will train the model using the defined intents and save the model along with required data files (chatbot_model.h5, words.pkl, classes.pkl) in the chatbot directory.

### 7. Run the Application
To run the application locally using Flask's development server, use:

```bash
flask run
```
Alternatively, for a production environment, use Gunicorn with multiple workers for better performance:

```bash
gunicorn -w 4 app:app
```
This command starts the app with 4 worker processes, which you can adjust based on your server's capabilities.

### 8. Access the Application
Open your web browser and navigate to:

```bash
http://127.0.0.1:5000/
```
Here, you can interact with the chatbot, explore museum details, and book tickets directly.

## Project Structure
#### app.py: Main application file that defines the routes and integrates the chatbot with booking functionalities.
#### chatbot/: Contains all chatbot-related files, including the NLP model, intents, utility scripts, and training data.
#### tickets/: Scripts for generating tickets in PDF format and handling email operations.
#### static/: Contains CSS, JavaScript, and image assets for the front end.
#### templates/: HTML templates used by Flask to render the web pages.
#### db/: MongoDB connection and database models for managing bookings and user data.

### Contributing
If you wish to contribute to Dwarpal, please follow these steps:

- Fork the repository.
- Create a new branch (git checkout -b feature-branch).
- Make your changes and commit them (git commit -m 'Add new feature').
- Push your changes to the branch (git push origin feature-branch).
- Open a pull request with a detailed description of your changes.

#### Troubleshooting
- Dependencies Issues: Ensure your virtual environment is activated when installing dependencies and running the application.
- MongoDB Connection: Verify that MongoDB is running and accessible at the URI specified in your configuration. Check  connection strings and firewall settings if necessary.
- Email Sending: If emails are not being sent, check that your Gmail app-specific password is correctly set in the .env file. - - Ensure that less secure apps are allowed or the correct security settings are enabled for SMTP.