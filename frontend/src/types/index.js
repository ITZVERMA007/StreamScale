// Job state constants
export const JOB_STATES = {
  PENDING: 'PENDING',
  STARTED: 'STARTED',
  PROGRESS: 'PROGRESS',
  SUCCESS: 'SUCCESS',
  FAILURE: 'FAILURE',
  RETRY: 'RETRY'
};

// Available resolutions
export const RESOLUTIONS = [
  { label: '360p', height: 360, key: '360p' },
  { label: '720p', height: 720, key: '720p' },
  { label: '1080p', height: 1080, key: '1080p' },
];

// File validation constants
export const ALLOWED_FILE_TYPES = ['video/mp4', 'video/x-matroska', 'video/quicktime', 'video/webm'];
export const ALLOWED_EXTENSIONS = ['.mp4', '.mkv', '.mov', '.webm'];
export const MAX_FILE_SIZE = 2 * 1024 * 1024 * 1024; // 2GB
