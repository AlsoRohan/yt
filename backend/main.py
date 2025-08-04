from fastapi import FastAPI, HTTPException, BackgroundTasks, UploadFile, File
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse
from pydantic import BaseModel
import os
import uuid
import asyncio
from typing import List, Optional
import logging

from services.video_processor import VideoProcessor
from services.youtube_downloader import YouTubeDownloader
from services.transcription_service import TranscriptionService
from services.highlight_detector import HighlightDetector
from services.clip_generator import ClipGenerator
from services.subtitle_generator import SubtitleGenerator

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI(title="YouTube Shorts Generator", version="1.0.0")

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Initialize services
video_processor = VideoProcessor()
youtube_downloader = YouTubeDownloader()
transcription_service = TranscriptionService()
highlight_detector = HighlightDetector()
clip_generator = ClipGenerator()
subtitle_generator = SubtitleGenerator()

# Pydantic models
class VideoRequest(BaseModel):
    youtube_url: str
    max_clips: Optional[int] = 3
    clip_duration: Optional[int] = 45
    include_subtitles: Optional[bool] = True
    auto_frame: Optional[bool] = True

class ProcessingStatus(BaseModel):
    job_id: str
    status: str
    progress: int
    message: str
    clips: Optional[List[dict]] = None

# In-memory job storage (use Redis in production)
jobs = {}

@app.get("/")
async def root():
    return {"message": "YouTube Shorts Generator API"}

@app.post("/generate-shorts")
async def generate_shorts(request: VideoRequest, background_tasks: BackgroundTasks):
    """Generate YouTube Shorts from a long-form video"""
    job_id = str(uuid.uuid4())
    
    # Initialize job status
    jobs[job_id] = {
        "status": "started",
        "progress": 0,
        "message": "Initializing...",
        "clips": []
    }
    
    # Start background processing
    background_tasks.add_task(process_video, job_id, request)
    
    return {"job_id": job_id, "message": "Processing started"}

@app.get("/status/{job_id}")
async def get_status(job_id: str):
    """Get processing status for a job"""
    if job_id not in jobs:
        raise HTTPException(status_code=404, detail="Job not found")
    
    return ProcessingStatus(job_id=job_id, **jobs[job_id])

@app.get("/download/{job_id}/{clip_index}")
async def download_clip(job_id: str, clip_index: int):
    """Download a generated clip"""
    if job_id not in jobs:
        raise HTTPException(status_code=404, detail="Job not found")
    
    job = jobs[job_id]
    if clip_index >= len(job["clips"]):
        raise HTTPException(status_code=404, detail="Clip not found")
    
    clip_path = job["clips"][clip_index]["file_path"]
    if not os.path.exists(clip_path):
        raise HTTPException(status_code=404, detail="Clip file not found")
    
    return FileResponse(
        clip_path,
        media_type="video/mp4",
        filename=f"short_{job_id}_{clip_index}.mp4"
    )

async def process_video(job_id: str, request: VideoRequest):
    """Background task to process video and generate shorts"""
    try:
        # Update status: Downloading video
        jobs[job_id].update({
            "status": "downloading",
            "progress": 10,
            "message": "Downloading video from YouTube..."
        })
        
        # Download video
        video_path = await youtube_downloader.download(request.youtube_url)
        
        # Update status: Transcribing
        jobs[job_id].update({
            "status": "transcribing",
            "progress": 25,
            "message": "Transcribing audio..."
        })
        
        # Transcribe video
        transcription = await transcription_service.transcribe(video_path)
        
        # Update status: Analyzing highlights
        jobs[job_id].update({
            "status": "analyzing",
            "progress": 40,
            "message": "Detecting engaging segments..."
        })
        
        # Detect highlights
        highlights = await highlight_detector.detect_highlights(
            video_path, transcription, max_clips=request.max_clips
        )
        
        # Update status: Generating clips
        jobs[job_id].update({
            "status": "generating",
            "progress": 60,
            "message": "Generating short clips..."
        })
        
        # Generate clips
        clips = []
        for i, highlight in enumerate(highlights):
            clip_path = await clip_generator.create_clip(
                video_path=video_path,
                start_time=highlight["start_time"],
                end_time=highlight["end_time"],
                output_path=f"outputs/{job_id}_clip_{i}.mp4",
                auto_frame=request.auto_frame,
                target_duration=request.clip_duration
            )
            
            # Add subtitles if requested
            if request.include_subtitles:
                clip_path = await subtitle_generator.add_subtitles(
                    video_path=clip_path,
                    transcription_segment=highlight["text"],
                    start_time=highlight["start_time"],
                    end_time=highlight["end_time"]
                )
            
            clips.append({
                "index": i,
                "title": highlight.get("title", f"Short {i+1}"),
                "duration": highlight["end_time"] - highlight["start_time"],
                "file_path": clip_path,
                "thumbnail": f"outputs/{job_id}_clip_{i}_thumb.jpg",
                "text": highlight["text"][:100] + "..." if len(highlight["text"]) > 100 else highlight["text"]
            })
            
            # Update progress
            progress = 60 + (30 * (i + 1) / len(highlights))
            jobs[job_id].update({
                "progress": int(progress),
                "message": f"Generated clip {i+1}/{len(highlights)}"
            })
        
        # Update status: Complete
        jobs[job_id].update({
            "status": "completed",
            "progress": 100,
            "message": f"Successfully generated {len(clips)} shorts!",
            "clips": clips
        })
        
        # Clean up original video file
        if os.path.exists(video_path):
            os.remove(video_path)
            
    except Exception as e:
        logger.error(f"Error processing video for job {job_id}: {str(e)}")
        jobs[job_id].update({
            "status": "error",
            "progress": 0,
            "message": f"Error: {str(e)}"
        })

@app.on_event("startup")
async def startup_event():
    """Create necessary directories on startup"""
    os.makedirs("downloads", exist_ok=True)
    os.makedirs("outputs", exist_ok=True)
    os.makedirs("temp", exist_ok=True)

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)