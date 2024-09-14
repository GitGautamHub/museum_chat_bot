document.addEventListener('DOMContentLoaded', () => {
    const chatBox = document.getElementById('chat-box');
    const chatInput = document.getElementById('chat-input');
    const sendBtn = document.getElementById('send-btn');
    const bookTicketBtn = document.getElementById('book-ticket-btn');

    let inBookingSession = false;  // Flag to track if the user is in a booking session

    sendBtn.addEventListener('click', () => sendMessage());

    chatInput.addEventListener('keypress', (event) => {
        if (event.key === 'Enter') {
            sendMessage();
        }
    });

    bookTicketBtn.addEventListener('click', () => {
        startTicketBooking();
    });

    function sendMessage() {
        const userMessage = chatInput.value.trim();
        if (userMessage) {
            appendMessage(userMessage, 'user-message');
            chatInput.value = '';

            const endpoint = inBookingSession ? '/continue-booking' : '/chat';  // Determine endpoint based on session state

            // Send message to backend
            fetch(endpoint, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({ message: userMessage }),
            })
            .then(response => response.json())
            .then(data => {
                appendMessage(data.response, 'bot-message');
                // If booking session ends, reset the flag
                if (data.response.includes('Your tickets have been booked')) {
                    inBookingSession = false;
                }
            })
            .catch(error => {
                console.error('Error:', error);
                appendMessage('Sorry, something went wrong. Please try again.', 'bot-message');
            });
        }
    }

    function appendMessage(message, className) {
        const messageElement = document.createElement('div');
        messageElement.className = `message ${className}`;
        
        let text = message;
        let imageUrl = null;
        
        // Check if message contains a link
        const httpIndex = message.indexOf('http');
        if (httpIndex !== -1) {
            text = message.substring(0, httpIndex); // Text before the link
            imageUrl = message.substring(httpIndex); // The link itself
        }
    
        // Add the text content
        const messageContent = document.createElement('div');
        messageContent.className = 'message-content';
        messageContent.textContent = text;
        messageElement.appendChild(messageContent);
    
        // If an image URL exists, append the image
        if (imageUrl) {
            const imageElement = document.createElement('img');
            imageElement.src = imageUrl;
            imageElement.className = 'mimg'; // Add any class for styling
            messageElement.appendChild(imageElement);
        }
    
        chatBox.appendChild(messageElement);
        chatBox.scrollTop = chatBox.scrollHeight;
    }
    

    function startTicketBooking() {
        appendMessage('Booking started. Please enter your name:', 'bot-message');
        fetch('/start-booking', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            }
        })
        .then(response => response.json())
        .then(data => {
            appendMessage(data.response, 'bot-message');
            inBookingSession = true;  // Set the booking session flag to true
        })
        .catch(error => {
            console.error('Error:', error);
            appendMessage('Sorry, something went wrong. Please try again.', 'bot-message');
        });
    }
});
