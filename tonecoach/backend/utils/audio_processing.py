import numpy as np
import librosa

def calculate_speaking_rate(transcript, duration):
    """
    Calculate speaking rate in words per minute
    """
    if not transcript or duration <= 0:
        return 0
    
    # Count words
    words = transcript.split()
    word_count = len(words)
    
    # Convert to words per minute
    minutes = duration / 60
    wpm = word_count / minutes
    
    return wpm

def detect_pitch_variations(y, sr):
    """
    Analyze pitch variations in speech
    """
    # Extract pitch (fundamental frequency)
    try:
        pitches, magnitudes = librosa.piptrack(y=y, sr=sr)
        
        # Get pitch for each frame
        pitch_values = []
        for i in range(pitches.shape[1]):
            index = magnitudes[:, i].argmax()
            pitch = pitches[index, i]
            if pitch > 0:  # Only append valid pitch values
                pitch_values.append(pitch)
        
        # If no valid pitches detected
        if not pitch_values:
            return {
                'label': 'Unknown',
                'stats': {
                    'mean': 0,
                    'std': 0,
                    'range': 0
                }
            }
        
        # Calculate statistics
        pitch_mean = np.mean(pitch_values)
        pitch_std = np.std(pitch_values)
        pitch_range = np.max(pitch_values) - np.min(pitch_values)
        
        # Classify pitch variation
        if pitch_std > 25:
            variation_label = 'High'
        elif pitch_std > 10:
            variation_label = 'Medium'
        else:
            variation_label = 'Low'
        
        return {
            'label': variation_label,
            'stats': {
                'mean': float(pitch_mean),
                'std': float(pitch_std),
                'range': float(pitch_range)
            }
        }
    except Exception as e:
        print(f"Error in pitch variation detection: {e}")
        return {
            'label': 'Unknown',
            'stats': {
                'mean': 0,
                'std': 0,
                'range': 0
            }
        }

def detect_volume_variations(y):
    """
    Analyze volume/amplitude variations in speech
    """
    try:
        # Get RMS energy
        rms = librosa.feature.rms(y=y)[0]
        
        # Calculate statistics
        rms_mean = np.mean(rms)
        rms_std = np.std(rms)
        rms_range = np.max(rms) - np.min(rms)
        
        # Classify volume variation
        if rms_std > 0.05:
            variation_label = 'High'
        elif rms_std > 0.02:
            variation_label = 'Medium'
        else:
            variation_label = 'Low'
        
        return {
            'label': variation_label,
            'stats': {
                'mean': float(rms_mean),
                'std': float(rms_std),
                'range': float(rms_range)
            }
        }
    except Exception as e:
        print(f"Error in volume variation detection: {e}")
        return {
            'label': 'Unknown',
            'stats': {
                'mean': 0,
                'std': 0,
                'range': 0
            }
        }