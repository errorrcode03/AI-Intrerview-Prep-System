document.addEventListener('DOMContentLoaded', async () => {
    const API_BASE = 'http://localhost:8000';
    const mockUserId = "test-user-123";

    try {
        const response = await fetch(`${API_BASE}/dashboard_stats/${mockUserId}`);
        if (!response.ok) throw new Error("Failed to fetch dashboard stats");
        
        const data = await response.json();

        // 1. Update Stat Cards
        document.getElementById('avg-score').textContent = data.average_score > 0 ? `${data.average_score}/10` : '--/10';
        document.getElementById('total-interviews').textContent = data.total_interviews;
        document.getElementById('total-coding').textContent = data.total_coding_attempts;

        // 2. Render Weak Topics (markdown-like lists formatting)
        const weakTopicsHtml = data.weak_topics
            .split('\n')
            .filter(line => line.trim() !== '')
            .map(line => {
                if (line.startsWith('*') || line.startsWith('-')) {
                    return `<li>${line.substring(1).trim()}</li>`;
                }
                return `<p>${line}</p>`;
            })
            .join('');
        
        document.getElementById('weak-topics').innerHTML = weakTopicsHtml.includes('<li>') 
            ? `<ul>${weakTopicsHtml}</ul>` 
            : weakTopicsHtml;

        // 3. Render Charts using Chart.js
        renderCharts(data.recent_scores, data.recent_coding_status);

    } catch (error) {
        console.error("Dashboard error:", error);
        document.getElementById('weak-topics').innerHTML = "<p class='status-wrong'>Failed to load data from backend. Make sure the server is running.</p>";
    }
});

function renderCharts(scores, codingStatuses) {
    // Shared chart styling
    Chart.defaults.color = '#94a3b8';
    Chart.defaults.font.family = "'Inter', sans-serif";
    
    // --- Scores Line Chart ---
    const ctxScores = document.getElementById('scoresChart').getContext('2d');
    
    // Generate mock labels (e.g., Q1, Q2)
    const scoreLabels = scores.map((_, i) => `Q${i + 1}`);
    
    new Chart(ctxScores, {
        type: 'line',
        data: {
            labels: scoreLabels.length ? scoreLabels : ['No Data'],
            datasets: [{
                label: 'Interview Score (out of 10)',
                data: scores.length ? scores : [0],
                borderColor: '#6366f1',
                backgroundColor: 'rgba(99, 102, 241, 0.1)',
                borderWidth: 2,
                tension: 0.4,
                fill: true,
                pointBackgroundColor: '#6366f1',
                pointRadius: 4
            }]
        },
        options: {
            responsive: true,
            scales: {
                y: {
                    beginAtZero: true,
                    max: 10,
                    grid: { color: 'rgba(255, 255, 255, 0.05)' }
                },
                x: {
                    grid: { display: false }
                }
            },
            plugins: {
                legend: { display: false }
            }
        }
    });

    // --- Coding Success Pie Chart ---
    const ctxCoding = document.getElementById('codingChart').getContext('2d');
    
    let accepted = 0;
    let failed = 0;
    
    codingStatuses.forEach(status => {
        if (status.toLowerCase().includes('accept') || status.toLowerCase().includes('executed')) {
            accepted++;
        } else {
            failed++;
        }
    });

    if (accepted === 0 && failed === 0) {
        accepted = 1; // Fake data for empty state shape
        failed = 0;
    }

    new Chart(ctxCoding, {
        type: 'doughnut',
        data: {
            labels: ['Success', 'Needs Work'],
            datasets: [{
                data: [accepted, failed],
                backgroundColor: ['#4ade80', '#ff5f56'],
                borderWidth: 0,
                hoverOffset: 4
            }]
        },
        options: {
            responsive: true,
            cutout: '75%',
            plugins: {
                legend: {
                    position: 'bottom',
                    labels: { padding: 20 }
                }
            }
        }
    });
}
