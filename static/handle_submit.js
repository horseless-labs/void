document.addEventListener('DOMContentLoaded', function() {
    const form = document.getElementById('message-form');
    const textarea = document.getElementById('message-input');

    form.addEventListener('submit', function(event) {
        event.preventDefault(); // Prevent the default form submission
        const formData = new FormData(form);

        // Clear the textarea immediately
        textarea.value = '';

        // Submit the form using Fetch API
        fetch(form.action, {
            method: 'POST',
            body: formData,
            headers: {
                'X-CSRFToken': document.querySelector('[name=csrfmiddlewaretoken]').value
            }
        })
        .then(response => response.json())
        .then(data => {
            // Handle the response if needed
            console.log('Success:', data);
        })
        .catch(error => {
            // Handle errors if needed
            console.error('Error:', error);
        });
    });

    textarea.addEventListener('keydown', function(event) {
        if (event.key === 'Enter') {
            event.preventDefault(); // Prevent the default action of adding a new line
            form.requestSubmit(); // Trigger form submission programmatically
        }
    });
});
