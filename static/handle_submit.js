$(document).ready(function() {
    const computerName = window.computerName || 'Computer';
    const userName = window.userName || 'User';
    const chat_id = window.chat_id || 'default_chat_id';
    const csrfToken = document.querySelector('meta[name="csrf-token"]').getAttribute('content');

    $('#message-form').on('submit', function(event) {
        event.preventDefault();

        var messageInput = $('#message-input');
        var messageText = messageInput.val().trim();

        if (messageText === '') {
            return;
        }

        // Perform AJAX request to submit the user's message
        $.ajax({
            // The URL where the form data should be sent, defined in the form's action attribute
            // In this case, it's chat-send-message
            url: $(this).attr('action'),
            type: 'POST',
            data: {
                'message': messageText,
                'csrfmiddlewaretoken': csrfToken
            },
            success: function(userResponse) {
                $('#messages').append(
                    `<div class="message-user">
                        ${userName}: ${messageText} <span class="timestamp">${new Date().toLocaleString()}</span>
                    </div>`
                );

                messageInput.val(''); // Clear the message field
                $('#messages').scrollTo($('#messages')[0].scrollHeight); // Scroll to the bottom of the chat window (broken)

                // Perform AJAX request to get a response from the agent
                $.ajax({
                    url: `/chat-send-response/${chat_id}/`, // URL to send the message and get the agent's response
                    type: 'POST',
                    data: {
                        'message': messageText,
                        'csrfmiddlewaretoken': csrfToken
                    },
                    success: function(botResponse) {
                        // Append the bot's message to the chat window
                        $('#messages').append(
                            `<div class="message-computer">
                                ${computerName}: ${botResponse.content.output} <span class="timestamp">${botResponse.timestamp}</span>
                            </div>`
                        );

                        $('#messages').scrollTo($('#messages')[0].scrollHeight); // Scroll tot he bottom of the chat window
                    },
                    error: function(xhr, status, error) {
                        console.error('Bot response failed:', error);
                        console.log('Response:', xhr.responseText);
                    }
                });
            },
            error: function(xhr, status, error) {
                console.error('Message submission failed:', error);
                console.log('Response:', xhr.responseText);
            }
        });
    });
});