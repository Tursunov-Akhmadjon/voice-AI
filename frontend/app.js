const chatBox = document.getElementById('chat-box');
const userInput = document.getElementById('user-input');
const sendBtn = document.getElementById('send-btn');
const micBtn = document.getElementById('mic-btn');
const statusText = document.getElementById('status');

// Session management
let sessionId = localStorage.getItem('session_id');
let isAISpeaking = false; // Track if AI is currently speaking
let isCyrillic = false; // Toggle for Cyrillic TTS version

// Create session if not exists
if (!sessionId) {
    fetch('/api/session')
        .then(res => res.json())
        .then(data => {
            sessionId = data.session_id;
            localStorage.setItem('session_id', sessionId);
        });
}

// Voice Recognition Setup - Enhanced for better capture
const SpeechRecognition = window.SpeechRecognition || window.webkitSpeechRecognition;
let recognition = null;
let recognitionTimeout = null;

if (SpeechRecognition) {
    recognition = new SpeechRecognition();
    recognition.lang = 'uz-UZ';
    recognition.continuous = true; // Keep listening for complete sentence
    recognition.interimResults = true; // Show interim results
    recognition.maxAlternatives = 3; // Get better alternatives

    recognition.onstart = () => {
        micBtn.classList.add('listening');
        statusText.textContent = "Eshitilmoqda... Gapiring";
        // Auto-stop after 10 seconds of listening
        recognitionTimeout = setTimeout(() => {
            if (recognition) {
                recognition.stop();
            }
        }, 10000);
    };

    recognition.onend = () => {
        micBtn.classList.remove('listening');
        statusText.textContent = "";
        if (recognitionTimeout) {
            clearTimeout(recognitionTimeout);
        }
    };

    recognition.onresult = (event) => {
        const last = event.results.length - 1;
        const result = event.results[last];
        if (result.isFinal) {
            const transcript = result[0].transcript.trim();
            userInput.value = transcript;
            recognition.stop();
            setTimeout(() => sendMessage(), 300);
        } else {
            const interim = result[0].transcript;
            userInput.value = interim;
        }
    };

    recognition.onerror = (event) => {
        console.error("Speech recognition error", event.error);
        if (event.error === 'no-speech') {
            statusText.textContent = "Ovoz eshitilmadi. Qayta urinib ko'ring.";
        } else if (event.error === 'audio-capture') {
            statusText.textContent = "Mikrofon ishlamayapti.";
        } else {
            statusText.textContent = "Xatolik: " + event.error;
        }
        micBtn.classList.remove('listening');
        if (recognitionTimeout) {
            clearTimeout(recognitionTimeout);
        }
    };
} else {
    micBtn.style.display = 'none';
    console.warn("Web Speech API not supported");
}

// Text to Speech Setup
let selectedVoice = null;
function loadVoices() {
    const voices = window.speechSynthesis.getVoices();
    selectedVoice = voices.find(v => v.lang.includes('uz') && v.name.toLowerCase().includes('female')) ||
        voices.find(v => v.lang.includes('uz')) ||
        voices.find(v => v.lang.includes('ru') && v.name.toLowerCase().includes('female')) ||
        voices.find(v => v.name.toLowerCase().includes('female')) ||
        voices.find(v => v.lang.includes('ru')) ||
        voices[0];
    console.log('Selected voice:', selectedVoice?.name);
}
if (window.speechSynthesis) {
    loadVoices();
    window.speechSynthesis.onvoiceschanged = loadVoices;
}
// Global audio object for Assistant 2
let currentAudio = null;

function stopSpeaking() {
    // Stop Browser TTS (Assistant 1)
    if (window.speechSynthesis && isAISpeaking) {
        window.speechSynthesis.cancel();
    }

    // Stop Backend TTS (Assistant 2)
    if (currentAudio) {
        currentAudio.pause();
        currentAudio.currentTime = 0;
        currentAudio = null;
    }

    isAISpeaking = false;
    console.log('Speech interrupted by user');
}

async function sendMessage() {
    const text = userInput.value.trim();
    if (!text) return;

    // Stop any ongoing AI speech immediately
    stopSpeaking();

    addMessage(text, 'user');
    userInput.value = '';

    // Disable input during processing
    userInput.disabled = true;
    sendBtn.disabled = true;

    // Show loading
    const loadingMsg = addLoadingMessage();
    statusText.textContent = "Javob yozilmoqda...";

    // Get selected version
    const version = document.querySelector('input[name="assistant"]:checked').value;

    try {
        const response = await fetch('/chat', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({
                message: text,
                session_id: sessionId,
                version: parseInt(version)
            })
        });

        if (!response.ok) throw new Error('Network error');

        const data = await response.json();
        loadingMsg.remove();

        // Always display Latin text
        addMessage(data.response, 'ai');

        if (version == 1) {
            // Browser TTS
            speak(data.response);
        } else {
            // Backend TTS (Assistant 2)
            if (data.audio) {
                currentAudio = new Audio("data:audio/wav;base64," + data.audio);
                isAISpeaking = true;
                currentAudio.onended = () => {
                    isAISpeaking = false;
                    currentAudio = null;
                };
                currentAudio.play();
            } else {
                console.warn("No audio received for Assistant 2");
            }
        }

        if (data.cached) console.log('✅ Cache hit!');

    } catch (error) {
        console.error('Error:', error);
        loadingMsg.remove();
        addMessage("Uzr, xatolik yuz berdi. Qayta urinib ko'ring.", 'ai');
    } finally {
        statusText.textContent = "";
        userInput.disabled = false;
        sendBtn.disabled = false;
        userInput.focus();
    }
}

// Event Listeners
sendBtn.addEventListener('click', sendMessage);
userInput.addEventListener('keypress', (e) => { if (e.key === 'Enter') sendMessage(); });
userInput.addEventListener('input', () => { if (isAISpeaking) stopSpeaking(); });
micBtn.addEventListener('click', () => { if (recognition) { stopSpeaking(); recognition.start(); } });
function speak(text) {
    if (!window.speechSynthesis) return;
    window.speechSynthesis.cancel();
    const utterance = new SpeechSynthesisUtterance(text);
    if (selectedVoice) utterance.voice = selectedVoice;
    utterance.lang = 'uz-UZ';
    utterance.rate = 0.9;
    utterance.pitch = 1.1;
    utterance.volume = 1.0;
    utterance.onstart = () => { isAISpeaking = true; };
    utterance.onend = () => { isAISpeaking = false; };
    utterance.onerror = () => { isAISpeaking = false; };
    window.speechSynthesis.speak(utterance);
}

function addMessage(text, sender) {
    const msgDiv = document.createElement('div');
    msgDiv.classList.add('message', sender);
    const bubble = document.createElement('div');
    bubble.classList.add('bubble');
    bubble.textContent = text;
    msgDiv.appendChild(bubble);
    chatBox.appendChild(msgDiv);
    chatBox.scrollTop = chatBox.scrollHeight;
}
function addLoadingMessage() {
    const msgDiv = document.createElement('div');
    msgDiv.classList.add('message', 'ai', 'loading');
    const bubble = document.createElement('div');
    bubble.classList.add('bubble');
    bubble.innerHTML = '<span class="typing-indicator"><span></span><span></span><span></span></span>';
    msgDiv.appendChild(bubble);
    chatBox.appendChild(msgDiv);
    chatBox.scrollTop = chatBox.scrollHeight;
    return msgDiv;
}

// Version toggle (Assistant 1 vs Assistant 2)
const toggleContainer = document.createElement('div');
toggleContainer.style.display = 'flex';
toggleContainer.style.gap = '10px';
toggleContainer.style.marginBottom = '10px';
toggleContainer.style.alignItems = 'center';

const label1 = document.createElement('label');
label1.innerHTML = '<input type="radio" name="assistant" value="1" checked> Assistant 1 (Browser TTS)';
const label2 = document.createElement('label');
label2.innerHTML = '<input type="radio" name="assistant" value="2"> Assistant 2 (Facebook MMS)';

toggleContainer.appendChild(label1);
toggleContainer.appendChild(label2);

// Insert before chat box
chatBox.parentNode.insertBefore(toggleContainer, chatBox);

// Remove old toggle button if exists
const oldToggle = document.getElementById('toggle-version');
if (oldToggle) oldToggle.remove();

async function sendMessage() {
    const text = userInput.value.trim();
    if (!text) return;

    // Stop any ongoing AI speech immediately
    stopSpeaking();

    addMessage(text, 'user');
    userInput.value = '';

    // Disable input during processing
    userInput.disabled = true;
    sendBtn.disabled = true;

    // Show loading
    const loadingMsg = addLoadingMessage();
    statusText.textContent = "Javob yozilmoqda...";

    // Get selected version
    const version = document.querySelector('input[name="assistant"]:checked').value;

    try {
        const response = await fetch('/chat', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({
                message: text,
                session_id: sessionId,
                version: parseInt(version)
            })
        });

        if (!response.ok) throw new Error('Network error');

        const data = await response.json();
        loadingMsg.remove();

        // Always display Latin text
        addMessage(data.response, 'ai');

        if (version == 1) {
            // Browser TTS
            speak(data.response);
        } else {
            // Backend TTS (Assistant 2)
            if (data.audio) {
                const audio = new Audio("data:audio/wav;base64," + data.audio);
                isAISpeaking = true;
                audio.onended = () => { isAISpeaking = false; };
                audio.play();
            } else {
                console.warn("No audio received for Assistant 2");
            }
        }

        if (data.cached) console.log('✅ Cache hit!');

    } catch (error) {
        console.error('Error:', error);
        loadingMsg.remove();
        addMessage("Uzr, xatolik yuz berdi. Qayta urinib ko'ring.", 'ai');
    } finally {
        statusText.textContent = "";
        userInput.disabled = false;
        sendBtn.disabled = false;
        userInput.focus();
    }
}

// Event Listeners
sendBtn.addEventListener('click', sendMessage);
userInput.addEventListener('keypress', (e) => { if (e.key === 'Enter') sendMessage(); });
userInput.addEventListener('input', () => { if (isAISpeaking) stopSpeaking(); });
micBtn.addEventListener('click', () => { if (recognition) { stopSpeaking(); recognition.start(); } });
