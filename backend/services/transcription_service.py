import whisper
import asyncio
import os
from typing import List, Dict
import logging

logger = logging.getLogger(__name__)

class TranscriptionService:
    def __init__(self, model_size: str = "base"):
        """Initialize Whisper model"""
        self.model_size = model_size
        self.model = None
        self._load_model()
    
    def _load_model(self):
        """Load Whisper model"""
        try:
            self.model = whisper.load_model(self.model_size)
            logger.info(f"Loaded Whisper model: {self.model_size}")
        except Exception as e:
            logger.error(f"Failed to load Whisper model: {str(e)}")
            raise
    
    async def transcribe(self, video_path: str, language: str = None) -> List[Dict]:
        """Transcribe video to text with timestamps"""
        try:
            if not os.path.exists(video_path):
                raise FileNotFoundError(f"Video file not found: {video_path}")
            
            # Run transcription in thread pool to avoid blocking
            loop = asyncio.get_event_loop()
            result = await loop.run_in_executor(
                None, self._transcribe_sync, video_path, language
            )
            
            # Process segments
            segments = []
            for segment in result["segments"]:
                segments.append({
                    "start": segment["start"],
                    "end": segment["end"],
                    "text": segment["text"].strip(),
                    "confidence": segment.get("avg_logprob", 0.0)
                })
            
            return segments
            
        except Exception as e:
            logger.error(f"Error transcribing video: {str(e)}")
            raise Exception(f"Failed to transcribe video: {str(e)}")
    
    def _transcribe_sync(self, video_path: str, language: str = None) -> dict:
        """Synchronous transcription"""
        options = {
            "task": "transcribe",
            "verbose": False,
        }
        
        if language:
            options["language"] = language
        
        return self.model.transcribe(video_path, **options)
    
    async def extract_audio_features(self, video_path: str) -> Dict:
        """Extract audio features for highlight detection"""
        try:
            loop = asyncio.get_event_loop()
            result = await loop.run_in_executor(
                None, self._extract_features_sync, video_path
            )
            
            return result
            
        except Exception as e:
            logger.error(f"Error extracting audio features: {str(e)}")
            return {}
    
    def _extract_features_sync(self, video_path: str) -> Dict:
        """Extract audio features synchronously"""
        try:
            import librosa
            import numpy as np
            
            # Load audio
            y, sr = librosa.load(video_path, sr=16000)
            
            # Extract features
            features = {
                "rms_energy": librosa.feature.rms(y=y)[0],
                "spectral_centroids": librosa.feature.spectral_centroid(y=y, sr=sr)[0],
                "zero_crossing_rate": librosa.feature.zero_crossing_rate(y)[0],
                "tempo": librosa.beat.tempo(y=y, sr=sr)[0],
                "duration": len(y) / sr
            }
            
            # Calculate time axis
            hop_length = 512
            features["time_axis"] = librosa.frames_to_time(
                np.arange(len(features["rms_energy"])), 
                sr=sr, 
                hop_length=hop_length
            )
            
            return features
            
        except ImportError:
            logger.warning("librosa not available, using basic features")
            return {"duration": 0}
        except Exception as e:
            logger.error(f"Error extracting features: {str(e)}")
            return {"duration": 0}
    
    def get_transcript_text(self, segments: List[Dict]) -> str:
        """Get full transcript text from segments"""
        return " ".join([segment["text"] for segment in segments])
    
    def find_segments_by_keywords(self, segments: List[Dict], keywords: List[str]) -> List[Dict]:
        """Find segments containing specific keywords"""
        matching_segments = []
        
        for segment in segments:
            text_lower = segment["text"].lower()
            for keyword in keywords:
                if keyword.lower() in text_lower:
                    matching_segments.append(segment)
                    break
        
        return matching_segments