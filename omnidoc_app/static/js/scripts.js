document.getElementById('startRecording').addEventListener('click', function() {
    console.log("Recording button clicked. Starting audio recording...");

    // Show recording animation (optional)
    const animationElement = document.getElementById("animationElement");
    animationElement.classList.remove("hidden");

    // Get the CSRF token from the meta tag
    let csrftoken = document.querySelector('meta[name="csrf-token"]')?.getAttribute('content');

    // If the meta tag is missing or CSRF token is not found, try getting it from the cookies
    if (!csrftoken) {
        csrftoken = getCookie('csrftoken');  // Fallback to cookie-based CSRF retrieval
    }

    // Check if the token exists
    if (!csrftoken) {
        console.error("CSRF token not found. Ensure it's correctly included in the HTML or cookies.");
        return;
    }

    // Make an AJAX request to trigger the backend recording process
    fetch('/start-recording/', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
            'X-CSRFToken': csrftoken // Django CSRF token for security
        },
        body: JSON.stringify({
            action: 'start_recording'
        })
    })
    .then(response => {
        if (!response.ok) {
            throw new Error('Network response was not ok');
        }
        return response.json();
    })
    .then(data => {
        console.log('Recording completed:', data);
        animationElement.classList.add("hidden");

        // Show transcription in the UI (if available)
        const transcriptionDiv = document.getElementById('transcription');
        transcriptionDiv.textContent = data.question;
    })
    .catch(error => {
        console.error('Error:', error);
        animationElement.classList.add("hidden");
    });
});

// Helper function to get CSRF token for Django
function getCookie(name) {
    let cookieValue = null;
    if (document.cookie && document.cookie !== '') {
        const cookies = document.cookie.split(';');
        for (let i = 0; i < cookies.length; i++) {
            const cookie = cookies[i].trim();
            if (cookie.substring(0, name.length + 1) === (name + '=')) {
                cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
                break;
            }
        }
    }
    return cookieValue;
}
