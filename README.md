# ToneCoach: Emotional Intelligence for Public Speaking

ToneCoach is an AI-powered speech coaching application that provides real-time feedback on speech expressiveness. It analyzes various aspects of your speech including tone, energy, pitch, and pacing to help improve your public speaking skills.

## Features

- Record and visualize your speech in real-time
- Analyze speech for expressiveness metrics:
  - Speaking rate (words per minute)
  - Pitch variation
  - Energy levels
  - Silence/pause patterns
- Receive personalized AI feedback
- Download your recordings for later review
- Modern, responsive interface

## Setup Instructions

### Prerequisites

- Python 3.7+
- Node.js (optional, for development)

### Backend Setup

1. Navigate to the backend directory:
   ```
   cd backend
   ```

2. Create a virtual environment and activate it:
   ```
   python -m venv venv
   
   # On Windows
   venv\Scripts\activate
   
   # On macOS/Linux
   source venv/bin/activate
   ```

3. Install dependencies:
   ```
   pip install -r requirements.txt
   ```

4. Start the Flask server:
   ```
   python app.py
   ```
   
   The server will run on http://localhost:5000 by default.

### Frontend Setup

The frontend is built with vanilla HTML, CSS, and JavaScript, so no build steps are required.

1. Simply open the `frontend/index.html` file in your web browser, or

2. Serve it using a simple HTTP server:
   ```
   # If you have Python installed
   # Navigate to the frontend directory
   cd frontend
   
   # Start a simple HTTP server
   python -m http.server 8000
   ```

   Then access the application at http://localhost:8000

## Usage

1. Open the ToneCoach application in your browser
2. Click "Start Recording" and speak into your microphone
3. Click "Stop Recording" when you're finished
4. Wait for the analysis to complete
5. Review your speech metrics and AI feedback
6. Optionally download your recording for later review

## Technical Details

### Frontend
- Pure HTML, CSS, and JavaScript
- Uses the Web Audio API for recording and visualization
- Responsive design that works on mobile and desktop

### Backend
- Flask-based Python API
- Speech analysis using librosa, webrtcvad, and other audio processing libraries
- Speech-to-text using Google's Speech Recognition API

## Extending the Application

### Adding New Metrics
To add new speech analysis metrics, modify the `speech_analyzer.py` file and add your analysis functions to the appropriate utility modules.

### Improving the Voice Cloning Feature
To implement voice cloning for demonstration purposes, you'll need to:
1. Add ElevenLabs or a similar voice cloning API integration
2. Create an endpoint for voice model training
3. Update the frontend to support playback of enhanced speech examples

## Troubleshooting

### Common Issues

- **Microphone Access Error**: Ensure you've granted microphone permissions in your browser
- **Analysis Error**: Check that the backend server is running and accessible
- **Empty Analysis Results**: Ensure your microphone is working and detecting audio properly

### Browser Compatibility

ToneCoach works best with:
- Chrome 74+
- Firefox 75+
- Edge 79+
- Safari 13+

## Future Development

- Multilingual support
- Integration with VR/AR platforms for immersive training
- More advanced emotion detection using deep learning models
- User accounts to track progress over time
- Collaborative features for speech coaches and students

## License

MIT License