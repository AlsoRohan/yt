# 🎬 YouTube Shorts Generator

Transform your long-form YouTube videos into engaging vertical Shorts automatically using AI-powered highlight detection, auto-framing, and subtitle generation.

## ✨ Features

### 🤖 AI-Powered Processing
- **Smart Highlight Detection**: Uses advanced algorithms to identify the most engaging segments
- **Audio Analysis**: Detects audio spikes, speaking patterns, and emotional content
- **Keyword Recognition**: Identifies important phrases and engaging content
- **Scene Change Detection**: Recognizes visual transitions and cuts

### 📱 Auto-Framing
- **Intelligent Cropping**: Converts 16:9 videos to 9:16 format automatically
- **Face Detection**: Uses AI to track faces and center them in the frame
- **Smart Composition**: Maintains visual focus on the most important elements

### 💬 Subtitle Generation
- **Whisper Integration**: High-accuracy speech-to-text transcription
- **Styled Subtitles**: Customizable fonts, colors, and animations
- **Multi-language Support**: Automatic language detection
- **Speaker Emphasis**: Bold text and highlighting for key phrases

### 🎨 Video Enhancement
- **Multiple Clips**: Generate up to 5 shorts per long video
- **Custom Duration**: 30, 45, or 60-second clips
- **Quality Optimization**: Maintains video quality during processing
- **Thumbnail Generation**: Automatic thumbnail creation for previews

## 🚀 Quick Start

### Using Docker (Recommended)

1. **Clone the repository**
   ```bash
   git clone <repository-url>
   cd youtube-shorts-generator
   ```

2. **Run with Docker Compose**
   ```bash
   docker-compose up --build
   ```

3. **Access the application**
   - Open http://localhost:3000 in your browser
   - The API documentation is available at http://localhost:3000/docs

### Development Setup

1. **Backend Setup**
   ```bash
   cd backend
   pip install -r ../requirements.txt
   uvicorn main:app --reload --port 8000
   ```

2. **Frontend Setup**
   ```bash
   cd frontend
   npm install
   npm run dev
   ```

3. **Access the application**
   - Frontend: http://localhost:3001
   - Backend API: http://localhost:8000

## 📋 Requirements

### System Dependencies
- Python 3.11+
- Node.js 18+
- FFmpeg
- OpenCV dependencies

### Python Packages
- FastAPI
- Whisper (OpenAI)
- MoviePy
- OpenCV
- yt-dlp
- face-recognition
- scikit-learn
- librosa

### Node.js Packages
- Next.js 14
- React 18
- Tailwind CSS
- Lucide React
- Axios

## 🛠️ Usage

### Web Interface

1. **Upload Video**
   - Paste a YouTube URL
   - Configure settings (optional):
     - Number of clips (1-5)
     - Clip duration (30-60 seconds)
     - Enable/disable subtitles
     - Enable/disable auto-framing

2. **Processing**
   - Monitor real-time progress
   - View processing steps:
     - Video download
     - Audio transcription
     - Highlight analysis
     - Clip generation

3. **Download Results**
   - Preview generated clips
   - Download individual shorts
   - Share clips directly

### API Usage

```python
import requests

# Start processing
response = requests.post('http://localhost:8000/generate-shorts', json={
    'youtube_url': 'https://www.youtube.com/watch?v=VIDEO_ID',
    'max_clips': 3,
    'clip_duration': 45,
    'include_subtitles': True,
    'auto_frame': True
})

job_id = response.json()['job_id']

# Check status
status = requests.get(f'http://localhost:8000/status/{job_id}').json()

# Download clip
clip_data = requests.get(f'http://localhost:8000/download/{job_id}/0')
```

## 🏗️ Architecture

```
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│   Frontend      │    │   Backend       │    │   Services      │
│   (Next.js)     │───▶│   (FastAPI)     │───▶│                 │
│                 │    │                 │    │ • YouTube DL    │
│ • React UI      │    │ • REST API      │    │ • Job Queue     │
│ • Video Preview │    │ • Progress      │    │ • OpenCV        │
│ • Progress      │    │ • File Serving  │    │ • MoviePy       │
│ • Downloads     │    │                 │    │ • Face Recog    │
└─────────────────┘    └─────────────────┘    └─────────────────┘
```

## 🔧 Configuration

### Environment Variables

```bash
# Backend
PYTHONPATH=/app
WHISPER_MODEL=base  # tiny, base, small, medium, large

# Frontend
NEXT_PUBLIC_API_URL=http://localhost:8000
NODE_ENV=production
```

### Advanced Settings

```python
# backend/config.py
class Settings:
    MAX_VIDEO_DURATION = 3600  # 1 hour
    MAX_CLIPS_PER_VIDEO = 5
    DEFAULT_CLIP_DURATION = 45
    WHISPER_MODEL = "base"
    FACE_DETECTION_ENABLED = True
    SUBTITLE_STYLES = {
        "default": {...},
        "bold_yellow": {...}
    }
```

## 📊 Performance

### Processing Times (Approximate)
- **10-minute video**: 2-3 minutes
- **30-minute video**: 5-8 minutes  
- **60-minute video**: 10-15 minutes

### Resource Usage
- **RAM**: 2-4 GB during processing
- **Storage**: ~2x original video size
- **CPU**: Multi-threaded processing

## 🐳 Deployment

### Docker Production

```bash
# Build and run production container
docker build -t youtube-shorts-generator .
docker run -p 80:80 -v $(pwd)/data:/app/data youtube-shorts-generator
```

### Cloud Deployment

The application is ready for deployment on:
- **Render**: Use the included `render.yaml`
- **Railway**: Direct Docker deployment
- **DigitalOcean**: Docker droplet
- **AWS/GCP**: Container services

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests if applicable
5. Submit a pull request

## 📝 License

This project is licensed under the MIT License - see the LICENSE file for details.

## ⚠️ Disclaimer

This tool is for educational and personal use. Please respect YouTube's Terms of Service and copyright laws. Only process videos you have permission to use.

## 🆘 Support

- **Issues**: GitHub Issues
- **Discussions**: GitHub Discussions
- **Documentation**: `/docs` endpoint when running

## 🎯 Roadmap

- [ ] Batch processing multiple videos
- [ ] Custom subtitle styles editor
- [ ] Background music integration
- [ ] Direct YouTube upload
- [ ] Advanced AI models (GPT-4V)
- [ ] Mobile app
- [ ] Cloud storage integration
- [ ] Analytics dashboard

---

Built with ❤️ using FastAPI, Next.js, and cutting-edge AI technologies.