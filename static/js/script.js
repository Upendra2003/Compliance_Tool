function sendPolicyId(policyId) {
    console.log(`\n=== FRONTEND: Starting compliance check for policy ID: ${policyId} ===`);

    // Get all provider cards and add loading state to clicked one
    const cards = document.querySelectorAll('.provider-card');
    cards.forEach((card, index) => {
        if (index + 1 === policyId) {
            card.classList.add('loading');
        } else {
            card.style.opacity = '0.5';
            card.style.pointerEvents = 'none';
        }
    });

    // Show progress modal
    showProgressModal();

    console.log("FRONTEND: Initializing compliance check session...");
    const startTime = performance.now();

    // Step 1: Get session ID
    fetch("/send_number", {
        method: "POST",
        headers: {
            "Content-Type": "application/json"
        },
        body: JSON.stringify({ number: policyId })
    })
    .then(response => response.json())
    .then(data => {
        const sessionId = data.session_id;
        console.log("FRONTEND: Session ID received:", sessionId);

        // Step 2: Connect to SSE for progress updates
        const eventSource = new EventSource(`/progress/${sessionId}`);

        eventSource.onmessage = function(event) {
            const update = JSON.parse(event.data);
            console.log("FRONTEND: Progress update:", update);

            if (update.type === 'connected') {
                console.log("FRONTEND: SSE connection established");
                updateProgress('Connected to server, starting checks...', 'processing');
            } else if (update.type === 'category_start') {
                updateProgress(`Checking ${update.data.category}...`, 'checking');
            } else if (update.type === 'category_complete') {
                updateProgress(`${update.data.category} completed ✓`, 'completed');
            } else if (update.type === 'status') {
                updateProgress(update.data.message, 'processing');
            } else if (update.type === 'complete') {
                const endTime = performance.now();
                console.log(`FRONTEND: Processing completed in ${((endTime - startTime) / 1000).toFixed(2)} seconds`);

                updateProgress('All checks completed! Loading report...', 'completed');
                eventSource.close();

                // Small delay to show final message
                setTimeout(() => {
                    navigateToReport(update.data.scoring_data, update.data.provider);
                }, 500);
            } else if (update.type === 'error') {
                console.error("FRONTEND: Server error:", update.data.message);
                eventSource.close();
                hideProgressModal();
                alert(`Processing error: ${update.data.message}`);

                // Reset loading states
                cards.forEach(card => {
                    card.classList.remove('loading');
                    card.style.opacity = '1';
                    card.style.pointerEvents = 'auto';
                });
            }
        };

        eventSource.onerror = function(error) {
            console.error("FRONTEND: SSE connection error:", error);
            console.log("FRONTEND: EventSource readyState:", eventSource.readyState);

            // Only show error if connection actually failed (not just closed after completion)
            if (eventSource.readyState === EventSource.CLOSED) {
                console.log("FRONTEND: SSE connection closed");
                // Don't show error alert - might be normal completion
            } else {
                eventSource.close();
                hideProgressModal();
                alert("Connection error. Please try again.");

                // Reset loading states
                cards.forEach(card => {
                    card.classList.remove('loading');
                    card.style.opacity = '1';
                    card.style.pointerEvents = 'auto';
                });
            }
        };

        // Step 3: Start the actual check process
        fetch("/run_checks", {
            method: "POST",
            headers: {
                "Content-Type": "application/json"
            },
            body: JSON.stringify({
                session_id: sessionId,
                policy_id: policyId
            })
        })
        .catch(error => {
            console.error("FRONTEND: Error starting checks:", error);
            eventSource.close();
            hideProgressModal();
            alert("Failed to start compliance check. Please try again.");

            cards.forEach(card => {
                card.classList.remove('loading');
                card.style.opacity = '1';
                card.style.pointerEvents = 'auto';
            });
        });
    })
    .catch(error => {
        const endTime = performance.now();
        console.error(`FRONTEND: Error after ${((endTime - startTime) / 1000).toFixed(2)} seconds`);
        console.error("FRONTEND: Error details:", error);
        hideProgressModal();
        alert("Failed to load compliance report. Please try again.");

        cards.forEach(card => {
            card.classList.remove('loading');
            card.style.opacity = '1';
            card.style.pointerEvents = 'auto';
        });
    });
}

function showProgressModal() {
    const modal = document.createElement('div');
    modal.id = 'progress-modal';
    modal.innerHTML = `
        <div class="progress-modal-overlay">
            <div class="progress-modal-content">
                <h2>Running DPDP Compliance Checks</h2>
                <div class="progress-timer">
                    <span class="timer-label">Elapsed Time:</span>
                    <span id="timer-display">0:00</span>
                </div>
                <div id="progress-messages"></div>
                <div class="progress-spinner"></div>
            </div>
        </div>
    `;
    document.body.appendChild(modal);

    // Start the timer
    startTimer();
}

function hideProgressModal() {
    stopTimer();
    const modal = document.getElementById('progress-modal');
    if (modal) {
        modal.remove();
    }
}

function updateProgress(message, status) {
    const messagesDiv = document.getElementById('progress-messages');
    if (!messagesDiv) return;

    const messageEl = document.createElement('div');
    messageEl.className = `progress-message progress-${status}`;
    messageEl.textContent = message;

    messagesDiv.appendChild(messageEl);

    // Auto-scroll to latest message
    messagesDiv.scrollTop = messagesDiv.scrollHeight;
}

function navigateToReport(scoringData, provider) {
    // Stop the timer before navigating
    stopTimer();

    // Store data in sessionStorage
    sessionStorage.setItem('scoringData', JSON.stringify(scoringData));
    sessionStorage.setItem('provider', provider);

    // Navigate to report page
    window.location.href = '/report';
}

// Timer functionality
let timerInterval = null;
let timerStartTime = null;

function startTimer() {
    timerStartTime = Date.now();
    const timerDisplay = document.getElementById('timer-display');

    if (!timerDisplay) return;

    timerInterval = setInterval(() => {
        const elapsed = Math.floor((Date.now() - timerStartTime) / 1000);
        const minutes = Math.floor(elapsed / 60);
        const seconds = elapsed % 60;
        timerDisplay.textContent = `${minutes}:${seconds.toString().padStart(2, '0')}`;
    }, 1000);
}

function stopTimer() {
    if (timerInterval) {
        clearInterval(timerInterval);
        timerInterval = null;
    }
}
