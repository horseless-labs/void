document.addEventListener("DOMContentLoaded", function () {
    const computerName = window.computerName;
    const userName = window.userName;
    const sourceName = window.sourceName;
    const chat_id = window.chat_id;
    const csrfToken = document.querySelector('meta[name="csrf-token"]').getAttribute('content');

    const form = document.querySelector("form");
    const inputBox = document.querySelector("input[name='message']");
    const chatContainer = document.getElementById("chat-container");

    // Function to scroll the chat container to the bottom
    function scrollToBottom() {
        chatContainer.scrollTop = chatContainer.scrollHeight;
    }

    // Add event listener to the form
    form.addEventListener("submit", (event) => {
        event.preventDefault();  // Prevent the default form submission behavior

        const message = inputBox.value.trim();
        if (!message) return;

        // Clear the input field immediately
        inputBox.value = '';

        // Display user message instantly
        const userMessageElement = document.createElement("div");
        userMessageElement.className = "message-user";
        userMessageElement.innerText = `${userName}: ${message}`;
        chatContainer.appendChild(userMessageElement);
        scrollToBottom();  // Scroll to the bottom right after adding the message

        // Send user message to the server
        fetch(`/${sourceName}-send-message/${chat_id}`, {
            method: "POST",
            body: JSON.stringify({ content: message }),
            headers: { "X-CSRFToken": csrfToken, "Content-Type": "application/json" },
        })
        .then(response => response.json())
        .then(data => {
            // Send bot response
            return fetch(`/${sourceName}-send-response/${chat_id}`, {
                method: "POST",
                body: JSON.stringify({ content: message }),
                headers: { "X-CSRFToken": csrfToken, "Content-Type": "application/json" },
            });
        })
        .then(response => response.json())
        .then(data => {
            // Display bot response
            const botMessageElement = document.createElement("div");
            botMessageElement.className = "message-computer";
            botMessageElement.innerText = `${computerName}: ${data[0].content}`;
            chatContainer.appendChild(botMessageElement);

            // Scroll to the bottom after adding the bot message
            scrollToBottom();
        })
        .catch(error => console.error(error));
    });

    // Ensure the chat container is always scrolled to the bottom on load
    scrollToBottom();
});
