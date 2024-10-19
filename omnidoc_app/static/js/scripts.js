let audioContext, recorder, microphone, analyser;
let isRecording = false;
let waveform;

document.getElementById('startRecording').addEventListener('click', startRecording);
document.getElementById('stopRecording').addEventListener('click', stopRecording);

async function startRecording() {
    console.log("started");
    audioContext = new AudioContext();
    analyser = audioContext.createAnalyser();
    const stream = await navigator.mediaDevices.getUserMedia({ audio: true });
    microphone = audioContext.createMediaStreamSource(stream);
    microphone.connect(analyser);

    recorder = new MediaRecorder(stream);
    recorder.start();

    let chunks = [];
    recorder.ondataavailable = event => chunks.push(event.data);
    recorder.onstop = async () => {
        const blob = new Blob(chunks, { type: 'audio/wav' });
        const formData = new FormData();
        formData.append('audio', blob);

        // Send audio to Django backend
        fetch('{% url "transcribe_audio" %}', {
            method: 'POST',
            body: formData,
            headers: { 'X-CSRFToken': '{{ csrf_token }}' }
        })
        .then(response => response.json())
        .then(data => {
            document.getElementById('transcription').innerText = data.transcription;
        });
    };

    // Start rendering the waveform
    startWaveformVisualization();

    startTalkingAnimation();
    isRecording = true;
}

function stopRecording() {
    console.log("stopped");
    if (isRecording) {
        recorder.stop();
        stopTalkingAnimation();
        stopWaveformVisualization();
        isRecording = false;
    }
}

function startTalkingAnimation() {
    document.getElementById('animationElement').classList.remove('hidden');
    document.getElementById('animationElement').classList.add('talking');
}

function stopTalkingAnimation() {
    document.getElementById('animationElement').classList.remove('talking');
    document.getElementById('animationElement').classList.add('hidden');
}

function startWaveformVisualization() {
    waveform = WaveSurfer.create({
        container: '#waveform',
        waveColor: 'violet',
        progressColor: 'purple',
        interact: false,  // Disable interaction with the waveform
        responsive: true,
        plugins: [
            WaveSurfer.microphone.create()
        ]
    });

    waveform.microphone.start();
}

function stopWaveformVisualization() {
    if (waveform && waveform.microphone) {
        waveform.microphone.stop();
        waveform.empty(); // Clear the waveform
    }
}
