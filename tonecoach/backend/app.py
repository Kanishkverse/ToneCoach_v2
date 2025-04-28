from flask import Flask, request, jsonify
from flask_cors import CORS
import os
import tempfile
import traceback

app = Flask(__name__)

# Configure CORS properly
CORS(app, resources={r"/*": {"origins": "*"}}, supports_credentials=True)

@app.route('/', methods=['GET'])
def home():
    """Root endpoint to check if API is running"""
    return jsonify({
        "status": "success",
        "message": "ToneCoach API is running",
        "version": "1.0.0"
    })

@app.route('/analyze', methods=['POST', 'OPTIONS'])
def analyze_speech():
    """Analyze speech audio and return detailed metrics"""
    # Handle preflight OPTIONS request
    if request.method == 'OPTIONS':
        response = jsonify({'status': 'success'})
        response.headers.add('Access-Control-Allow-Origin', '*')
        response.headers.add('Access-Control-Allow-Headers', 'Content-Type')
        response.headers.add('Access-Control-Allow-Methods', 'POST')
        return response
        
    if 'audio' not in request.files:
        return jsonify({'error': 'No audio file provided'}), 400
    
    audio_file = request.files['audio']
    analysis_level = request.form.get('level', 'detailed')
    
    # Return a simplified analysis for testing
    simple_analysis = {
        'duration': 10.5,
        'speaking_rate': 145,
        'pitch_variation': 'Medium',
        'energy_level': 'Medium',
        'transcript': 'This is a sample transcript.',
        'emotion': 'Neutral',
        'feedback': 'This is a placeholder feedback. Your speech seems good!',
        'pattern_data': {
            'labels': list(range(1, 11)),
            'pitchData': [50, 55, 60, 65, 70, 65, 60, 55, 50, 45],
            'energyData': [30, 35, 40, 45, 50, 55, 50, 45, 40, 35]
        }
    }
    
    # Set CORS headers in the response
    response = jsonify(simple_analysis)
    response.headers.add('Access-Control-Allow-Origin', '*')
    return response

if __name__ == '__main__':
    app.run(debug=True)