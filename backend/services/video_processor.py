import cv2
import numpy as np
from typing import Tuple, Optional
import logging

logger = logging.getLogger(__name__)

class VideoProcessor:
    def __init__(self):
        pass
    
    def get_video_info(self, video_path: str) -> dict:
        """Get basic video information"""
        try:
            cap = cv2.VideoCapture(video_path)
            
            if not cap.isOpened():
                raise Exception("Could not open video file")
            
            # Get video properties
            fps = cap.get(cv2.CAP_PROP_FPS)
            frame_count = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
            width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
            height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
            duration = frame_count / fps if fps > 0 else 0
            
            cap.release()
            
            return {
                'width': width,
                'height': height,
                'fps': fps,
                'frame_count': frame_count,
                'duration': duration,
                'aspect_ratio': width / height if height > 0 else 0
            }
            
        except Exception as e:
            logger.error(f"Error getting video info: {str(e)}")
            return {}
    
    def detect_scene_changes(self, video_path: str, threshold: float = 0.3) -> list:
        """Detect scene changes in video"""
        try:
            cap = cv2.VideoCapture(video_path)
            
            if not cap.isOpened():
                return []
            
            scene_changes = []
            prev_frame = None
            frame_number = 0
            fps = cap.get(cv2.CAP_PROP_FPS)
            
            while True:
                ret, frame = cap.read()
                if not ret:
                    break
                
                # Convert to grayscale for comparison
                gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
                
                if prev_frame is not None:
                    # Calculate histogram difference
                    diff = cv2.compareHist(
                        cv2.calcHist([prev_frame], [0], None, [256], [0, 256]),
                        cv2.calcHist([gray], [0], None, [256], [0, 256]),
                        cv2.HISTCMP_CORREL
                    )
                    
                    # If difference is significant, mark as scene change
                    if diff < (1 - threshold):
                        timestamp = frame_number / fps
                        scene_changes.append(timestamp)
                
                prev_frame = gray
                frame_number += 1
            
            cap.release()
            return scene_changes
            
        except Exception as e:
            logger.error(f"Error detecting scene changes: {str(e)}")
            return []
    
    def extract_keyframes(self, video_path: str, num_frames: int = 10) -> list:
        """Extract key frames from video"""
        try:
            cap = cv2.VideoCapture(video_path)
            
            if not cap.isOpened():
                return []
            
            frame_count = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
            fps = cap.get(cv2.CAP_PROP_FPS)
            
            # Calculate frame intervals
            interval = max(1, frame_count // num_frames)
            keyframes = []
            
            for i in range(0, frame_count, interval):
                cap.set(cv2.CAP_PROP_POS_FRAMES, i)
                ret, frame = cap.read()
                
                if ret:
                    timestamp = i / fps
                    keyframes.append({
                        'frame_number': i,
                        'timestamp': timestamp,
                        'frame': frame
                    })
                
                if len(keyframes) >= num_frames:
                    break
            
            cap.release()
            return keyframes
            
        except Exception as e:
            logger.error(f"Error extracting keyframes: {str(e)}")
            return []
    
    def calculate_motion_intensity(self, video_path: str, sample_rate: int = 30) -> list:
        """Calculate motion intensity over time"""
        try:
            cap = cv2.VideoCapture(video_path)
            
            if not cap.isOpened():
                return []
            
            motion_data = []
            prev_frame = None
            frame_count = 0
            fps = cap.get(cv2.CAP_PROP_FPS)
            
            while True:
                ret, frame = cap.read()
                if not ret:
                    break
                
                # Sample frames at specified rate
                if frame_count % sample_rate == 0:
                    gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
                    
                    if prev_frame is not None:
                        # Calculate optical flow
                        flow = cv2.calcOpticalFlowPyrLK(
                            prev_frame, gray, None, None
                        )
                        
                        # Calculate motion magnitude
                        if flow[0] is not None:
                            motion_magnitude = np.mean(np.sqrt(
                                flow[0][:, :, 0]**2 + flow[0][:, :, 1]**2
                            ))
                        else:
                            motion_magnitude = 0
                        
                        timestamp = frame_count / fps
                        motion_data.append({
                            'timestamp': timestamp,
                            'motion_intensity': motion_magnitude
                        })
                    
                    prev_frame = gray
                
                frame_count += 1
            
            cap.release()
            return motion_data
            
        except Exception as e:
            logger.error(f"Error calculating motion intensity: {str(e)}")
            return []
    
    def detect_faces_in_video(self, video_path: str, sample_interval: int = 60) -> list:
        """Detect faces throughout the video"""
        try:
            import face_recognition
            
            cap = cv2.VideoCapture(video_path)
            
            if not cap.isOpened():
                return []
            
            face_data = []
            frame_count = 0
            fps = cap.get(cv2.CAP_PROP_FPS)
            total_frames = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
            
            # Sample frames at intervals
            for frame_pos in range(0, total_frames, sample_interval):
                cap.set(cv2.CAP_PROP_POS_FRAMES, frame_pos)
                ret, frame = cap.read()
                
                if not ret:
                    continue
                
                # Convert BGR to RGB
                rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
                
                # Detect faces
                face_locations = face_recognition.face_locations(rgb_frame)
                
                if face_locations:
                    timestamp = frame_pos / fps
                    face_data.append({
                        'timestamp': timestamp,
                        'face_count': len(face_locations),
                        'face_locations': face_locations
                    })
            
            cap.release()
            return face_data
            
        except ImportError:
            logger.warning("face_recognition not available")
            return []
        except Exception as e:
            logger.error(f"Error detecting faces: {str(e)}")
            return []
    
    def get_video_quality_metrics(self, video_path: str) -> dict:
        """Analyze video quality metrics"""
        try:
            cap = cv2.VideoCapture(video_path)
            
            if not cap.isOpened():
                return {}
            
            # Sample some frames for analysis
            frame_count = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
            sample_frames = min(10, frame_count)
            
            brightness_values = []
            contrast_values = []
            sharpness_values = []
            
            for i in range(sample_frames):
                frame_pos = i * (frame_count // sample_frames)
                cap.set(cv2.CAP_PROP_POS_FRAMES, frame_pos)
                ret, frame = cap.read()
                
                if not ret:
                    continue
                
                gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
                
                # Calculate metrics
                brightness = np.mean(gray)
                contrast = np.std(gray)
                
                # Sharpness using Laplacian variance
                laplacian = cv2.Laplacian(gray, cv2.CV_64F)
                sharpness = laplacian.var()
                
                brightness_values.append(brightness)
                contrast_values.append(contrast)
                sharpness_values.append(sharpness)
            
            cap.release()
            
            return {
                'avg_brightness': np.mean(brightness_values) if brightness_values else 0,
                'avg_contrast': np.mean(contrast_values) if contrast_values else 0,
                'avg_sharpness': np.mean(sharpness_values) if sharpness_values else 0,
                'brightness_std': np.std(brightness_values) if brightness_values else 0,
                'contrast_std': np.std(contrast_values) if contrast_values else 0,
                'sharpness_std': np.std(sharpness_values) if sharpness_values else 0
            }
            
        except Exception as e:
            logger.error(f"Error analyzing video quality: {str(e)}")
            return {}