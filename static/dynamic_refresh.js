// Does away with the need to reload the page when messages have been submitted

var computerName = window.computerName;
var userName = window.userName;
var sourceName = window.sourceName;
var csrfToken = document.querySelector('meta[name="csrf-token"]').getAttribute('content');
console.log(`The sourceName is ${sourceName}`)
console.log(`The user is ${userName}`);

const form = document.querySelector("form")
const inputBox = document.querySelector("input[name='message']")
const chatContainer = document.getElementById("chat-container")
const submitButton = document.getElementById("send-btn")
console.log("Hello from this script")

// Add event listener to the form
submitButton.addEventListener("click", (event) => {
    console.log("button clicked")
    event.preventDefault();

    const message = inputBox.value;
    console.log(message)
    console.log("Form submitted");

    fetch(`/${sourceName}-send-message/`, {
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
        return fetch(`/${sourceName}-send-response/`, {
            method: "POST",
            body: JSON.stringify({ content: message }),
            headers: { "Content-Type": "application/json"},
        })
    })
    .then ((response) => {
        return response.json();
    })
    .then ((data) => {
        const messageElement = document.createElement("div");
        messageElement.className = data[0].role === "user" ? "message-user" : "message-computer";
        messageElement.innerText = `${data[0].role === "user" ? userName + ": " : computerName + ": "}${data[0].content}`;
        chatContainer.appendChild(messageElement);
    })
    .catch((error) => {
        console.error(error)
    })

    // Clear the input field
    inputBox.value = ''
});