from transformers import AutoFeatureExtractor, HubertForSequenceClassification
import torch
import torchaudio 

# Load the model and feature extractor once
extractor = AutoFeatureExtractor.from_pretrained("superb/hubert-large-superb-er")
model = HubertForSequenceClassification.from_pretrained("superb/hubert-large-superb-er")

# Define emotion labels (index -> label)
emotion_labels = [
    "neutral", "calm", "happy", "sad", "angry", "fearful", "disgust", "surprised"
]

def predict_emotion(audio_path):
    # Load audio
    speech_array, sampling_rate = torchaudio.load(audio_path)
    
    # Resample if needed (model expects 16kHz)
    if sampling_rate != 16000:
        resampler = torchaudio.transforms.Resample(orig_freq=sampling_rate, new_freq=16000)
        speech_array = resampler(speech_array)
    
    # Feature extraction
    inputs = extractor(speech_array.squeeze().numpy(), sampling_rate=16000, return_tensors="pt", padding=True)
    
    # Prediction
    with torch.no_grad():
        logits = model(**inputs).logits
    
    predicted_id = torch.argmax(logits, dim=-1).item()
    predicted_emotion = emotion_labels[predicted_id]
    
    return predicted_emotion
