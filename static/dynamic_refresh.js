// Does away with the need to reload the page when messages have been submitted

var computerName = window.computerName;
var userName = window.userName;
var sourceName = window.sourceName;
var chat_id = window.chat_id;
var csrfToken = document.querySelector('meta[name="csrf-token"]').getAttribute('content');
console.log(`The sourceName is ${sourceName}`)
console.log(`The user is ${userName}`);

const form = document.querySelector("form")
// const form = document.getElementById("message-form")
const inputBox = document.querySelector("input[name='message']")
// const inputBox = document.getElementById("message-input")
const chatContainer = document.getElementById("chat-container")
const submitButton = document.getElementById("send-btn")
// const submitButton = form.querySelector("button[type='submit'")
console.log("Hello from this script")

// Add event listener to the form
submitButton.addEventListener("click", (event) => {
    console.log("button clicked")
    event.preventDefault();

    const message = inputBox.value;
    console.log(message)
    console.log("Form submitted");

    fetch(`/${sourceName}-send-message/${chat_id}`, {
        method: "POST",
        body: JSON.stringify({ content: message }),
        headers: { "X-CSRFToken": csrfToken, "Content-Type": "application/json"},
    })
    .then((response) => response.json())
    .then((data) => {
        console.log(data);
        // Could be neater, but whatever. 
        const messageElement = document.createElement("div");
        messageElement.className = data.role === "user" ? "message-user" : "message-computer";
        messageElement.innerText = `${data.role === "user" ? userName + ": " : computerName + ": "}${data.content}`;
        chatContainer.appendChild(messageElement);
    })    
    .then(() => {
        return fetch(`/${sourceName}-send-response/${chat_id}`, {
            method: "POST",
            body: JSON.stringify({ content: message }),
            headers: { "X-CSRFToken": csrfToken, "Content-Type": "application/json"},
        })
    })
    .then ((response) => {
        return response.json();
    })
    .then ((data) => {
        const messageElement = document.createElement("div");
        messageElement.className = data.role === "user" ? "message-user" : "message-computer";
        messageElement.innerText = `${data.role === "user" ? userName + ": " : computerName + ": "}${data[0].content}`;
        chatContainer.appendChild(messageElement);
    })
    .catch((error) => {
        console.error(error)
    })

    // Clear the input field
    inputBox.value = ''
});