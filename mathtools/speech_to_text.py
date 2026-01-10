import logging
from typing import Dict, Any

# Try to import whisper, but make it optional
try:
    import whisper
    WHISPER_AVAILABLE = True
except ImportError:
    WHISPER_AVAILABLE = False
    print("Warning: OpenAI Whisper not installed. Speech-to-text will not be available.")
    print("To install: pip install openai-whisper")


class SpeechToTextProcessor:
    """
    Speech-to-text processor using OpenAI Whisper.
    """
    
    def __init__(self, config: Dict[str, Any]):
        """
        Initialize speech-to-text processor.
        
        Args:
            config: ASR configuration from config.yaml
        """
        self.config = config
        self.logger = logging.getLogger("speech_to_text")
        
        if not WHISPER_AVAILABLE:
            self.logger.warning("Whisper not available - speech-to-text disabled")
            self.model = None
            self.language = config.get('language', 'en')
            return
        
        # Load Whisper model
        model_size = config.get('model', 'base')
        self.logger.info(f"Loading Whisper model: {model_size}")
        
        try:
            self.model = whisper.load_model(model_size, device=config.get('device', 'cpu'))
            self.language = config.get('language', 'en')
            self.logger.info("Speech-to-text processor initialized")
        except Exception as e:
            self.logger.error(f"Failed to load Whisper model: {e}")
            self.model = None
    
    def transcribe_audio(self, audio_path: str) -> Dict[str, Any]:
        """
        Transcribe audio file to text.
        
        Args:
            audio_path: Path to audio file
        
        Returns:
            Dictionary with transcription and metadata
        """
        if not WHISPER_AVAILABLE or self.model is None:
            return {
                "text": "",
                "language": self.language,
                "confidence": 0.0,
                "segments": [],
                "duration": 0.0,
                "error": "Whisper not available or model not loaded"
            }
        
        try:
            self.logger.info(f"Transcribing audio: {audio_path}")
            
            # Transcribe
            result = self.model.transcribe(
                audio_path,
                language=self.language,
                task='transcribe',
                verbose=False
            )
            
            text = result['text'].strip()
            language = result.get('language', self.language)
            
            # Extract segments with timestamps
            segments = []
            if 'segments' in result:
                for seg in result['segments']:
                    segments.append({
                        'text': seg['text'].strip(),
                        'start': seg['start'],
                        'end': seg['end'],
                        'confidence': seg.get('confidence', 1.0)
                    })
            
            # Calculate average confidence
            confidences = [s.get('confidence', 1.0) for s in segments]
            avg_confidence = sum(confidences) / len(confidences) if confidences else 1.0
            
            self.logger.info(
                f"Transcription completed: {len(text)} chars, "
                f"{len(segments)} segments, "
                f"confidence: {avg_confidence:.3f}"
            )
            
            return {
                "text": text,
                "language": language,
                "confidence": avg_confidence,
                "segments": segments,
                "duration": segments[-1]['end'] if segments else 0.0,
                "error": None
            }
        
        except Exception as e:
            self.logger.error(f"Transcription failed: {str(e)}", exc_info=True)
            return {
                "text": "",
                "language": self.language,
                "confidence": 0.0,
                "segments": [],
                "duration": 0.0,
                "error": str(e)
            }
    
    def transcribe_audio_bytes(self, audio_bytes: bytes, format: str = "wav") -> Dict[str, Any]:
        """
        Transcribe audio from bytes.
        
        Args:
            audio_bytes: Audio data as bytes
            format: Audio format (wav, mp3, etc.)
        
        Returns:
            Dictionary with transcription and metadata
        """
        if not WHISPER_AVAILABLE or self.model is None:
            return {
                "text": "",
                "language": self.language,
                "confidence": 0.0,
                "segments": [],
                "duration": 0.0,
                "error": "Whisper not available or model not loaded"
            }
        
        import tempfile
        import os
        
        try:
            # Save bytes to temporary file
            with tempfile.NamedTemporaryFile(delete=False, suffix=f".{format}") as tmp_file:
                tmp_file.write(audio_bytes)
                tmp_path = tmp_file.name
            
            # Transcribe
            result = self.transcribe_audio(tmp_path)
            
            # Clean up
            os.unlink(tmp_path)
            
            return result
        
        except Exception as e:
            self.logger.error(f"Transcription from bytes failed: {str(e)}", exc_info=True)
            return {
                "text": "",
                "language": self.language,
                "confidence": 0.0,
                "segments": [],
                "duration": 0.0,
                "error": str(e)
            }
    
    def enhance_math_transcription(self, text: str) -> str:
        """
        Post-process transcription to fix common math terminology.
        
        Args:
            text: Raw transcription
        
        Returns:
            Enhanced text with proper math notation
        """
        # Common speech-to-text math corrections
        replacements = {
            'plus': '+',
            'minus': '-',
            'times': '*',
            'divided by': '/',
            'equals': '=',
            'squared': '^2',
            'cubed': '^3',
            'square root of': 'sqrt(',
            'to the power of': '^',
            'pie': 'pi',  # Common misrecognition
            'sign': 'sin',  # Common misrecognition
            'co sign': 'cos',
            'tangent': 'tan',
        }
        
        enhanced = text.lower()
        for phrase, symbol in replacements.items():
            enhanced = enhanced.replace(phrase, symbol)
        
        # Add closing parenthesis for sqrt if missing
        if 'sqrt(' in enhanced and enhanced.count('sqrt(') > enhanced.count(')'):
            enhanced += ')' * (enhanced.count('sqrt(') - enhanced.count(')'))
        
        return enhanced


# Example usage
if __name__ == "__main__":
    config = {
        'model': 'base',
        'language': 'en',
        'device': 'cpu'
    }
    
    processor = SpeechToTextProcessor(config)
    # result = processor.transcribe_audio("path/to/audio.wav")
    # print(result)