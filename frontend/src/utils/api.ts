import { VideoRequest, JobStatus } from '@/types';

const API_BASE_URL = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000';

export async function generateShorts(request: VideoRequest): Promise<{ job_id: string; message: string }> {
  const response = await fetch(`${API_BASE_URL}/generate-shorts`, {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
    },
    body: JSON.stringify(request),
  });

  if (!response.ok) {
    throw new Error(`HTTP error! status: ${response.status}`);
  }

  return response.json();
}

export async function getJobStatus(jobId: string): Promise<JobStatus> {
  const response = await fetch(`${API_BASE_URL}/status/${jobId}`);

  if (!response.ok) {
    throw new Error(`HTTP error! status: ${response.status}`);
  }

  return response.json();
}

export async function downloadClip(jobId: string, clipIndex: number): Promise<void> {
  const response = await fetch(`${API_BASE_URL}/download/${jobId}/${clipIndex}`);

  if (!response.ok) {
    throw new Error(`HTTP error! status: ${response.status}`);
  }

  // Create blob and download
  const blob = await response.blob();
  const url = window.URL.createObjectURL(blob);
  
  // Create temporary download link
  const a = document.createElement('a');
  a.href = url;
  a.download = `short_${jobId}_${clipIndex}.mp4`;
  document.body.appendChild(a);
  a.click();
  
  // Cleanup
  window.URL.revokeObjectURL(url);
  document.body.removeChild(a);
}

export function getThumbnailUrl(jobId: string, clipIndex: number): string {
  return `${API_BASE_URL}/download/${jobId}/${clipIndex}`.replace('.mp4', '_thumb.jpg');
}

export function getVideoUrl(jobId: string, clipIndex: number): string {
  return `${API_BASE_URL}/download/${jobId}/${clipIndex}`;
}