document.getElementById('user-input').onkeydown = function(e){
    if(e.keyCode === 13){
        sendMessage();
    }
};

// Function to send user message and display it in the chat
function sendMessage() {
    let userInput = document.getElementById("user-input").value;
    if (userInput.trim() !== "") {
        displayMessage(userInput, true); // Display user message
        // Send to backend for processing
        fetch('/chatbot/process/', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
                'X-CSRFToken': '{{ csrf_token }}'
            },
            body: JSON.stringify({ message: userInput })
        })
        .then(response => {
                return response.json();
        })
        .then(data => {
            displayMessage(data.response, false); // Display bot response
        })
        .catch(error => {
            console.error('Error:', error);
        });

        document.getElementById("user-input").value = ""; // Clear input field
    }
}

// Function to display messages in the chat container
function displayMessage(message, isUser) {
    let chatContainer = document.getElementById("chat-container");
    let chatMessages = document.getElementById("chat-messages");
    let messageElement;
    if (isUser) {
        messageElement = document.createElement("div");
    } else {
        messageElement = document.createElement("md-block");
    }
    messageElement.textContent = message;
    messageElement.classList.add('message');
    if (isUser) {
        messageElement.classList.add('user-message');
    } else {
        messageElement.classList.add('bot-message');
    }

    chatMessages.appendChild(messageElement);
    chatContainer.scrollTop = chatContainer.scrollHeight;
}