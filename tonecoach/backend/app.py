from flask import Flask, request, jsonify
from flask_cors import CORS
import os
from utils.emotion_detection import predict_emotion

app = Flask(__name__)
CORS(app, resources={r"/*": {"origins": "http://127.0.0.1:8000"}}, supports_credentials=True)


@app.route('/analyze', methods=['POST', 'OPTIONS'])
def analyze():
    if request.method == 'OPTIONS':
        return '', 204

    file = request.files.get('audio')
    if not file:
        return jsonify({'error': 'No audio file provided'}), 400

    audio_path = os.path.join(os.getcwd(), "temp_audio.wav") # Temporary path for saving audio
    file.save(audio_path)

    emotion = predict_emotion(audio_path)

    return jsonify({'emotion': emotion})

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)
