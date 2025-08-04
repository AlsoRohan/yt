'use client';

import { useState } from 'react';
import VideoUploader from '@/components/VideoUploader';
import ProcessingStatus from '@/components/ProcessingStatus';
import ClipPreview from '@/components/ClipPreview';
import { Clip, JobStatus } from '@/types';

export default function Home() {
  const [jobId, setJobId] = useState<string>('');
  const [status, setStatus] = useState<JobStatus | null>(null);
  const [clips, setClips] = useState<Clip[]>([]);

  const handleJobStarted = (id: string) => {
    setJobId(id);
    setStatus(null);
    setClips([]);
  };

  const handleStatusUpdate = (newStatus: JobStatus) => {
    setStatus(newStatus);
    if (newStatus.clips) {
      setClips(newStatus.clips);
    }
  };

  const handleReset = () => {
    setJobId('');
    setStatus(null);
    setClips([]);
  };

  return (
    <div className="min-h-screen bg-gradient-to-br from-purple-900 via-blue-900 to-indigo-900">
      <div className="container mx-auto px-4 py-8">
        {/* Header */}
        <div className="text-center mb-12">
          <h1 className="text-5xl font-bold text-white mb-4">
            🎬 YouTube Shorts Generator
          </h1>
          <p className="text-xl text-gray-300 max-w-3xl mx-auto">
            Transform your long-form YouTube videos into engaging vertical Shorts automatically. 
            Just paste a YouTube URL and let AI do the magic!
          </p>
        </div>

        {/* Main Content */}
        <div className="max-w-6xl mx-auto">
          {!jobId ? (
            /* Upload Section */
            <div className="bg-white/10 backdrop-blur-md rounded-2xl p-8 shadow-2xl">
              <VideoUploader onJobStarted={handleJobStarted} />
            </div>
          ) : (
            /* Processing/Results Section */
            <div className="space-y-8">
              {/* Status Section */}
              <div className="bg-white/10 backdrop-blur-md rounded-2xl p-6 shadow-2xl">
                <ProcessingStatus 
                  jobId={jobId}
                  onStatusUpdate={handleStatusUpdate}
                  onReset={handleReset}
                />
              </div>

              {/* Results Section */}
              {clips.length > 0 && (
                <div className="bg-white/10 backdrop-blur-md rounded-2xl p-8 shadow-2xl">
                  <h2 className="text-3xl font-bold text-white mb-6 text-center">
                    🎯 Generated Shorts
                  </h2>
                  <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
                    {clips.map((clip, index) => (
                      <ClipPreview 
                        key={index}
                        clip={clip}
                        jobId={jobId}
                        index={index}
                      />
                    ))}
                  </div>
                </div>
              )}
            </div>
          )}
        </div>

        {/* Features Section */}
        <div className="mt-16 max-w-6xl mx-auto">
          <h2 className="text-3xl font-bold text-white text-center mb-12">
            ✨ Features
          </h2>
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
            <div className="bg-white/10 backdrop-blur-md rounded-xl p-6 text-center">
              <div className="text-4xl mb-4">🤖</div>
              <h3 className="text-xl font-semibold text-white mb-2">AI-Powered</h3>
              <p className="text-gray-300">Smart highlight detection using advanced AI algorithms</p>
            </div>
            <div className="bg-white/10 backdrop-blur-md rounded-xl p-6 text-center">
              <div className="text-4xl mb-4">📱</div>
              <h3 className="text-xl font-semibold text-white mb-2">Auto-Framing</h3>
              <p className="text-gray-300">Automatic conversion to vertical 9:16 format</p>
            </div>
            <div className="bg-white/10 backdrop-blur-md rounded-xl p-6 text-center">
              <div className="text-4xl mb-4">💬</div>
              <h3 className="text-xl font-semibold text-white mb-2">Subtitles</h3>
              <p className="text-gray-300">Auto-generated styled subtitles with speaker emphasis</p>
            </div>
            <div className="bg-white/10 backdrop-blur-md rounded-xl p-6 text-center">
              <div className="text-4xl mb-4">⚡</div>
              <h3 className="text-xl font-semibold text-white mb-2">Fast Processing</h3>
              <p className="text-gray-300">Quick generation with real-time progress updates</p>
            </div>
          </div>
        </div>

        {/* Footer */}
        <div className="mt-16 text-center text-gray-400">
          <p>Built with ❤️ using FastAPI, Next.js, and AI</p>
        </div>
      </div>
    </div>
  );
}