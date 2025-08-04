'use client';

import { useState } from 'react';
import { Upload, Link, Settings } from 'lucide-react';
import { VideoRequest } from '@/types';
import { generateShorts } from '@/utils/api';

interface VideoUploaderProps {
  onJobStarted: (jobId: string) => void;
}

export default function VideoUploader({ onJobStarted }: VideoUploaderProps) {
  const [url, setUrl] = useState('');
  const [isLoading, setIsLoading] = useState(false);
  const [showAdvanced, setShowAdvanced] = useState(false);
  const [settings, setSettings] = useState({
    max_clips: 3,
    clip_duration: 45,
    include_subtitles: true,
    auto_frame: true
  });

  const isValidYouTubeUrl = (url: string) => {
    const patterns = [
      /^https?:\/\/(www\.)?(youtube\.com|youtu\.be)\/.+/,
      /^https?:\/\/(www\.)?youtube\.com\/watch\?v=.+/,
      /^https?:\/\/youtu\.be\/.+/
    ];
    return patterns.some(pattern => pattern.test(url));
  };

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    
    if (!url.trim()) {
      alert('Please enter a YouTube URL');
      return;
    }

    if (!isValidYouTubeUrl(url)) {
      alert('Please enter a valid YouTube URL');
      return;
    }

    setIsLoading(true);

    try {
      const request: VideoRequest = {
        youtube_url: url,
        ...settings
      };

      const response = await generateShorts(request);
      
      if (response.job_id) {
        onJobStarted(response.job_id);
      } else {
        throw new Error('No job ID received');
      }
    } catch (error) {
      console.error('Error starting job:', error);
      alert('Failed to start processing. Please try again.');
    } finally {
      setIsLoading(false);
    }
  };

  return (
    <div className="max-w-2xl mx-auto">
      <div className="text-center mb-8">
        <div className="inline-flex items-center justify-center w-16 h-16 bg-gradient-to-r from-purple-500 to-pink-500 rounded-full mb-4">
          <Upload className="w-8 h-8 text-white" />
        </div>
        <h2 className="text-2xl font-bold text-white mb-2">
          Upload Your YouTube Video
        </h2>
        <p className="text-gray-300">
          Paste a YouTube URL to automatically generate engaging Shorts
        </p>
      </div>

      <form onSubmit={handleSubmit} className="space-y-6">
        {/* URL Input */}
        <div>
          <label htmlFor="url" className="block text-sm font-medium text-gray-300 mb-2">
            YouTube URL
          </label>
          <div className="relative">
            <Link className="absolute left-3 top-1/2 transform -translate-y-1/2 w-5 h-5 text-gray-400" />
            <input
              type="url"
              id="url"
              value={url}
              onChange={(e) => setUrl(e.target.value)}
              placeholder="https://www.youtube.com/watch?v=..."
              className="w-full pl-10 pr-4 py-3 bg-white/10 border border-white/20 rounded-lg text-white placeholder-gray-400 focus:outline-none focus:ring-2 focus:ring-purple-500 focus:border-transparent"
              disabled={isLoading}
            />
          </div>
        </div>

        {/* Advanced Settings Toggle */}
        <div>
          <button
            type="button"
            onClick={() => setShowAdvanced(!showAdvanced)}
            className="flex items-center text-sm text-gray-300 hover:text-white transition-colors"
          >
            <Settings className="w-4 h-4 mr-2" />
            Advanced Settings
            <span className="ml-2 text-xs">
              {showAdvanced ? '▼' : '▶'}
            </span>
          </button>
        </div>

        {/* Advanced Settings */}
        {showAdvanced && (
          <div className="bg-white/5 rounded-lg p-6 space-y-4">
            <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
              {/* Max Clips */}
              <div>
                <label className="block text-sm font-medium text-gray-300 mb-2">
                  Max Clips
                </label>
                <select
                  value={settings.max_clips}
                  onChange={(e) => setSettings({...settings, max_clips: parseInt(e.target.value)})}
                  className="w-full px-3 py-2 bg-white/10 border border-white/20 rounded-lg text-white focus:outline-none focus:ring-2 focus:ring-purple-500"
                >
                  <option value={1}>1 Clip</option>
                  <option value={2}>2 Clips</option>
                  <option value={3}>3 Clips</option>
                  <option value={4}>4 Clips</option>
                  <option value={5}>5 Clips</option>
                </select>
              </div>

              {/* Clip Duration */}
              <div>
                <label className="block text-sm font-medium text-gray-300 mb-2">
                  Clip Duration (seconds)
                </label>
                <select
                  value={settings.clip_duration}
                  onChange={(e) => setSettings({...settings, clip_duration: parseInt(e.target.value)})}
                  className="w-full px-3 py-2 bg-white/10 border border-white/20 rounded-lg text-white focus:outline-none focus:ring-2 focus:ring-purple-500"
                >
                  <option value={30}>30 seconds</option>
                  <option value={45}>45 seconds</option>
                  <option value={60}>60 seconds</option>
                </select>
              </div>
            </div>

            {/* Checkboxes */}
            <div className="space-y-3">
              <label className="flex items-center">
                <input
                  type="checkbox"
                  checked={settings.include_subtitles}
                  onChange={(e) => setSettings({...settings, include_subtitles: e.target.checked})}
                  className="w-4 h-4 text-purple-600 bg-white/10 border-white/20 rounded focus:ring-purple-500"
                />
                <span className="ml-2 text-sm text-gray-300">Include Subtitles</span>
              </label>

              <label className="flex items-center">
                <input
                  type="checkbox"
                  checked={settings.auto_frame}
                  onChange={(e) => setSettings({...settings, auto_frame: e.target.checked})}
                  className="w-4 h-4 text-purple-600 bg-white/10 border-white/20 rounded focus:ring-purple-500"
                />
                <span className="ml-2 text-sm text-gray-300">Auto-Frame to Vertical</span>
              </label>
            </div>
          </div>
        )}

        {/* Submit Button */}
        <button
          type="submit"
          disabled={isLoading || !url.trim()}
          className="w-full py-4 px-6 bg-gradient-to-r from-purple-600 to-pink-600 text-white font-semibold rounded-lg shadow-lg hover:from-purple-700 hover:to-pink-700 focus:outline-none focus:ring-2 focus:ring-purple-500 focus:ring-offset-2 focus:ring-offset-gray-900 disabled:opacity-50 disabled:cursor-not-allowed transition-all duration-200"
        >
          {isLoading ? (
            <div className="flex items-center justify-center">
              <div className="animate-spin rounded-full h-5 w-5 border-b-2 border-white mr-2"></div>
              Starting Processing...
            </div>
          ) : (
            'Generate Shorts 🚀'
          )}
        </button>
      </form>

      {/* Example URLs */}
      <div className="mt-8 p-4 bg-white/5 rounded-lg">
        <h3 className="text-sm font-medium text-gray-300 mb-2">Example URLs:</h3>
        <div className="space-y-1 text-xs text-gray-400">
          <div>• https://www.youtube.com/watch?v=dQw4w9WgXcQ</div>
          <div>• https://youtu.be/dQw4w9WgXcQ</div>
        </div>
      </div>
    </div>
  );
}