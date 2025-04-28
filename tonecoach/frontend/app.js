document.addEventListener('DOMContentLoaded', () => {
    // DOM Elements
    const recordButton = document.getElementById('recordButton');
    const stopButton = document.getElementById('stopButton');
    const downloadButton = document.getElementById('downloadButton');
    const improveButton = document.getElementById('improveButton');
    const compareSpeechButton = document.getElementById('compareSpeechButton');
    const audioVisualizer = document.getElementById('audioVisualizer');
    const analysisContainer = document.getElementById('analysisContainer');
    const loadingIndicator = document.getElementById('loadingIndicator');
    const toggleSettings = document.getElementById('toggleSettings');
    const settingsContent = document.getElementById('settingsContent');
    const themeToggle = document.getElementById('themeToggle');
    const analysisLevel = document.getElementById('analysisLevel');
    const voiceCloning = document.getElementById('voiceCloning');
    const waveformRadio = document.getElementById('waveform');
    const frequencyBarsRadio = document.getElementById('frequencyBars');
    
    // Make sure loading indicator is hidden on page load
    if (loadingIndicator) {
        loadingIndicator.classList.add('hidden');
    }
    
    // Canvas context for visualizer
    const canvasCtx = audioVisualizer.getContext('2d');
    
    // Audio context and variables
    let audioContext;
    let mediaRecorder;
    let audioChunks = [];
    let audioBlob;
    let audioUrl;
    let analyser;
    let dataArray;
    let bufferLength;
    let recordingStartTime;
    let animationFrame;
    let visualizationType = 'waveform';
    
    // Initialize canvas
    initializeCanvas();
    
    // Initialize empty visualizer
    drawEmptyVisualizer();
    
    // Settings toggle
    toggleSettings.addEventListener('click', () => {
        settingsContent.classList.toggle('hidden');
        toggleSettings.querySelector('i').classList.toggle('fa-chevron-down');
        toggleSettings.querySelector('i').classList.toggle('fa-chevron-up');
    });
    
    // Theme toggle
    themeToggle.addEventListener('click', () => {
        document.body.classList.toggle('dark-theme');
        themeToggle.querySelector('i').classList.toggle('fa-moon');
        themeToggle.querySelector('i').classList.toggle('fa-sun');
    });
    
    // Visualization type selection
    waveformRadio.addEventListener('change', () => {
        visualizationType = 'waveform';
        if (analyser) {
            cancelAnimationFrame(animationFrame);
            drawVisualizer();
        } else {
            drawEmptyVisualizer();
        }
    });
    
    frequencyBarsRadio.addEventListener('change', () => {
        visualizationType = 'frequencyBars';
        if (analyser) {
            cancelAnimationFrame(animationFrame);
            drawVisualizer();
        } else {
            drawEmptyVisualizer();
        }
    });
    
    // Ensure the canvas fills its container
    function initializeCanvas() {
        const container = audioVisualizer.parentElement;
        audioVisualizer.width = container.clientWidth - 40; // Adjust for padding
        audioVisualizer.height = container.clientHeight - 40;
    }
    
    // Call resize on window resize
    window.addEventListener('resize', () => {
        initializeCanvas();
        if (analyser) {
            cancelAnimationFrame(animationFrame);
            drawVisualizer();
        } else {
            drawEmptyVisualizer();
        }
    });
    
    // Draw empty visualizer
    function drawEmptyVisualizer() {
        canvasCtx.fillStyle = 'rgb(255, 255, 255)';
        canvasCtx.fillRect(0, 0, audioVisualizer.width, audioVisualizer.height);
        
        // Draw a flat line for empty visualizer
        canvasCtx.lineWidth = 2;
        canvasCtx.strokeStyle = 'rgb(222, 226, 230)';
        canvasCtx.beginPath();
        const y = audioVisualizer.height / 2;
        canvasCtx.moveTo(0, y);
        canvasCtx.lineTo(audioVisualizer.width, y);
        canvasCtx.stroke();
        
        // Add text
        canvasCtx.font = '14px Poppins, sans-serif';
        canvasCtx.fillStyle = 'rgb(173, 181, 189)';
        canvasCtx.textAlign = 'center';
        canvasCtx.fillText('Click "Start Recording" to begin', audioVisualizer.width / 2, y - 20);
    }
    
    // Initialize audio visualizer
    function initVisualizer(stream) {
        audioContext = new (window.AudioContext || window.webkitAudioContext)();
        const source = audioContext.createMediaStreamSource(stream);
        analyser = audioContext.createAnalyser();
        analyser.fftSize = 2048;
        bufferLength = analyser.frequencyBinCount;
        dataArray = new Uint8Array(bufferLength);
        source.connect(analyser);
        
        // Start drawing visualizer
        drawVisualizer();
    }
    
    // Draw audio visualizer based on selected type
    function drawVisualizer() {
        if (visualizationType === 'waveform') {
            drawWaveform();
        } else {
            drawFrequencyBars();
        }
    }
    
    // Draw waveform visualization
    function drawWaveform() {
        animationFrame = requestAnimationFrame(drawWaveform);
        
        analyser.getByteTimeDomainData(dataArray);
        
        canvasCtx.fillStyle = 'rgb(255, 255, 255)';
        canvasCtx.fillRect(0, 0, audioVisualizer.width, audioVisualizer.height);
        
        canvasCtx.lineWidth = 2;
        canvasCtx.strokeStyle = 'rgb(58, 134, 255)';
        canvasCtx.beginPath();
        
        const sliceWidth = audioVisualizer.width / bufferLength;
        let x = 0;
        
        for (let i = 0; i < bufferLength; i++) {
            const v = dataArray[i] / 128.0;
            const y = v * audioVisualizer.height / 2;
            
            if (i === 0) {
                canvasCtx.moveTo(x, y);
            } else {
                canvasCtx.lineTo(x, y);
            }
            
            x += sliceWidth;
        }
        
        canvasCtx.lineTo(audioVisualizer.width, audioVisualizer.height / 2);
        canvasCtx.stroke();
    }
    
    // Draw frequency bars visualization
    function drawFrequencyBars() {
        animationFrame = requestAnimationFrame(drawFrequencyBars);
        
        analyser.getByteFrequencyData(dataArray);
        
        canvasCtx.fillStyle = 'rgb(255, 255, 255)';
        canvasCtx.fillRect(0, 0, audioVisualizer.width, audioVisualizer.height);
        
        const barWidth = (audioVisualizer.width / bufferLength) * 2.5;
        let barHeight;
        let x = 0;
        
        for (let i = 0; i < bufferLength; i++) {
            barHeight = dataArray[i] / 2;
            
            const gradient = canvasCtx.createLinearGradient(0, audioVisualizer.height - barHeight, 0, audioVisualizer.height);
            gradient.addColorStop(0, 'rgb(58, 134, 255)');
            gradient.addColorStop(1, 'rgb(131, 56, 236)');
            
            canvasCtx.fillStyle = gradient;
            canvasCtx.fillRect(x, audioVisualizer.height - barHeight, barWidth, barHeight);
            
            x += barWidth + 1;
        }
    }
    
    // Initialize speech pattern chart
    // Initialize speech pattern chart
    function initSpeechPatternChart(data) {
        if (!document.getElementById('speechPatternChart')) {
            console.error('Speech pattern chart canvas not found');
            return;
        }
        
        const ctx = document.getElementById('speechPatternChart').getContext('2d');
        
        // Safe way to destroy existing chart
        if (window.speechPatternChart instanceof Chart) {
            window.speechPatternChart.destroy();
        }
        
        // Create default data if none provided
        if (!data) {
            data = {
                labels: Array.from({length: 10}, (_, i) => i + 1),
                pitchData: Array.from({length: 10}, () => 0),
                energyData: Array.from({length: 10}, () => 0)
            };
        }
        
        try {
            window.speechPatternChart = new Chart(ctx, {
                type: 'line',
                data: {
                    labels: data.labels,
                    datasets: [
                        {
                            label: 'Pitch',
                            data: data.pitchData,
                            borderColor: 'rgb(58, 134, 255)',
                            backgroundColor: 'rgba(58, 134, 255, 0.1)',
                            tension: 0.4,
                            fill: true
                        },
                        {
                            label: 'Energy',
                            data: data.energyData,
                            borderColor: 'rgb(131, 56, 236)',
                            backgroundColor: 'rgba(131, 56, 236, 0.1)',
                            tension: 0.4,
                            fill: true
                        }
                    ]
                },
                options: {
                    responsive: true,
                    maintainAspectRatio: false,
                    plugins: {
                        legend: {
                            position: 'top',
                        },
                        tooltip: {
                            mode: 'index',
                            intersect: false
                        }
                    },
                    scales: {
                        y: {
                            beginAtZero: true
                        }
                    }
                }
            });
        } catch (error) {
            console.error("Error initializing chart:", error);
            // If chart initialization fails, don't block the UI
            loadingIndicator.classList.add('hidden');
        }
    }
    
    // Start recording function
    async function startRecording() {
        try {
            const stream = await navigator.mediaDevices.getUserMedia({ audio: true });
            
            // Initialize the audio visualizer
            initVisualizer(stream);
            
            // Set up the media recorder
            mediaRecorder = new MediaRecorder(stream);
            audioChunks = [];
            
            mediaRecorder.ondataavailable = (event) => {
                audioChunks.push(event.data);
            };
            
            mediaRecorder.onstop = async () => {
                // Create audio blob from chunks
                audioBlob = new Blob(audioChunks, { type: 'audio/wav' });
                audioUrl = URL.createObjectURL(audioBlob);
                
                // Enable download button
                downloadButton.disabled = false;
                
                // Show loading indicator
                loadingIndicator.classList.remove('hidden');
                
                // Get selected analysis level
                const level = analysisLevel.value;
                
                // Analyze speech based on selected level
                if (level === 'basic') {
                    // Basic analysis (client-side only)
                    const recordingDuration = (Date.now() - recordingStartTime) / 1000;
                    displayBasicAnalysis(recordingDuration);
                    loadingIndicator.classList.add('hidden');
                } else {
                    // Detailed or advanced analysis (backend API)
                    await analyzeAudio(audioBlob, level);
                    loadingIndicator.classList.add('hidden');
                }
                
                // Show analysis results
                analysisContainer.classList.remove('hidden');
                
                // Enable "Hear Improved Version" button if voice cloning is enabled
                if (voiceCloning.checked) {
                    improveButton.disabled = false;
                    compareSpeechButton.disabled = false;
                }
            };
            
            // Start recording
            recordingStartTime = Date.now();
            mediaRecorder.start();
            
            // Update UI
            recordButton.disabled = true;
            stopButton.disabled = false;
            
        } catch (error) {
            console.error('Error starting recording:', error);
            alert('Could not access the microphone. Please ensure you have granted permission.');
        }
    }
    
    // Stop recording function
    function stopRecording() {
        if (mediaRecorder && mediaRecorder.state !== 'inactive') {
            mediaRecorder.stop();
            mediaRecorder.stream.getTracks().forEach(track => track.stop());
            
            // Cancel visualization animation frame
            if (animationFrame) {
                cancelAnimationFrame(animationFrame);
            }
            
            // Update UI
            recordButton.disabled = false;
            stopButton.disabled = true;
        }
    }
    
    // Download recording function
    function downloadRecording() {
        if (audioUrl) {
            const downloadLink = document.createElement('a');
            downloadLink.href = audioUrl;
            downloadLink.download = 'tonecoach_recording.wav';
            downloadLink.click();
        }
    }
    
    // Analyze audio with backend API
    // Analyze audio with backend API
    async function analyzeAudio(audioBlob, level) {
        try {
            // Create form data with audio file
            const formData = new FormData();
            formData.append('audio', audioBlob, 'recording.wav');
            formData.append('level', level);
            
            console.log("Sending audio for analysis...");
            
            // Add a timeout to the fetch request
            const controller = new AbortController();
            const timeoutId = setTimeout(() => controller.abort(), 30000); // 30-second timeout
            
            // Send to backend for analysis
            const response = await fetch('http://localhost:5000/analyze', {
                method: 'POST',
                body: formData,
                signal: controller.signal,
                // Explicitly disable credentials to avoid CORS preflight issues
                credentials: 'omit',
                mode: 'cors'
            });
            
            clearTimeout(timeoutId); // Clear the timeout
            
            console.log("Response received:", response.status);
            
            if (!response.ok) {
                const errorText = await response.text();
                console.error("Server error response:", errorText);
                throw new Error(`Server error: ${response.status}`);
            }
            
            const analysisData = await response.json();
            console.log("Analysis data received:", analysisData);
            displayAnalysisResults(analysisData);
            
        } catch (error) {
            console.error('Error analyzing audio:', error);
            
            // If API fails, still show basic analysis
            const recordingDuration = (Date.now() - recordingStartTime) / 1000;
            displayBasicAnalysis(recordingDuration);
            
            // Hide loading indicator in case of error
            loadingIndicator.classList.add('hidden');
        }
    }
    
    // Display analysis results from API
    function displayAnalysisResults(data) {
        // Update metrics
        document.getElementById('duration').textContent = formatTime(data.duration);
        document.getElementById('speakingRate').textContent = `${Math.round(data.speaking_rate)} WPM`;
        document.getElementById('pitchVariation').textContent = data.pitch_variation;
        document.getElementById('energy').textContent = data.energy_level;
        
        // Update progress bars
        updateProgressBar('pitchVariationBar', data.pitch_variation);
        updateProgressBar('energyBar', data.energy_level);
        
        // Update emotions
        if (data.emotion) {
            document.getElementById('primaryEmotion').textContent = data.emotion;
        }
        
        // Update transcript
        if (data.transcript) {
            document.getElementById('transcript').textContent = data.transcript;
        }
        
        // Update AI feedback
        document.getElementById('aiFeedback').textContent = data.feedback || 'Analysis complete. No specific feedback available.';
        
        // Initialize speech pattern chart
        if (data.pattern_data) {
            initSpeechPatternChart(data.pattern_data);
        } else {
            // Create mock data if not available
            const mockData = {
                labels: Array.from({length: 10}, (_, i) => i + 1),
                pitchData: Array.from({length: 10}, () => Math.random() * 50 + 50),
                energyData: Array.from({length: 10}, () => Math.random() * 70 + 30)
            };
            initSpeechPatternChart(mockData);
        }
    }
    
    // Update progress bar based on level
    function updateProgressBar(id, level) {
        const progressBar = document.getElementById(id);
        let percentage = 0;
        
        switch (level ? level.toLowerCase() : '') {
            case 'low':
                percentage = 30;
                break;
            case 'medium':
                percentage = 60;
                break;
            case 'high':
                percentage = 90;
                break;
            default:
                percentage = 0;
        }
        
        progressBar.style.width = `${percentage}%`;
    }
    
    // Display basic analysis if API fails or basic level is selected
    function displayBasicAnalysis(duration) {
        document.getElementById('duration').textContent = formatTime(duration);
        document.getElementById('speakingRate').textContent = 'N/A';
        document.getElementById('pitchVariation').textContent = 'N/A';
        document.getElementById('energy').textContent = 'N/A';
        document.getElementById('primaryEmotion').textContent = 'N/A';
        document.getElementById('transcript').textContent = 'Transcription not available in basic analysis mode.';
        document.getElementById('aiFeedback').textContent = 'For detailed AI feedback, select "Detailed" or "Advanced" analysis in settings.';
        
        // Initialize empty speech pattern chart
        initSpeechPatternChart();
    }
    
    // Play improved version of speech (with voice cloning)
    function playImprovedVersion() {
        // This would be implemented with the voice cloning API
        alert('Voice cloning feature would be implemented here. This would play back an enhanced version of your speech in your own voice.');
    }
    
    // Compare original and improved speech
    function compareSpeech() {
        // This would show a comparison UI
        alert('Speech comparison feature would be implemented here. This would allow you to compare your original speech with the AI-enhanced version.');
    }
    
    // Format seconds to MM:SS
    function formatTime(seconds) {
        const minutes = Math.floor(seconds / 60);
        const remainingSeconds = Math.floor(seconds % 60);
        return `${minutes}:${remainingSeconds.toString().padStart(2, '0')}`;
    }
    
    // Event listeners
    recordButton.addEventListener('click', startRecording);
    stopButton.addEventListener('click', stopRecording);
    downloadButton.addEventListener('click', downloadRecording);
    improveButton.addEventListener('click', playImprovedVersion);
    compareSpeechButton.addEventListener('click', compareSpeech);
});