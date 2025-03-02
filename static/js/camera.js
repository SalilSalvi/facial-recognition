document.addEventListener('DOMContentLoaded', () => {
    const video = document.getElementById('webcam');
    const canvas = document.getElementById('canvas');
    const authButton = document.getElementById('authenticate');
    const statusMessage = document.getElementById('status');
    const loadingIndicator = document.getElementById('loading');
    
    let stream = null;
    
    // Initialize webcam
    async function initCamera() {
        try {
            stream = await navigator.mediaDevices.getUserMedia({
                video: { 
                    facingMode: 'user',
                    width: { ideal: 640 },
                    height: { ideal: 480 }
                },
                audio: false
            });
            
            video.srcObject = stream;
            showMessage('Camera initialized. Click the Authenticate button when ready.', 'info');
            authButton.disabled = false;
            
        } catch (err) {
            console.error('Error accessing camera:', err);
            showMessage('Unable to access camera. Please ensure you have given camera permissions.', 'error');
        }
    }
    
    // Start camera when page loads
    initCamera();
    
    // Authenticate button handler
    authButton.addEventListener('click', async () => {
        if (!stream) {
            showMessage('Camera not initialized. Please refresh and try again.', 'error');
            return;
        }
        
        try {
            showLoading(true);
            
            // Capture frame from webcam
            canvas.width = video.videoWidth;
            canvas.height = video.videoHeight;
            const ctx = canvas.getContext('2d');
            ctx.drawImage(video, 0, 0, canvas.width, canvas.height);
            
            // Get the image data as base64
            const imageData = canvas.toDataURL('image/jpeg');
            
            // Send to server for verification - using /verify endpoint
            const response = await fetch('/verify', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify({ image: imageData })
            });
            
            const result = await response.json();
            
            if (result.success) {
                if (result.authenticated) {
                    showMessage(`Welcome, ${result.name}! Redirecting...`, 'success');
                    
                    // Redirect to content page after successful authentication
                    setTimeout(() => {
                        window.location.href = '/content';
                    }, 1500);
                } else {
                    showMessage('Authentication failed. Face not recognized.', 'error');
                }
            } else {
                showMessage(`Error: ${result.error}`, 'error');
            }
            
        } catch (err) {
            console.error('Authentication error:', err);
            showMessage('Authentication process failed. Please try again.', 'error');
        } finally {
            showLoading(false);
        }
    });
    
    // Helper functions
    function showMessage(message, type) {
        statusMessage.textContent = message;
        statusMessage.className = `status-message ${type}`;
        statusMessage.classList.remove('hidden');
        
        // Hide message after some time for non-error messages
        if (type !== 'error') {
            setTimeout(() => {
                statusMessage.classList.add('hidden');
            }, 5000);
        }
    }
    
    function showLoading(show) {
        if (show) {
            loadingIndicator.classList.remove('hidden');
            authButton.disabled = true;
        } else {
            loadingIndicator.classList.add('hidden');
            authButton.disabled = false;
        }
    }
    
    // Cleanup on page unload
    window.addEventListener('beforeunload', () => {
        if (stream) {
            stream.getTracks().forEach(track => track.stop());
        }
    });
});