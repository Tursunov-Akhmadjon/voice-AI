import torch
from transformers import VitsModel, AutoTokenizer
import scipy.io.wavfile
import io
import base64
import numpy as np

class TTSService:
    def __init__(self):
        self.model_name = "facebook/mms-tts-uzb-script_cyrillic"
        self.model = None
        self.tokenizer = None
        self.device = "cpu" # Use CPU to avoid complex CUDA setup for user
        self.audio_cache = {} # Simple in-memory cache for audio
        
    def _load_model(self):
        if self.model is None:
            print(f"Loading TTS model: {self.model_name}...")
            try:
                self.tokenizer = AutoTokenizer.from_pretrained(self.model_name)
                self.model = VitsModel.from_pretrained(self.model_name)
                self.model.to(self.device)
                print("TTS model loaded successfully.")
            except Exception as e:
                print(f"Error loading TTS model: {e}")
                self.model = None

    def generate_audio(self, text: str) -> str:
        """
        Generates audio from text and returns base64 encoded WAV string.
        Uses in-memory cache to speed up repeated requests.
        """
        # Check cache first
        if text in self.audio_cache:
            # print(f"[TTS CACHE HIT] {text[:30]}...") # Removed to prevent encoding errors
            return self.audio_cache[text]

        self._load_model()
        if not self.model or not self.tokenizer:
            return None

        try:
            inputs = self.tokenizer(text, return_tensors="pt")
            inputs = inputs.to(self.device)

            with torch.no_grad():
                output = self.model(**inputs).waveform

            # Convert to numpy
            audio_data = output.cpu().numpy().squeeze()
            
            # Normalize audio
            audio_data = audio_data / np.max(np.abs(audio_data))
            
            # Convert to 16-bit PCM
            audio_data_int16 = (audio_data * 32767).astype(np.int16)
            
            # Save to in-memory buffer
            buffer = io.BytesIO()
            scipy.io.wavfile.write(buffer, rate=self.model.config.sampling_rate, data=audio_data_int16)
            
            # Encode to base64
            audio_base64 = base64.b64encode(buffer.getvalue()).decode('utf-8')
            
            # Store in cache (limit size if needed, but for now keep simple)
            self.audio_cache[text] = audio_base64
            
            return audio_base64
            
        except Exception as e:
            print(f"Error generating audio: {e}")
            return None

tts_service = TTSService()
