import os
import asyncio
from typing import List, Dict
import logging
from moviepy.editor import VideoFileClip, CompositeVideoClip, TextClip
import pysrt

logger = logging.getLogger(__name__)

class SubtitleGenerator:
    def __init__(self):
        self.default_style = {
            'fontsize': 40,
            'color': 'white',
            'font': 'Arial-Bold',
            'stroke_color': 'black',
            'stroke_width': 2,
            'method': 'caption'
        }
    
    async def add_subtitles(self, video_path: str, transcription_segment: str,
                           start_time: float, end_time: float, 
                           style: dict = None) -> str:
        """Add subtitles to a video clip"""
        try:
            if style is None:
                style = self.default_style.copy()
            
            # Run subtitle generation in thread pool
            loop = asyncio.get_event_loop()
            subtitled_path = await loop.run_in_executor(
                None, self._add_subtitles_sync, video_path, transcription_segment,
                start_time, end_time, style
            )
            
            return subtitled_path
            
        except Exception as e:
            logger.error(f"Error adding subtitles: {str(e)}")
            return video_path  # Return original if subtitle addition fails
    
    def _add_subtitles_sync(self, video_path: str, transcription_segment: str,
                           start_time: float, end_time: float, style: dict) -> str:
        """Add subtitles synchronously"""
        try:
            # Load video
            video = VideoFileClip(video_path)
            duration = video.duration
            
            # Split text into chunks for better readability
            text_chunks = self._split_text_into_chunks(transcription_segment, max_chars=40)
            
            # Create subtitle clips
            subtitle_clips = []
            chunk_duration = duration / len(text_chunks) if text_chunks else duration
            
            for i, chunk in enumerate(text_chunks):
                if not chunk.strip():
                    continue
                
                # Calculate timing for this chunk
                chunk_start = i * chunk_duration
                chunk_end = min((i + 1) * chunk_duration, duration)
                
                # Create text clip with styling
                txt_clip = TextClip(
                    chunk.strip(),
                    fontsize=style['fontsize'],
                    color=style['color'],
                    font=style['font'],
                    stroke_color=style.get('stroke_color'),
                    stroke_width=style.get('stroke_width', 0),
                    method=style.get('method', 'caption')
                ).set_start(chunk_start).set_duration(chunk_end - chunk_start)
                
                # Position subtitle at bottom of screen
                txt_clip = txt_clip.set_position(('center', 'bottom')).set_margin(40)
                
                subtitle_clips.append(txt_clip)
            
            # Composite video with subtitles
            if subtitle_clips:
                final_video = CompositeVideoClip([video] + subtitle_clips)
            else:
                final_video = video
            
            # Generate output path
            output_path = video_path.replace('.mp4', '_subtitled.mp4')
            
            # Write final video
            final_video.write_videofile(
                output_path,
                codec='libx264',
                audio_codec='aac',
                temp_audiofile='temp-audio.m4a',
                remove_temp=True,
                verbose=False,
                logger=None
            )
            
            # Clean up
            final_video.close()
            video.close()
            
            # Replace original file
            os.replace(output_path, video_path)
            return video_path
            
        except Exception as e:
            logger.error(f"Error in sync subtitle addition: {str(e)}")
            return video_path
    
    def _split_text_into_chunks(self, text: str, max_chars: int = 40) -> List[str]:
        """Split text into readable chunks"""
        words = text.split()
        chunks = []
        current_chunk = ""
        
        for word in words:
            if len(current_chunk + " " + word) <= max_chars:
                current_chunk += (" " + word) if current_chunk else word
            else:
                if current_chunk:
                    chunks.append(current_chunk)
                current_chunk = word
        
        if current_chunk:
            chunks.append(current_chunk)
        
        return chunks
    
    async def create_srt_file(self, transcription: List[Dict], output_path: str) -> str:
        """Create SRT subtitle file from transcription"""
        try:
            loop = asyncio.get_event_loop()
            srt_path = await loop.run_in_executor(
                None, self._create_srt_sync, transcription, output_path
            )
            return srt_path
        except Exception as e:
            logger.error(f"Error creating SRT file: {str(e)}")
            return ""
    
    def _create_srt_sync(self, transcription: List[Dict], output_path: str) -> str:
        """Create SRT file synchronously"""
        try:
            subs = pysrt.SubRipFile()
            
            for i, segment in enumerate(transcription):
                start_time = self._seconds_to_srt_time(segment['start'])
                end_time = self._seconds_to_srt_time(segment['end'])
                
                sub = pysrt.SubRipItem(
                    index=i + 1,
                    start=start_time,
                    end=end_time,
                    text=segment['text'].strip()
                )
                subs.append(sub)
            
            # Ensure output directory exists
            os.makedirs(os.path.dirname(output_path), exist_ok=True)
            
            # Save SRT file
            subs.save(output_path, encoding='utf-8')
            return output_path
            
        except Exception as e:
            logger.error(f"Error creating SRT file: {str(e)}")
            return ""
    
    def _seconds_to_srt_time(self, seconds: float):
        """Convert seconds to SRT time format"""
        hours = int(seconds // 3600)
        minutes = int((seconds % 3600) // 60)
        secs = int(seconds % 60)
        milliseconds = int((seconds % 1) * 1000)
        
        return pysrt.SubRipTime(hours, minutes, secs, milliseconds)
    
    async def add_animated_subtitles(self, video_path: str, transcription_segment: str,
                                   start_time: float, end_time: float) -> str:
        """Add animated subtitles with word-by-word appearance"""
        try:
            loop = asyncio.get_event_loop()
            animated_path = await loop.run_in_executor(
                None, self._add_animated_subtitles_sync, video_path, 
                transcription_segment, start_time, end_time
            )
            return animated_path
        except Exception as e:
            logger.error(f"Error adding animated subtitles: {str(e)}")
            return video_path
    
    def _add_animated_subtitles_sync(self, video_path: str, transcription_segment: str,
                                   start_time: float, end_time: float) -> str:
        """Add animated subtitles synchronously"""
        try:
            video = VideoFileClip(video_path)
            duration = video.duration
            
            words = transcription_segment.split()
            if not words:
                return video_path
            
            # Calculate timing for each word
            word_duration = duration / len(words)
            
            subtitle_clips = []
            
            for i, word in enumerate(words):
                # Create individual word clip
                word_start = i * word_duration
                word_end = min((i + 1) * word_duration, duration)
                
                # Highlight current word
                current_text = " ".join(words[:i+1])
                
                txt_clip = TextClip(
                    current_text,
                    fontsize=self.default_style['fontsize'],
                    color='yellow' if i == len(words) - 1 else 'white',
                    font=self.default_style['font'],
                    stroke_color='black',
                    stroke_width=2,
                    method='caption'
                ).set_start(word_start).set_duration(word_end - word_start)
                
                txt_clip = txt_clip.set_position(('center', 'bottom')).set_margin(40)
                subtitle_clips.append(txt_clip)
            
            # Composite video with animated subtitles
            final_video = CompositeVideoClip([video] + subtitle_clips)
            
            # Generate output path
            output_path = video_path.replace('.mp4', '_animated_subs.mp4')
            
            # Write final video
            final_video.write_videofile(
                output_path,
                codec='libx264',
                audio_codec='aac',
                verbose=False,
                logger=None
            )
            
            # Clean up
            final_video.close()
            video.close()
            
            # Replace original file
            os.replace(output_path, video_path)
            return video_path
            
        except Exception as e:
            logger.error(f"Error in animated subtitle creation: {str(e)}")
            return video_path
    
    def get_subtitle_styles(self) -> Dict[str, dict]:
        """Get available subtitle styles"""
        return {
            'default': self.default_style,
            'bold_yellow': {
                'fontsize': 45,
                'color': 'yellow',
                'font': 'Arial-Bold',
                'stroke_color': 'black',
                'stroke_width': 3,
                'method': 'caption'
            },
            'modern': {
                'fontsize': 38,
                'color': 'white',
                'font': 'Helvetica-Bold',
                'stroke_color': 'black',
                'stroke_width': 1,
                'method': 'caption'
            },
            'gaming': {
                'fontsize': 42,
                'color': 'lime',
                'font': 'Arial-Bold',
                'stroke_color': 'darkgreen',
                'stroke_width': 2,
                'method': 'caption'
            }
        }