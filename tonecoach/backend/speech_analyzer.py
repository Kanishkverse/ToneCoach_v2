import librosa
import numpy as np
import speech_recognition as sr
from pydub import AudioSegment
import webrtcvad
import wave
import struct
from utils.audio_processing import calculate_speaking_rate, detect_pitch_variations
from utils.emotion_detection import analyze_emotion

class SpeechAnalyzer:
    def __init__(self):
        self.recognizer = sr.Recognizer()
        try:
            self.vad = webrtcvad.Vad(3)  # Aggressiveness level 3 (most aggressive)
        except Exception as e:
            print(f"Warning: Could not initialize VAD: {e}")
            self.vad = None
    
    def analyze(self, audio_path, level='detailed'):
        """Analyze a speech audio file and return metrics based on the selected level"""
        
        # Load audio file
        try:
            y, sr = librosa.load(audio_path, sr=None)
            duration = librosa.get_duration(y=y, sr=sr)
        except Exception as e:
            print(f"Error loading audio file: {e}")
            # Return basic duration-only analysis in case of error
            return {
                'duration': 0,
                'speaking_rate': 0,
                'pitch_variation': 'N/A',
                'energy_level': 'N/A',
                'feedback': 'Could not analyze the audio file. Please try again with a different recording.'
            }
        
        # Basic analysis (duration only)
        if level == 'basic':
            return {
                'duration': duration,
                'speaking_rate': 0,
                'pitch_variation': 'N/A',
                'energy_level': 'N/A',
                'feedback': 'Basic analysis completed. For more detailed analysis, change the analysis level.'
            }
        
        # Calculate common metrics
        energy = self._calculate_energy(y)
        pitch_variations = detect_pitch_variations(y, sr)
        
        # For detailed and advanced levels
        transcript = ""
        speaking_rate = 0
        silence_ratio = 0
        emotion = "Neutral"
        
        if level in ['detailed', 'advanced']:
            try:
                transcript = self._transcribe(audio_path)
                speaking_rate = calculate_speaking_rate(transcript, duration)
                silence_ratio = self._calculate_silence_ratio(audio_path)
                emotion = analyze_emotion(y, sr)
            except Exception as e:
                print(f"Error in detailed analysis: {e}")
                # Continue with partial results
        
        # Generate feedback
        feedback = self._generate_feedback(
            duration, 
            speaking_rate, 
            pitch_variations, 
            energy, 
            silence_ratio,
            emotion,
            level
        )
        
        # Build pattern data for visualization
        pattern_data = self._build_pattern_data(y, sr)
        
        # Return different detail levels based on requested level
        analysis_results = {
            'duration': duration,
            'transcript': transcript,
            'speaking_rate': speaking_rate,
            'pitch_variation': pitch_variations['label'],
            'energy_level': energy['label'],
            'silence_ratio': silence_ratio,
            'emotion': emotion,
            'feedback': feedback,
            'pattern_data': pattern_data
        }
        
        # For advanced level, add additional metrics
        if level == 'advanced':
            analysis_results.update({
                'pitch_stats': pitch_variations['stats'],
                'energy_value': energy['value'],
                'advanced_metrics': {
                    'pace_consistency': self._calculate_pace_consistency(y, sr),
                    'expressiveness_score': self._calculate_expressiveness_score(pitch_variations, energy, silence_ratio)
                }
            })
        
        return analysis_results
    
    def _transcribe(self, audio_path):
        """Transcribe speech to text"""
        try:
            with sr.AudioFile(audio_path) as source:
                audio = self.recognizer.record(source)
                transcript = self.recognizer.recognize_google(audio)
                return transcript
        except Exception as e:
            print(f"Error in transcription: {e}")
            return ""
    
    def _calculate_energy(self, y):
        """Calculate energy level of audio"""
        try:
            rms = librosa.feature.rms(y=y)[0]
            mean_energy = np.mean(rms)
            
            # Classify energy level
            if mean_energy > 0.1:
                label = "High"
            elif mean_energy > 0.05:
                label = "Medium"
            else:
                label = "Low"
            
            return {
                'value': float(mean_energy),
                'label': label
            }
        except Exception as e:
            print(f"Error calculating energy: {e}")
            return {'value': 0, 'label': 'N/A'}
    
    def _calculate_silence_ratio(self, audio_path):
        """Calculate ratio of silence to speech"""
        if not self.vad:
            return 0
            
        try:
            # Open wave file
            with wave.open(audio_path, 'rb') as wf:
                # Get parameters
                channels = wf.getnchannels()
                sample_width = wf.getsampwidth()
                sample_rate = wf.getframerate()
                
                # Process in 30ms chunks (standard for VAD)
                chunk_duration = 0.03  # seconds
                chunk_size = int(sample_rate * chunk_duration)
                
                total_chunks = 0
                silent_chunks = 0
                
                while True:
                    frames = wf.readframes(chunk_size)
                    if not frames:
                        break
                    
                    # Make sure we have enough frames
                    if len(frames) < 2 * channels * chunk_size:
                        break
                    
                    # Convert to PCM 16-bit mono
                    if channels == 2:
                        # Convert stereo to mono
                        mono_frames = b''
                        for i in range(0, len(frames), 4):
                            if i + 3 < len(frames):
                                left = struct.unpack('<h', frames[i:i+2])[0]
                                right = struct.unpack('<h', frames[i+2:i+4])[0]
                                mono = (left + right) // 2
                                mono_frames += struct.pack('<h', mono)
                    else:
                        mono_frames = frames
                    
                    total_chunks += 1
                    
                    # Check if chunk is speech or silence
                    try:
                        is_speech = self.vad.is_speech(mono_frames, sample_rate)
                        if not is_speech:
                            silent_chunks += 1
                    except Exception as e:
                        pass
            
            if total_chunks == 0:
                return 0
                
            silence_ratio = silent_chunks / total_chunks
            return silence_ratio
            
        except Exception as e:
            print(f"Error calculating silence ratio: {e}")
            return 0
    
    def _calculate_pace_consistency(self, y, sr):
        """Calculate consistency of speaking pace"""
        # This is a simplified placeholder implementation
        try:
            # Detect onsets (word boundaries)
            onset_env = librosa.onset.onset_strength(y=y, sr=sr)
            onsets = librosa.onset.onset_detect(onset_envelope=onset_env, sr=sr)
            
            if len(onsets) < 2:
                return "N/A"
            
            # Calculate inter-onset intervals
            intervals = np.diff(onsets)
            
            # Calculate coefficient of variation (lower is more consistent)
            cv = np.std(intervals) / np.mean(intervals) if np.mean(intervals) > 0 else 0
            
            if cv < 0.3:
                return "Very Consistent"
            elif cv < 0.5:
                return "Consistent"
            elif cv < 0.7:
                return "Somewhat Inconsistent"
            else:
                return "Inconsistent"
                
        except Exception as e:
            print(f"Error calculating pace consistency: {e}")
            return "N/A"
    
    def _calculate_expressiveness_score(self, pitch_variations, energy, silence_ratio):
        """Calculate overall expressiveness score based on multiple metrics"""
        try:
            # Convert pitch variation label to score
            pitch_score = 0
            if pitch_variations['label'] == 'High':
                pitch_score = 5
            elif pitch_variations['label'] == 'Medium':
                pitch_score = 3
            elif pitch_variations['label'] == 'Low':
                pitch_score = 1
            
            # Convert energy label to score
            energy_score = 0
            if energy['label'] == 'High':
                energy_score = 5
            elif energy['label'] == 'Medium':
                energy_score = 3
            elif energy['label'] == 'Low':
                energy_score = 1
            
            # Silence ratio score (optimal around 0.2-0.3)
            silence_score = 5 - abs(silence_ratio - 0.25) * 10
            silence_score = max(0, min(silence_score, 5))
            
            # Calculate weighted average
            total_score = (pitch_score * 0.4) + (energy_score * 0.4) + (silence_score * 0.2)
            
            # Convert to 0-100 scale
            expressiveness_score = total_score * 20
            
            return round(expressiveness_score)
            
        except Exception as e:
            print(f"Error calculating expressiveness score: {e}")
            return 50  # Default middle score
    
    def _build_pattern_data(self, y, sr):
        """Build pattern data for visualization"""
        try:
            # Create 10 segments for visualization
            segment_count = 10
            segment_length = len(y) // segment_count
            
            labels = []
            pitch_data = []
            energy_data = []
            
            for i in range(segment_count):
                start = i * segment_length
                end = start + segment_length
                segment = y[start:end]
                
                # Skip if segment is too short
                if len(segment) < 512:
                    continue
                
                labels.append(i + 1)
                
                # Calculate pitch for segment
                pitches, magnitudes = librosa.piptrack(y=segment, sr=sr)
                pitch_values = []
                for j in range(pitches.shape[1]):
                    index = magnitudes[:, j].argmax()
                    pitch = pitches[index, j]
                    if pitch > 0:
                        pitch_values.append(pitch)
                
                # Calculate average pitch (normalized for visualization)
                if pitch_values:
                    avg_pitch = np.mean(pitch_values) / 10
                else:
                    avg_pitch = 0
                pitch_data.append(avg_pitch)
                
                # Calculate energy for segment
                rms = librosa.feature.rms(y=segment)[0]
                energy_value = np.mean(rms) * 1000
                energy_data.append(energy_value)
            
            return {
                'labels': labels,
                'pitchData': pitch_data,
                'energyData': energy_data
            }
            
        except Exception as e:
            print(f"Error building pattern data: {e}")
            # Return default empty pattern data
            return {
                'labels': list(range(1, 11)),
                'pitchData': [0] * 10,
                'energyData': [0] * 10
            }
    
    def _generate_feedback(self, duration, speaking_rate, pitch_variations, energy, silence_ratio, emotion, level):
        """Generate personalized feedback based on speech metrics and analysis level"""
        
        if level == 'basic':
            return "Basic analysis completed. For personalized feedback, use detailed or advanced analysis."
        
        feedback = []
        
        # Speaking rate feedback
        if speaking_rate < 120:
            feedback.append("Your speaking rate is quite slow. Try to increase your pace a bit to keep the audience engaged.")
        elif speaking_rate > 180:
            feedback.append("You're speaking quite rapidly. Consider slowing down slightly to improve clarity.")
        else:
            feedback.append("Your speaking pace is good and should be easy for listeners to follow.")
        
        # Pitch variation feedback
        if pitch_variations['label'] == 'Low':
            feedback.append("Your speech has limited pitch variation, which might sound monotonous. Try to vary your tone more to emphasize key points.")
        elif pitch_variations['label'] == 'High':
            feedback.append("You have excellent vocal expressiveness with good pitch variation that helps convey emotion and emphasis.")
        
        # Energy feedback
        if energy['label'] == 'Low':
            feedback.append("Your vocal energy is quite low. Try projecting your voice more confidently.")
        elif energy['label'] == 'High':
            feedback.append("Your energy level is high, showing enthusiasm and confidence.")
        
        # Silence feedback
        if silence_ratio > 0.3:
            feedback.append("You have frequent pauses in your speech. While some pauses are effective, too many can disrupt your flow.")
        elif silence_ratio < 0.1:
            feedback.append("Consider incorporating strategic pauses to give emphasis to important points and allow your audience time to absorb information.")
        
        # Duration feedback
        minutes = int(duration / 60)
        if minutes > 5:
            feedback.append("Your speech was quite long. For maximum retention, consider condensing your main points.")
        
        # Emotion feedback
        if emotion and emotion != "Neutral":
            feedback.append(f"Your speech conveys a {emotion.lower()} tone, which aligns well with your message.")
        
        # Advanced level additional feedback
        if level == 'advanced':
            feedback.append("For more precise improvement, focus on maintaining consistent pacing while varying your pitch at key moments to emphasize important points.")
        
        return " ".join(feedback)