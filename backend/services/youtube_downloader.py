import yt_dlp
import os
import asyncio
from typing import Optional
import logging

logger = logging.getLogger(__name__)

class YouTubeDownloader:
    def __init__(self):
        self.download_dir = "downloads"
        os.makedirs(self.download_dir, exist_ok=True)
    
    async def download(self, url: str, quality: str = "best") -> str:
        """Download video from YouTube URL"""
        try:
            # Configure yt-dlp options
            ydl_opts = {
                'format': f'{quality}[ext=mp4]/best[ext=mp4]/best',
                'outtmpl': os.path.join(self.download_dir, '%(title)s.%(ext)s'),
                'noplaylist': True,
                'extract_flat': False,
            }
            
            # Run download in thread pool to avoid blocking
            loop = asyncio.get_event_loop()
            video_path = await loop.run_in_executor(
                None, self._download_sync, url, ydl_opts
            )
            
            return video_path
            
        except Exception as e:
            logger.error(f"Error downloading video: {str(e)}")
            raise Exception(f"Failed to download video: {str(e)}")
    
    def _download_sync(self, url: str, ydl_opts: dict) -> str:
        """Synchronous download function"""
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            # Extract info first
            info = ydl.extract_info(url, download=False)
            title = info.get('title', 'video')
            
            # Sanitize filename
            safe_title = "".join(c for c in title if c.isalnum() or c in (' ', '-', '_')).rstrip()
            safe_title = safe_title[:50]  # Limit length
            
            # Update output template with safe title
            ydl_opts['outtmpl'] = os.path.join(self.download_dir, f'{safe_title}.%(ext)s')
            
            # Download the video
            ydl.download([url])
            
            # Return the downloaded file path
            video_path = os.path.join(self.download_dir, f'{safe_title}.mp4')
            
            # Find the actual downloaded file (in case extension differs)
            for file in os.listdir(self.download_dir):
                if file.startswith(safe_title):
                    video_path = os.path.join(self.download_dir, file)
                    break
            
            return video_path
    
    async def get_video_info(self, url: str) -> dict:
        """Get video information without downloading"""
        try:
            ydl_opts = {
                'quiet': True,
                'no_warnings': True,
            }
            
            loop = asyncio.get_event_loop()
            info = await loop.run_in_executor(
                None, self._get_info_sync, url, ydl_opts
            )
            
            return {
                'title': info.get('title', ''),
                'duration': info.get('duration', 0),
                'description': info.get('description', ''),
                'uploader': info.get('uploader', ''),
                'view_count': info.get('view_count', 0),
                'upload_date': info.get('upload_date', ''),
            }
            
        except Exception as e:
            logger.error(f"Error getting video info: {str(e)}")
            raise Exception(f"Failed to get video info: {str(e)}")
    
    def _get_info_sync(self, url: str, ydl_opts: dict) -> dict:
        """Synchronous info extraction"""
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            return ydl.extract_info(url, download=False)