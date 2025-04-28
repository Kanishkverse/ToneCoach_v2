import numpy as np
import librosa

def analyze_emotion(y, sr):
    """
    Basic emotion detection in speech based on acoustic features
    
    This is a simplified implementation. For production use,
    consider using a pre-trained model for emotion recognition.
    """
    try:
        # Extract various features
        # 1. Spectral centroid (brightness)
        centroid = librosa.feature.spectral_centroid(y=y, sr=sr).mean()
        
        # 2. Spectral contrast
        contrast = librosa.feature.spectral_contrast(y=y, sr=sr).mean()
        
        # 3. RMS energy
        rms = librosa.feature.rms(y=y).mean()
        
        # 4. Zero crossing rate (noisiness)
        zcr = librosa.feature.zero_crossing_rate(y=y).mean()
        
        # 5. Pitch statistics
        pitches, magnitudes = librosa.piptrack(y=y, sr=sr)
        pitch_values = []
        for i in range(pitches.shape[1]):
            index = magnitudes[:, i].argmax()
            pitch = pitches[index, i]
            if pitch > 0:
                pitch_values.append(pitch)
        
        if pitch_values:
            pitch_mean = np.mean(pitch_values)
            pitch_std = np.std(pitch_values)
        else:
            pitch_mean = 0
            pitch_std = 0
        
        # Simple rule-based emotion classification
        # Note: This is a very simplified approach
        
        # High energy, high pitch variation → Excited/Happy
        if rms > 0.1 and pitch_std > 20:
            return "Excited"
        
        # Low energy, low pitch → Sad/Tired
        elif rms < 0.05 and pitch_mean < 100:
            return "Subdued"
        
        # High energy, low pitch variation → Angry/Stern
        elif rms > 0.1 and pitch_std < 10:
            return "Assertive"
        
        # High pitch, medium energy → Anxious/Nervous
        elif pitch_mean > 150 and 0.05 < rms < 0.1:
            return "Nervous"
        
        # Medium everything → Neutral
        else:
            return "Neutral"
    except Exception as e:
        print(f"Error in emotion analysis: {e}")
        return "Neutral"