import numpy as np
import asyncio
from typing import List, Dict, Optional
import logging
from sklearn.preprocessing import StandardScaler
from sklearn.cluster import KMeans
import re

logger = logging.getLogger(__name__)

class HighlightDetector:
    def __init__(self):
        self.engagement_keywords = [
            "amazing", "incredible", "wow", "unbelievable", "shocking", "surprising",
            "important", "crucial", "key", "essential", "must", "never", "always",
            "secret", "hidden", "revealed", "discovery", "breakthrough", "game-changer",
            "mistake", "error", "wrong", "right", "correct", "truth", "fact",
            "question", "answer", "solution", "problem", "issue", "challenge",
            "tip", "trick", "hack", "method", "technique", "strategy", "way",
            "best", "worst", "top", "bottom", "first", "last", "only", "unique"
        ]
        
        self.emotion_keywords = [
            "love", "hate", "excited", "angry", "sad", "happy", "frustrated",
            "confused", "surprised", "shocked", "amazed", "disappointed"
        ]
    
    async def detect_highlights(self, video_path: str, transcription: List[Dict], 
                              max_clips: int = 3, min_duration: int = 30, 
                              max_duration: int = 60) -> List[Dict]:
        """Detect highlight segments from video and transcription"""
        try:
            # Extract features from transcription
            text_features = self._extract_text_features(transcription)
            
            # Extract audio features (if available)
            audio_features = await self._extract_audio_features(video_path)
            
            # Combine features and score segments
            scored_segments = self._score_segments(transcription, text_features, audio_features)
            
            # Select best highlights
            highlights = self._select_highlights(
                scored_segments, max_clips, min_duration, max_duration
            )
            
            return highlights
            
        except Exception as e:
            logger.error(f"Error detecting highlights: {str(e)}")
            # Fallback: return evenly spaced segments
            return self._fallback_highlights(transcription, max_clips, min_duration, max_duration)
    
    def _extract_text_features(self, transcription: List[Dict]) -> Dict:
        """Extract features from transcription text"""
        features = {
            "engagement_scores": [],
            "emotion_scores": [],
            "question_scores": [],
            "exclamation_scores": [],
            "word_counts": [],
            "speaking_rates": []
        }
        
        for segment in transcription:
            text = segment["text"].lower()
            duration = segment["end"] - segment["start"]
            word_count = len(text.split())
            
            # Engagement keywords score
            engagement_score = sum(1 for keyword in self.engagement_keywords if keyword in text)
            features["engagement_scores"].append(engagement_score)
            
            # Emotion keywords score
            emotion_score = sum(1 for keyword in self.emotion_keywords if keyword in text)
            features["emotion_scores"].append(emotion_score)
            
            # Question marks
            question_score = text.count("?")
            features["question_scores"].append(question_score)
            
            # Exclamation marks
            exclamation_score = text.count("!")
            features["exclamation_scores"].append(exclamation_score)
            
            # Word count
            features["word_counts"].append(word_count)
            
            # Speaking rate (words per second)
            speaking_rate = word_count / max(duration, 1)
            features["speaking_rates"].append(speaking_rate)
        
        return features
    
    async def _extract_audio_features(self, video_path: str) -> Dict:
        """Extract audio features for highlight detection"""
        try:
            from services.transcription_service import TranscriptionService
            transcription_service = TranscriptionService()
            return await transcription_service.extract_audio_features(video_path)
        except Exception as e:
            logger.warning(f"Could not extract audio features: {str(e)}")
            return {}
    
    def _score_segments(self, transcription: List[Dict], text_features: Dict, 
                       audio_features: Dict) -> List[Dict]:
        """Score each segment based on multiple features"""
        scored_segments = []
        
        # Normalize text features
        engagement_scores = np.array(text_features["engagement_scores"])
        emotion_scores = np.array(text_features["emotion_scores"])
        question_scores = np.array(text_features["question_scores"])
        exclamation_scores = np.array(text_features["exclamation_scores"])
        speaking_rates = np.array(text_features["speaking_rates"])
        
        # Normalize scores
        if len(engagement_scores) > 1:
            engagement_scores = (engagement_scores - engagement_scores.mean()) / max(engagement_scores.std(), 1)
            emotion_scores = (emotion_scores - emotion_scores.mean()) / max(emotion_scores.std(), 1)
            speaking_rates = (speaking_rates - speaking_rates.mean()) / max(speaking_rates.std(), 1)
        
        for i, segment in enumerate(transcription):
            score = 0.0
            
            # Text-based scoring
            score += engagement_scores[i] * 0.3
            score += emotion_scores[i] * 0.2
            score += question_scores[i] * 0.1
            score += exclamation_scores[i] * 0.1
            score += min(speaking_rates[i], 2.0) * 0.1  # Cap speaking rate bonus
            
            # Audio-based scoring (if available)
            if audio_features and "rms_energy" in audio_features:
                try:
                    start_time = segment["start"]
                    end_time = segment["end"]
                    time_axis = audio_features.get("time_axis", [])
                    rms_energy = audio_features.get("rms_energy", [])
                    
                    if len(time_axis) > 0 and len(rms_energy) > 0:
                        # Find corresponding audio segment
                        start_idx = np.searchsorted(time_axis, start_time)
                        end_idx = np.searchsorted(time_axis, end_time)
                        
                        if start_idx < len(rms_energy) and end_idx <= len(rms_energy):
                            segment_energy = np.mean(rms_energy[start_idx:end_idx])
                            # Normalize energy score
                            energy_score = min(segment_energy * 10, 1.0)
                            score += energy_score * 0.2
                except Exception as e:
                    logger.debug(f"Error processing audio features for segment {i}: {str(e)}")
            
            scored_segments.append({
                "start_time": segment["start"],
                "end_time": segment["end"],
                "text": segment["text"],
                "score": score,
                "confidence": segment.get("confidence", 0.0)
            })
        
        return scored_segments
    
    def _select_highlights(self, scored_segments: List[Dict], max_clips: int, 
                          min_duration: int, max_duration: int) -> List[Dict]:
        """Select the best highlight segments"""
        # Sort by score
        sorted_segments = sorted(scored_segments, key=lambda x: x["score"], reverse=True)
        
        highlights = []
        used_time_ranges = []
        
        for segment in sorted_segments:
            if len(highlights) >= max_clips:
                break
            
            start_time = segment["start_time"]
            end_time = segment["end_time"]
            duration = end_time - start_time
            
            # Check duration constraints
            if duration < min_duration or duration > max_duration:
                # Try to extend or trim the segment
                if duration < min_duration:
                    # Extend segment
                    extension = (min_duration - duration) / 2
                    start_time = max(0, start_time - extension)
                    end_time = end_time + extension
                elif duration > max_duration:
                    # Trim segment to max duration
                    end_time = start_time + max_duration
                
                duration = end_time - start_time
            
            # Check for overlap with existing highlights
            overlap = False
            for used_start, used_end in used_time_ranges:
                if (start_time < used_end and end_time > used_start):
                    overlap = True
                    break
            
            if not overlap:
                highlights.append({
                    "start_time": start_time,
                    "end_time": end_time,
                    "text": segment["text"],
                    "score": segment["score"],
                    "title": self._generate_title(segment["text"])
                })
                used_time_ranges.append((start_time, end_time))
        
        return highlights
    
    def _generate_title(self, text: str) -> str:
        """Generate a title for the highlight"""
        # Take first few words and clean them up
        words = text.strip().split()[:6]
        title = " ".join(words)
        
        # Clean up title
        title = re.sub(r'[^\w\s-]', '', title)
        title = title.strip()
        
        if not title:
            return "Highlight"
        
        return title.title()
    
    def _fallback_highlights(self, transcription: List[Dict], max_clips: int, 
                           min_duration: int, max_duration: int) -> List[Dict]:
        """Fallback method to create highlights when feature extraction fails"""
        if not transcription:
            return []
        
        total_duration = transcription[-1]["end"] - transcription[0]["start"]
        segment_duration = min(max_duration, max(min_duration, total_duration / max_clips))
        
        highlights = []
        current_time = transcription[0]["start"]
        
        for i in range(max_clips):
            start_time = current_time
            end_time = min(start_time + segment_duration, transcription[-1]["end"])
            
            # Find text for this segment
            segment_text = ""
            for segment in transcription:
                if segment["start"] >= start_time and segment["end"] <= end_time:
                    segment_text += segment["text"] + " "
            
            if segment_text.strip():
                highlights.append({
                    "start_time": start_time,
                    "end_time": end_time,
                    "text": segment_text.strip(),
                    "score": 0.5,
                    "title": f"Highlight {i+1}"
                })
            
            current_time = end_time + 10  # 10 second gap between clips
            
            if current_time >= transcription[-1]["end"]:
                break
        
        return highlights