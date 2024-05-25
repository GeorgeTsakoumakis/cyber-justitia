document.getElementById('user-input').onkeydown = function(e){
    if(e.keyCode === 13){
        sendMessage();
    }
};

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
