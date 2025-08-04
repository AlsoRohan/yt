export interface Clip {
  index: number;
  title: string;
  duration: number;
  file_path: string;
  thumbnail: string;
  text: string;
}

export interface JobStatus {
  job_id: string;
  status: 'started' | 'downloading' | 'transcribing' | 'analyzing' | 'generating' | 'completed' | 'error';
  progress: number;
  message: string;
  clips?: Clip[];
}

export interface VideoRequest {
  youtube_url: string;
  max_clips?: number;
  clip_duration?: number;
  include_subtitles?: boolean;
  auto_frame?: boolean;
}

export interface ApiResponse<T = any> {
  success: boolean;
  data?: T;
  error?: string;
}