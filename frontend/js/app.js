document.addEventListener('DOMContentLoaded', () => {
    const dropZone = document.getElementById('drop-zone');
    const fileInput = document.getElementById('resume-upload');
    const uploadStatus = document.getElementById('upload-status');
    const resultCard = document.getElementById('analysis-result');
    const API_BASE = 'http://localhost:8000'; // FastAPI default port

    // Use authenticated user ID, redirect if not found for actions that require it
    let userId = localStorage.getItem('user_id');

    // Drag and drop handlers
    dropZone.addEventListener('dragover', (e) => {
        e.preventDefault();
        dropZone.classList.add('dragover');
    });

    dropZone.addEventListener('dragleave', () => {
        dropZone.classList.remove('dragover');
    });

    dropZone.addEventListener('drop', (e) => {
        e.preventDefault();
        dropZone.classList.remove('dragover');
        
        if (e.dataTransfer.files.length) {
            handleFile(e.dataTransfer.files[0]);
        }
    });

    fileInput.addEventListener('change', (e) => {
        if (e.target.files.length) {
            handleFile(e.target.files[0]);
        }
    });

    async function handleFile(file) {
        if (!file.name.endsWith('.pdf') && !file.name.endsWith('.docx')) {
            alert('Please upload a PDF or DOCX file.');
            return;
        }

        // UI update
        dropZone.classList.add('hidden');
        uploadStatus.classList.remove('hidden');
        resultCard.classList.add('hidden');

        const formData = new FormData();
        formData.append('file', file);
        // We append user_id as query param since it's defined that way in FastAPI
        
        if (!userId) {
            alert('Please login first to upload a resume.');
            window.location.href = 'login.html';
            return;
        }
        
        try {
            const response = await fetch(`${API_BASE}/upload_resume?user_id=${userId}`, {
                method: 'POST',
                body: formData
            });

            if (!response.ok) {
                throw new Error('Upload failed');
            }

            const data = await response.json();
            displayResult(data);
        } catch (error) {
            console.error('Error:', error);
            alert('An error occurred during upload. Is the backend running?');
            // Reset UI
            dropZone.classList.remove('hidden');
            uploadStatus.classList.add('hidden');
        }
    }

    function displayResult(data) {
        uploadStatus.classList.add('hidden');
        resultCard.classList.remove('hidden');
        
        let skillsHtml = '';
        if (data.skills && data.skills.length > 0) {
            skillsHtml = `
                <div style="margin-top: 1rem;">
                    <strong>Detected Skills:</strong>
                    <div style="display: flex; gap: 0.5rem; flex-wrap: wrap; margin-top: 0.5rem;">
                        ${data.skills.map(skill => `<span style="background: rgba(99, 102, 241, 0.2); padding: 0.25rem 0.75rem; border-radius: 99px; font-size: 0.85rem; color: #a5b4fc;">${skill}</span>`).join('')}
                    </div>
                </div>
            `;
        }

        resultCard.innerHTML = `
            <h3>Analysis Complete</h3>
            <p><strong>ATS Score:</strong> <span style="color: ${data.ats_score > 75 ? '#4ade80' : '#ffbd2e'}; font-size: 1.5rem; font-weight: bold;">${data.ats_score}%</span></p>
            ${skillsHtml}
            <button class="btn btn-primary" style="margin-top: 2rem; width: 100%;" onclick="startInterview()">Start HR Interview Round</button>
        `;
    }
});

// Navigate to the interview chat interface
function startInterview() {
    window.location.href = "interview.html";
}
