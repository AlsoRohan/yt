'use client';

import { useState } from 'react';
import { Play, Download, Share2, Clock } from 'lucide-react';
import { Clip } from '@/types';
import { downloadClip } from '@/utils/api';

interface ClipPreviewProps {
  clip: Clip;
  jobId: string;
  index: number;
}

export default function ClipPreview({ clip, jobId, index }: ClipPreviewProps) {
  const [isDownloading, setIsDownloading] = useState(false);
  const [showPreview, setShowPreview] = useState(false);

  const handleDownload = async () => {
    setIsDownloading(true);
    try {
      await downloadClip(jobId, index);
    } catch (error) {
      console.error('Download failed:', error);
      alert('Download failed. Please try again.');
    } finally {
      setIsDownloading(false);
    }
  };

  const handleShare = async () => {
    if (navigator.share) {
      try {
        await navigator.share({
          title: clip.title,
          text: `Check out this YouTube Short: ${clip.title}`,
          url: window.location.href
        });
      } catch (error) {
        console.log('Share cancelled');
      }
    } else {
      // Fallback: copy to clipboard
      navigator.clipboard.writeText(window.location.href);
      alert('Link copied to clipboard!');
    }
  };

  const formatDuration = (seconds: number) => {
    const mins = Math.floor(seconds / 60);
    const secs = Math.floor(seconds % 60);
    return `${mins}:${secs.toString().padStart(2, '0')}`;
  };

  return (
    <div className="bg-white/5 rounded-xl overflow-hidden shadow-lg hover:shadow-xl transition-all duration-300 hover:scale-105">
      {/* Thumbnail */}
      <div className="relative aspect-[9/16] bg-gray-800">
        {clip.thumbnail ? (
          <img
            src={`/api/thumbnail/${jobId}/${index}`}
            alt={clip.title}
            className="w-full h-full object-cover"
            onError={(e) => {
              // Fallback to placeholder if thumbnail fails to load
              e.currentTarget.style.display = 'none';
            }}
          />
        ) : (
          <div className="w-full h-full flex items-center justify-center bg-gradient-to-br from-purple-600 to-pink-600">
            <Play className="w-16 h-16 text-white opacity-50" />
          </div>
        )}
        
        {/* Play Overlay */}
        <div className="absolute inset-0 bg-black/30 flex items-center justify-center opacity-0 hover:opacity-100 transition-opacity duration-200">
          <button
            onClick={() => setShowPreview(true)}
            className="bg-white/20 backdrop-blur-sm rounded-full p-4 hover:bg-white/30 transition-colors"
          >
            <Play className="w-8 h-8 text-white" />
          </button>
        </div>

        {/* Duration Badge */}
        <div className="absolute top-2 right-2 bg-black/70 rounded-full px-2 py-1 flex items-center">
          <Clock className="w-3 h-3 text-white mr-1" />
          <span className="text-xs text-white font-medium">
            {formatDuration(clip.duration)}
          </span>
        </div>
      </div>

      {/* Content */}
      <div className="p-4">
        <h3 className="text-lg font-semibold text-white mb-2 line-clamp-2">
          {clip.title}
        </h3>
        
        <p className="text-sm text-gray-300 mb-4 line-clamp-3">
          {clip.text}
        </p>

        {/* Actions */}
        <div className="flex space-x-2">
          <button
            onClick={handleDownload}
            disabled={isDownloading}
            className="flex-1 flex items-center justify-center px-3 py-2 bg-gradient-to-r from-purple-600 to-pink-600 text-white rounded-lg hover:from-purple-700 hover:to-pink-700 transition-colors disabled:opacity-50 disabled:cursor-not-allowed"
          >
            {isDownloading ? (
              <>
                <div className="animate-spin rounded-full h-4 w-4 border-b-2 border-white mr-2"></div>
                Downloading...
              </>
            ) : (
              <>
                <Download className="w-4 h-4 mr-2" />
                Download
              </>
            )}
          </button>

          <button
            onClick={handleShare}
            className="px-3 py-2 bg-white/10 hover:bg-white/20 text-white rounded-lg transition-colors"
          >
            <Share2 className="w-4 h-4" />
          </button>
        </div>
      </div>

      {/* Video Preview Modal */}
      {showPreview && (
        <VideoPreviewModal
          clip={clip}
          jobId={jobId}
          index={index}
          onClose={() => setShowPreview(false)}
        />
      )}
    </div>
  );
}

interface VideoPreviewModalProps {
  clip: Clip;
  jobId: string;
  index: number;
  onClose: () => void;
}

function VideoPreviewModal({ clip, jobId, index, onClose }: VideoPreviewModalProps) {
  return (
    <div className="fixed inset-0 bg-black/80 flex items-center justify-center z-50 p-4">
      <div className="bg-white/10 backdrop-blur-md rounded-2xl overflow-hidden max-w-md w-full">
        {/* Header */}
        <div className="flex items-center justify-between p-4 border-b border-white/10">
          <h3 className="text-lg font-semibold text-white truncate">
            {clip.title}
          </h3>
          <button
            onClick={onClose}
            className="text-gray-400 hover:text-white transition-colors"
          >
            ✕
          </button>
        </div>

        {/* Video Player */}
        <div className="aspect-[9/16] bg-black">
          <video
            controls
            autoPlay
            className="w-full h-full"
            src={`/api/download/${jobId}/${index}`}
          >
            Your browser does not support the video tag.
          </video>
        </div>

        {/* Footer */}
        <div className="p-4">
          <p className="text-sm text-gray-300 mb-4">
            {clip.text}
          </p>
          
          <div className="flex space-x-2">
            <button
              onClick={async () => {
                await downloadClip(jobId, index);
              }}
              className="flex-1 flex items-center justify-center px-4 py-2 bg-gradient-to-r from-purple-600 to-pink-600 text-white rounded-lg hover:from-purple-700 hover:to-pink-700 transition-colors"
            >
              <Download className="w-4 h-4 mr-2" />
              Download
            </button>
            
            <button
              onClick={onClose}
              className="px-4 py-2 bg-white/10 hover:bg-white/20 text-white rounded-lg transition-colors"
            >
              Close
            </button>
          </div>
        </div>
      </div>
    </div>
  );
}