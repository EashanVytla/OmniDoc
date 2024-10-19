document.getElementById('startRecording').addEventListener('click', function() {
    // Start audio recording
    console.log("Recording button clicked. Starting audio recording...");
    
    // Show recording animation (optional)
    const animationElement = document.getElementById("animationElement");
    animationElement.classList.remove("hidden");

    // Make an AJAX request to trigger the backend recording process
    fetch('/start-recording/', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
            'X-CSRFToken': getCookie('csrftoken') // Django CSRF token for security
        },
        body: JSON.stringify({
            action: 'start_recording'
        })
    })
    .then(response => response.json())
    .then(data => {
        console.log('Recording completed:', data);
        // Hide recording animation after recording is done
        animationElement.classList.add("hidden");

        // Show transcription in the UI (if available)
        const transcriptionDiv = document.getElementById('transcription');
        transcriptionDiv.textContent = data.transcription;
    })
    .catch(error => {
        console.error('Error:', error);
    });
});

// Helper function to get CSRF token for Django
function getCookie(name) {
    let cookieValue = null;
    if (document.cookie && document.cookie !== '') {
        const cookies = document.cookie.split(';');
        for (let i = 0; i < cookies.length; i++) {
            const cookie = cookies[i].trim();
            // Does this cookie string begin with the name we want?
            if (cookie.substring(0, name.length + 1) === (name + '=')) {
                cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
                break;
            }
        }
    }
    return cookieValue;
}
