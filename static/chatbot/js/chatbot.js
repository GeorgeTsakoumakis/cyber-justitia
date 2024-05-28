let input = document.getElementById('user-input');

input.addEventListener('keydown', function (event) {
    if (event.key === 'Enter' && !event.shiftKey) {
        event.preventDefault();  // Prevent the default action
        sendMessage();
    } else if (event.key === 'Enter' && event.shiftKey) {
        // Shift + Enter pressed, insert a newline
        let cursorPosition = input.selectionStart;
        let value = input.value;
        input.value = value.slice(0, cursorPosition) + '\n' + value.slice(cursorPosition);
        input.selectionStart = input.selectionEnd = cursorPosition + 1;
        event.preventDefault();  // Prevent the default action (new line is already inserted)
        input.scrollTop = input.scrollHeight;
    }
});

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