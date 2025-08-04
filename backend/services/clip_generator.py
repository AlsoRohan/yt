import cv2
import numpy as np
import asyncio
import os
from typing import Optional, Tuple
import logging
from moviepy.editor import VideoFileClip, CompositeVideoClip
import face_recognition

logger = logging.getLogger(__name__)

class ClipGenerator:
    def __init__(self):
        self.output_dir = "outputs"
        os.makedirs(self.output_dir, exist_ok=True)
    
    async def create_clip(self, video_path: str, start_time: float, end_time: float,
                         output_path: str, auto_frame: bool = True, 
                         target_duration: int = 45) -> str:
        """Create a short clip from the original video"""
        try:
            # Adjust timing if needed
            duration = end_time - start_time
            if duration > target_duration:
                end_time = start_time + target_duration
            
            # Run video processing in thread pool
            loop = asyncio.get_event_loop()
            clip_path = await loop.run_in_executor(
                None, self._create_clip_sync, video_path, start_time, end_time, 
                output_path, auto_frame
            )
            
            return clip_path
            
        except Exception as e:
            logger.error(f"Error creating clip: {str(e)}")
            raise Exception(f"Failed to create clip: {str(e)}")
    
    def _create_clip_sync(self, video_path: str, start_time: float, end_time: float,
                         output_path: str, auto_frame: bool) -> str:
        """Synchronous clip creation"""
        try:
            # Load video
            video = VideoFileClip(video_path)
            
            # Extract clip
            clip = video.subclip(start_time, end_time)
            
            # Auto-frame to vertical format if requested
            if auto_frame:
                clip = self._auto_frame_to_vertical(clip)
            else:
                # Simple center crop to 9:16
                clip = self._center_crop_to_vertical(clip)
            
            # Ensure output directory exists
            os.makedirs(os.path.dirname(output_path), exist_ok=True)
            
            # Write the clip
            clip.write_videofile(
                output_path,
                codec='libx264',
                audio_codec='aac',
                temp_audiofile='temp-audio.m4a',
                remove_temp=True,
                verbose=False,
                logger=None
            )
            
            # Generate thumbnail
            self._generate_thumbnail(output_path)
            
            # Clean up
            clip.close()
            video.close()
            
            return output_path
            
        except Exception as e:
            logger.error(f"Error in sync clip creation: {str(e)}")
            raise
    
    def _auto_frame_to_vertical(self, clip) -> VideoFileClip:
        """Auto-frame video to vertical format using face detection"""
        try:
            # Get video dimensions
            width, height = clip.size
            target_width = int(height * 9 / 16)  # 9:16 aspect ratio
            
            if width <= target_width:
                # Video is already narrow enough, just crop height if needed
                return self._center_crop_to_vertical(clip)
            
            # Try face detection for smart cropping
            face_positions = self._detect_faces_in_clip(clip)
            
            if face_positions:
                # Use face positions to determine crop area
                crop_x = self._calculate_crop_position(face_positions, width, target_width)
            else:
                # Fallback to center crop
                crop_x = (width - target_width) // 2
            
            # Crop the video
            cropped_clip = clip.crop(x1=crop_x, x2=crop_x + target_width)
            
            return cropped_clip
            
        except Exception as e:
            logger.warning(f"Auto-framing failed, using center crop: {str(e)}")
            return self._center_crop_to_vertical(clip)
    
    def _center_crop_to_vertical(self, clip) -> VideoFileClip:
        """Simple center crop to 9:16 aspect ratio"""
        width, height = clip.size
        
        # Calculate target dimensions
        target_aspect = 9 / 16
        current_aspect = width / height
        
        if current_aspect > target_aspect:
            # Video is too wide, crop width
            target_width = int(height * target_aspect)
            crop_x = (width - target_width) // 2
            cropped_clip = clip.crop(x1=crop_x, x2=crop_x + target_width)
        else:
            # Video is too tall, crop height
            target_height = int(width / target_aspect)
            crop_y = (height - target_height) // 2
            cropped_clip = clip.crop(y1=crop_y, y2=crop_y + target_height)
        
        return cropped_clip
    
    def _detect_faces_in_clip(self, clip, sample_frames: int = 5) -> list:
        """Detect faces in sample frames of the clip"""
        face_positions = []
        duration = clip.duration
        
        try:
            for i in range(sample_frames):
                # Sample frame at different time points
                time_point = (i + 1) * duration / (sample_frames + 1)
                frame = clip.get_frame(time_point)
                
                # Convert BGR to RGB (face_recognition expects RGB)
                rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
                
                # Detect faces
                face_locations = face_recognition.face_locations(rgb_frame)
                
                for face_location in face_locations:
                    top, right, bottom, left = face_location
                    center_x = (left + right) // 2
                    center_y = (top + bottom) // 2
                    face_positions.append((center_x, center_y, time_point))
            
        except Exception as e:
            logger.debug(f"Face detection failed: {str(e)}")
        
        return face_positions
    
    def _calculate_crop_position(self, face_positions: list, video_width: int, 
                               target_width: int) -> int:
        """Calculate optimal crop position based on face positions"""
        if not face_positions:
            return (video_width - target_width) // 2
        
        # Calculate average face position
        avg_x = sum(pos[0] for pos in face_positions) / len(face_positions)
        
        # Center crop around average face position
        crop_x = int(avg_x - target_width // 2)
        
        # Ensure crop position is within bounds
        crop_x = max(0, min(crop_x, video_width - target_width))
        
        return crop_x
    
    def _generate_thumbnail(self, video_path: str) -> str:
        """Generate thumbnail for the clip"""
        try:
            thumbnail_path = video_path.replace('.mp4', '_thumb.jpg')
            
            # Load video and extract frame at 25% duration
            video = VideoFileClip(video_path)
            frame_time = video.duration * 0.25
            frame = video.get_frame(frame_time)
            
            # Convert to PIL Image and save
            from PIL import Image
            img = Image.fromarray(frame.astype('uint8'))
            img.thumbnail((320, 568))  # 9:16 aspect ratio thumbnail
            img.save(thumbnail_path, 'JPEG', quality=85)
            
            video.close()
            return thumbnail_path
            
        except Exception as e:
            logger.warning(f"Failed to generate thumbnail: {str(e)}")
            return ""
    
    async def add_effects(self, video_path: str, effects: dict) -> str:
        """Add effects like zoom, transitions, etc."""
        try:
            loop = asyncio.get_event_loop()
            processed_path = await loop.run_in_executor(
                None, self._add_effects_sync, video_path, effects
            )
            return processed_path
        except Exception as e:
            logger.error(f"Error adding effects: {str(e)}")
            return video_path  # Return original if effects fail
    
    def _add_effects_sync(self, video_path: str, effects: dict) -> str:
        """Add effects synchronously"""
        try:
            video = VideoFileClip(video_path)
            
            # Apply zoom effect if requested
            if effects.get('zoom', False):
                video = video.resize(lambda t: 1 + 0.02 * t)  # Gradual zoom
            
            # Apply fade in/out
            if effects.get('fade', True):
                video = video.fadein(0.5).fadeout(0.5)
            
            # Save processed video
            output_path = video_path.replace('.mp4', '_processed.mp4')
            video.write_videofile(
                output_path,
                codec='libx264',
                audio_codec='aac',
                verbose=False,
                logger=None
            )
            
            video.close()
            
            # Replace original file
            os.replace(output_path, video_path)
            return video_path
            
        except Exception as e:
            logger.error(f"Error in sync effects processing: {str(e)}")
            return video_path