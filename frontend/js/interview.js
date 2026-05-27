document.addEventListener('DOMContentLoaded', () => {
    const API_BASE = 'http://localhost:8000';
    const mockUserId = "test-user-123"; // In a real app, this comes from auth
    
    let currentInterviewId = null;
    let currentDialogueId = null;

    const chatHistory = document.getElementById('chat-history');
    const chatForm = document.getElementById('chat-form');
    const answerInput = document.getElementById('answer-input');
    const submitBtn = document.getElementById('submit-btn');
    const speakBtn = document.getElementById('speak-btn');
    const feedbackToast = document.getElementById('feedback-toast');
    const scoreBadge = document.getElementById('score-badge');
    const feedbackText = document.getElementById('feedback-text');

    // Initialize Interview on page load
    startInterview();

    async function startInterview() {
        try {
            const response = await fetch(`${API_BASE}/start_interview`, {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({
                    user_id: mockUserId,
                    interview_type: "HR"
                })
            });

            if (!response.ok) throw new Error("Failed to start interview");
            
            const data = await response.json();
            currentInterviewId = data.interview_id;
            currentDialogueId = data.first_dialogue_id;

            // Clear loading message and append AI question
            chatHistory.innerHTML = '';
            appendMessage('ai', data.question);

        } catch (error) {
            console.error(error);
            chatHistory.innerHTML = `<div class="message system-message" style="color: #ff5f56;">Error connecting to server. Is the backend running?</div>`;
        }
    }

    chatForm.addEventListener('submit', async (e) => {
        e.preventDefault();
        
        const answer = answerInput.value.trim();
        if (!answer || !currentDialogueId) return;

        // Display user answer
        appendMessage('user', answer);
        answerInput.value = '';
        answerInput.disabled = true;
        submitBtn.disabled = true;
        
        // Hide previous feedback
        feedbackToast.classList.add('hidden');

        // Show typing indicator
        const typingId = appendTypingIndicator();

        try {
            const response = await fetch(`${API_BASE}/submit_answer`, {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({
                    dialogue_id: currentDialogueId,
                    answer_text: answer
                })
            });

            if (!response.ok) throw new Error("Failed to submit answer");

            const data = await response.json();
            
            // Remove typing indicator
            document.getElementById(typingId).remove();

            // Show Feedback
            showFeedback(data.score, data.feedback);

            // Update state
            currentDialogueId = data.next_dialogue_id;

            // Append next question
            appendMessage('ai', data.next_question);

        } catch (error) {
            console.error(error);
            document.getElementById(typingId).remove();
            appendMessage('system', 'Error processing answer. Please try again.');
        } finally {
            answerInput.disabled = false;
            submitBtn.disabled = false;
            answerInput.focus();
        }
    });

    function appendMessage(sender, text) {
        const div = document.createElement('div');
        div.className = `message ${sender}-message`;
        div.textContent = text;
        chatHistory.appendChild(div);
        scrollToBottom();

        // Read AI response aloud
        if (sender === 'ai') {
            speakText(text);
        }
    }

    // --- Web Speech API (Free Voice Features) ---

    // 1. Text to Speech (AI Voice)
    function speakText(text) {
        if (!('speechSynthesis' in window)) return;
        
        // Stop any currently playing audio
        window.speechSynthesis.cancel();
        
        const utterance = new SpeechSynthesisUtterance(text);
        utterance.rate = 1.0; 
        utterance.pitch = 1.0;
        
        // Try to pick an English voice
        const voices = window.speechSynthesis.getVoices();
        const preferredVoice = voices.find(v => v.lang.includes('en-US') || v.lang.includes('en-GB'));
        if (preferredVoice) {
            utterance.voice = preferredVoice;
        }
        
        window.speechSynthesis.speak(utterance);
    }

    // Load voices ASAP since it can be async
    if ('speechSynthesis' in window) {
        window.speechSynthesis.onvoiceschanged = () => window.speechSynthesis.getVoices();
    }

    // 2. Speech to Text (Microphone)
    let recognition;
    let isRecording = false;

    if ('webkitSpeechRecognition' in window || 'SpeechRecognition' in window) {
        const SpeechRecognition = window.SpeechRecognition || window.webkitSpeechRecognition;
        recognition = new SpeechRecognition();
        recognition.continuous = true;
        recognition.interimResults = true;
        recognition.lang = 'en-US';

        recognition.onresult = (event) => {
            let interimTranscript = '';
            let finalTranscript = '';

            for (let i = event.resultIndex; i < event.results.length; ++i) {
                if (event.results[i].isFinal) {
                    finalTranscript += event.results[i][0].transcript;
                } else {
                    interimTranscript += event.results[i][0].transcript;
                }
            }

            // Append final transcripts and show interim
            if (finalTranscript) {
                answerInput.value += finalTranscript + ' ';
            }
        };

        recognition.onerror = (event) => {
            console.error('Speech recognition error:', event.error);
            stopRecording();
        };

        recognition.onend = () => {
            stopRecording();
        };
    }

    speakBtn.addEventListener('click', () => {
        if (!recognition) {
            alert('Speech recognition is not supported in this browser. Please use Chrome or Edge.');
            return;
        }

        if (isRecording) {
            stopRecording();
        } else {
            startRecording();
        }
    });

    function startRecording() {
        isRecording = true;
        speakBtn.textContent = '🛑 Stop Recording';
        speakBtn.style.backgroundColor = '#ff5f56';
        speakBtn.style.color = 'white';
        recognition.start();
    }

    function stopRecording() {
        isRecording = false;
        speakBtn.textContent = '🎤 Speak';
        speakBtn.style.backgroundColor = '';
        speakBtn.style.color = '';
        if (recognition) {
            recognition.stop();
        }
    }
    
    // ------------------------------------------

    function appendTypingIndicator() {
        const id = 'typing-' + Date.now();
        const div = document.createElement('div');
        div.id = id;
        div.className = 'message system-message';
        div.innerHTML = `<div class="spinner small-spinner"></div> AI is analyzing and writing...`;
        chatHistory.appendChild(div);
        scrollToBottom();
        return id;
    }

    function showFeedback(score, feedback) {
        scoreBadge.textContent = `${score}/10`;
        feedbackText.textContent = feedback;
        
        if (score >= 7) {
            feedbackToast.classList.remove('warning');
        } else {
            feedbackToast.classList.add('warning');
        }
        
        feedbackToast.classList.remove('hidden');
    }

    function scrollToBottom() {
        chatHistory.scrollTop = chatHistory.scrollHeight;
    }
});
