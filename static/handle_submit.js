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

        $.ajax({
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

                messageInput.val('');
                $('#messages').scrollTop($('#messages')[0].scrollHeight);

                $.ajax({
                    url: `/chat-send-response/${chat_id}/`,
                    type: 'POST',
                    data: {
                        'message': messageText,
                        'csrfmiddlewaretoken': csrfToken
                    },
                    success: function(botResponse) {
                        $('#messages').append(
                            `<div class="message-computer">
                                ${computerName}: ${botResponse.content.output} <span class="timestamp">${botResponse.timestamp}</span>
                            </div>`
                        );

                        $('#messages').scrollTop($('#messages')[0].scrollHeight);
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
