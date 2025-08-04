'use client';

import { useState, useEffect } from 'react';
import { RefreshCw, CheckCircle, XCircle, ArrowLeft } from 'lucide-react';
import { JobStatus } from '@/types';
import { getJobStatus } from '@/utils/api';

interface ProcessingStatusProps {
  jobId: string;
  onStatusUpdate: (status: JobStatus) => void;
  onReset: () => void;
}

export default function ProcessingStatus({ jobId, onStatusUpdate, onReset }: ProcessingStatusProps) {
  const [status, setStatus] = useState<JobStatus | null>(null);
  const [isPolling, setIsPolling] = useState(true);

  useEffect(() => {
    let interval: NodeJS.Timeout;

    const pollStatus = async () => {
      try {
        const response = await getJobStatus(jobId);
        setStatus(response);
        onStatusUpdate(response);

        // Stop polling if completed or error
        if (response.status === 'completed' || response.status === 'error') {
          setIsPolling(false);
        }
      } catch (error) {
        console.error('Error fetching status:', error);
        setIsPolling(false);
      }
    };

    if (isPolling) {
      // Poll immediately, then every 2 seconds
      pollStatus();
      interval = setInterval(pollStatus, 2000);
    }

    return () => {
      if (interval) clearInterval(interval);
    };
  }, [jobId, isPolling, onStatusUpdate]);

  const getStatusIcon = (status: string) => {
    switch (status) {
      case 'completed':
        return <CheckCircle className="w-6 h-6 text-green-500" />;
      case 'error':
        return <XCircle className="w-6 h-6 text-red-500" />;
      default:
        return <RefreshCw className="w-6 h-6 text-blue-500 animate-spin" />;
    }
  };

  const getStatusColor = (status: string) => {
    switch (status) {
      case 'completed':
        return 'text-green-400';
      case 'error':
        return 'text-red-400';
      default:
        return 'text-blue-400';
    }
  };

  const getProgressColor = (status: string) => {
    switch (status) {
      case 'completed':
        return 'bg-green-500';
      case 'error':
        return 'bg-red-500';
      default:
        return 'bg-blue-500';
    }
  };

  if (!status) {
    return (
      <div className="text-center">
        <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-white mx-auto mb-4"></div>
        <p className="text-gray-300">Loading status...</p>
      </div>
    );
  }

  return (
    <div className="max-w-2xl mx-auto">
      {/* Header */}
      <div className="flex items-center justify-between mb-6">
        <div className="flex items-center space-x-3">
          {getStatusIcon(status.status)}
          <div>
            <h2 className="text-xl font-semibold text-white">
              Processing Video
            </h2>
            <p className="text-sm text-gray-400">Job ID: {jobId.slice(0, 8)}...</p>
          </div>
        </div>
        
        <button
          onClick={onReset}
          className="flex items-center px-4 py-2 bg-white/10 hover:bg-white/20 rounded-lg text-white transition-colors"
        >
          <ArrowLeft className="w-4 h-4 mr-2" />
          New Video
        </button>
      </div>

      {/* Progress Bar */}
      <div className="mb-6">
        <div className="flex justify-between items-center mb-2">
          <span className={`text-sm font-medium ${getStatusColor(status.status)}`}>
            {status.status.charAt(0).toUpperCase() + status.status.slice(1)}
          </span>
          <span className="text-sm text-gray-400">
            {status.progress}%
          </span>
        </div>
        <div className="w-full bg-gray-700 rounded-full h-3">
          <div
            className={`h-3 rounded-full transition-all duration-500 ${getProgressColor(status.status)}`}
            style={{ width: `${status.progress}%` }}
          ></div>
        </div>
      </div>

      {/* Status Message */}
      <div className="bg-white/5 rounded-lg p-4 mb-6">
        <p className="text-white text-center">{status.message}</p>
      </div>

      {/* Processing Steps */}
      <div className="space-y-3">
        <ProcessingStep 
          title="Downloading Video" 
          status={getStepStatus('downloading', status.status)} 
        />
        <ProcessingStep 
          title="Transcribing Audio" 
          status={getStepStatus('transcribing', status.status)} 
        />
        <ProcessingStep 
          title="Analyzing Highlights" 
          status={getStepStatus('analyzing', status.status)} 
        />
        <ProcessingStep 
          title="Generating Clips" 
          status={getStepStatus('generating', status.status)} 
        />
      </div>

      {/* Completion Message */}
      {status.status === 'completed' && (
        <div className="mt-6 p-4 bg-green-500/20 border border-green-500/30 rounded-lg">
          <div className="flex items-center">
            <CheckCircle className="w-5 h-5 text-green-400 mr-2" />
            <span className="text-green-400 font-medium">
              Processing Complete! 🎉
            </span>
          </div>
          <p className="text-green-300 text-sm mt-1">
            Your shorts are ready for preview and download below.
          </p>
        </div>
      )}

      {/* Error Message */}
      {status.status === 'error' && (
        <div className="mt-6 p-4 bg-red-500/20 border border-red-500/30 rounded-lg">
          <div className="flex items-center">
            <XCircle className="w-5 h-5 text-red-400 mr-2" />
            <span className="text-red-400 font-medium">
              Processing Failed
            </span>
          </div>
          <p className="text-red-300 text-sm mt-1">
            {status.message}
          </p>
          <button
            onClick={onReset}
            className="mt-3 px-4 py-2 bg-red-600 hover:bg-red-700 text-white rounded-lg text-sm transition-colors"
          >
            Try Again
          </button>
        </div>
      )}
    </div>
  );
}

interface ProcessingStepProps {
  title: string;
  status: 'pending' | 'active' | 'completed';
}

function ProcessingStep({ title, status }: ProcessingStepProps) {
  const getStepIcon = () => {
    switch (status) {
      case 'completed':
        return <CheckCircle className="w-5 h-5 text-green-500" />;
      case 'active':
        return <RefreshCw className="w-5 h-5 text-blue-500 animate-spin" />;
      default:
        return <div className="w-5 h-5 rounded-full border-2 border-gray-600"></div>;
    }
  };

  const getStepColor = () => {
    switch (status) {
      case 'completed':
        return 'text-green-400';
      case 'active':
        return 'text-blue-400';
      default:
        return 'text-gray-500';
    }
  };

  return (
    <div className="flex items-center space-x-3">
      {getStepIcon()}
      <span className={`text-sm ${getStepColor()}`}>
        {title}
      </span>
    </div>
  );
}

function getStepStatus(stepName: string, currentStatus: string): 'pending' | 'active' | 'completed' {
  const steps = ['started', 'downloading', 'transcribing', 'analyzing', 'generating', 'completed'];
  const currentIndex = steps.indexOf(currentStatus);
  const stepIndex = steps.indexOf(stepName);

  if (currentStatus === 'error') {
    return stepIndex < currentIndex ? 'completed' : 'pending';
  }

  if (stepIndex < currentIndex) {
    return 'completed';
  } else if (stepIndex === currentIndex) {
    return 'active';
  } else {
    return 'pending';
  }
}