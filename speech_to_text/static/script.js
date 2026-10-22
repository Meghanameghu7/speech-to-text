const startBtn = document.getElementById("startBtn");
const stopBtn = document.getElementById("stopBtn");
const transcription = document.getElementById("transcription");
const message = document.getElementById("message");
const saveBtn = document.getElementById("saveBtn");

const SpeechRecognition =
window.SpeechRecognition || window.webkitSpeechRecognition;

let recognition;

if (SpeechRecognition) {
recognition = new SpeechRecognition();
recognition.continuous = true;
recognition.interimResults = true;
recognition.lang = "en-IN";

recognition.onresult = function (event) {
    let text = "";

    for (let i = 0; i < event.results.length; i++) {
        text += event.results[i][0].transcript + " ";
    }

    transcription.value = text.trim();
};

recognition.onerror = function () {
    message.textContent = "Speech recognition error. Please try again.";
};

startBtn.onclick = function () {
    recognition.start();
    message.textContent = "Listening... Please speak.";
};

stopBtn.onclick = function () {
    recognition.stop();
    message.textContent = "Recording stopped.";
};

} else {
message.textContent = "Please use Google Chrome for speech recognition.";
}

saveBtn.onclick = async function () {
const text = transcription.value.trim();

if (!text) {
    message.textContent = "Please enter or speak some text first.";
    return;
}

try {
    const response = await fetch("/save", {
        method: "POST",
        headers: {
            "Content-Type": "application/json"
        },
        body: JSON.stringify({ text: text })
    });

    const result = await response.json();
    message.textContent = result.message;
} catch (error) {
    message.textContent = "Could not connect to the server.";
}

};