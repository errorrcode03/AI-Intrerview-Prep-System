document.addEventListener('DOMContentLoaded', () => {
    const API_BASE = 'http://localhost:8000';
    const mockUserId = "test-user-123";
    
    // Default boilerplate code for Two Sum
    const defaultCodes = {
        '71': `def twoSum(nums, target):\n    # Write your code here\n    pass\n`,
        '54': `#include <bits/stdc++.h>\nusing namespace std;\n\nclass Solution {\npublic:\n    vector<int> twoSum(vector<int>& nums, int target) {\n        // Write your code here\n        return {};\n    }\n};`,
        '62': `class Solution {\n    public int[] twoSum(int[] nums, int target) {\n        // Write your code here\n        return new int[]{};\n    }\n}`,
        '63': `/**\n * @param {number[]} nums\n * @param {number} target\n * @return {number[]}\n */\nvar twoSum = function(nums, target) {\n    // Write your code here\n};`
    };

    const monacoMap = {
        '71': 'python',
        '54': 'cpp',
        '62': 'java',
        '63': 'javascript'
    };

    let editor = null;

    // Load Monaco Editor
    require.config({ paths: { 'vs': 'https://cdnjs.cloudflare.com/ajax/libs/monaco-editor/0.44.0/min/vs' }});
    require(['vs/editor/editor.main'], function() {
        editor = monaco.editor.create(document.getElementById('monaco-editor'), {
            value: defaultCodes['71'],
            language: 'python',
            theme: 'vs-dark',
            automaticLayout: true,
            minimap: { enabled: false },
            fontSize: 14,
            scrollBeyondLastLine: false
        });
    });

    const langSelect = document.getElementById('language-select');
    langSelect.addEventListener('change', (e) => {
        const langId = e.target.value;
        const monacoLang = monacoMap[langId];
        
        if (editor) {
            monaco.editor.setModelLanguage(editor.getModel(), monacoLang);
            // Only update value if they haven't typed much, or prompt them.
            // For simplicity in MVP, we just overwrite.
            editor.setValue(defaultCodes[langId]);
        }
    });

    const submitBtn = document.getElementById('submit-code-btn');
    submitBtn.addEventListener('click', async () => {
        if (!editor) return;
        
        const code = editor.getValue();
        const langId = parseInt(langSelect.value);
        const title = document.getElementById('problem-title').innerText;

        // UI updates
        submitBtn.disabled = true;
        submitBtn.textContent = 'Executing...';
        
        const feedbackPanel = document.getElementById('ai-feedback-panel');
        feedbackPanel.classList.remove('hidden');
        
        document.getElementById('feedback-status').className = 'feedback-status status-processing';
        document.getElementById('feedback-status').textContent = 'Executing and Analyzing...';
        document.getElementById('time-complexity').textContent = 'O(?)';
        document.getElementById('ai-critique').textContent = 'Gemini is reading your code...';
        document.getElementById('console-output-text').textContent = '...';

        try {
            const response = await fetch(`${API_BASE}/submit_code`, {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({
                    user_id: mockUserId,
                    question_title: title,
                    code: code,
                    language_id: langId
                })
            });

            if (!response.ok) throw new Error("Submission failed");

            const data = await response.json();
            
            // Update Status
            const statusEl = document.getElementById('feedback-status');
            statusEl.textContent = data.status;
            if (data.status.toLowerCase().includes('accept')) {
                statusEl.className = 'feedback-status status-accepted';
            } else {
                statusEl.className = 'feedback-status status-wrong';
            }

            // Update AI Feedback
            document.getElementById('time-complexity').textContent = data.time_complexity;
            document.getElementById('ai-critique').textContent = data.ai_feedback;
            document.getElementById('console-output-text').textContent = data.output || "No output.";

        } catch (error) {
            console.error(error);
            document.getElementById('feedback-status').textContent = 'Error executing code';
            document.getElementById('feedback-status').className = 'feedback-status status-wrong';
            document.getElementById('ai-critique').textContent = 'Failed to connect to backend.';
        } finally {
            submitBtn.disabled = false;
            submitBtn.textContent = 'Submit Code';
        }
    });

    const runBtn = document.getElementById('run-code-btn');
    runBtn.addEventListener('click', async () => {
        if (!editor) return;
        
        const code = editor.getValue();
        const langId = parseInt(langSelect.value);
        const title = document.getElementById('problem-title').innerText;

        runBtn.disabled = true;
        runBtn.textContent = 'Running...';
        
        const feedbackPanel = document.getElementById('ai-feedback-panel');
        feedbackPanel.classList.remove('hidden');
        
        document.getElementById('feedback-status').className = 'feedback-status status-processing';
        document.getElementById('feedback-status').textContent = 'Simulating Execution...';
        document.getElementById('time-complexity').textContent = '-';
        document.getElementById('ai-critique').textContent = 'Just running the code, no deep AI analysis.';
        document.getElementById('console-output-text').textContent = '...';

        try {
            const response = await fetch(`${API_BASE}/run_code`, {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({
                    question_title: title,
                    code: code,
                    language_id: langId
                })
            });

            if (!response.ok) throw new Error("Run failed");

            const data = await response.json();
            
            const statusEl = document.getElementById('feedback-status');
            statusEl.textContent = data.status;
            statusEl.className = data.status.toLowerCase().includes('error') ? 'feedback-status status-wrong' : 'feedback-status status-accepted';

            document.getElementById('console-output-text').textContent = data.output || "No output.";

        } catch (error) {
            console.error(error);
            document.getElementById('feedback-status').textContent = 'Error running code';
            document.getElementById('feedback-status').className = 'feedback-status status-wrong';
            document.getElementById('console-output-text').textContent = 'Failed to connect to backend.';
        } finally {
            runBtn.disabled = false;
            runBtn.textContent = 'Run Code';
        }
    });
});
