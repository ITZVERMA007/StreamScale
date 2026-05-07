import { motion } from 'framer-motion';
import { Download, Film, AlertTriangle } from 'lucide-react';
import { cn } from '../utils/helpers';

export default function ResolutionCard({ 
  taskId,
  resolution, 
  filename, 
  taskStatus,
  errorMsg,
  index 
}) {
  const isAvailable = taskStatus === 'COMPLETED';
  const isFailed = taskStatus === 'FAILED';

  const API_BASE_URL = import.meta.env.VITE_API_BASE_URL || '';
  const videoUrl = `${API_BASE_URL}/api/v1/download/${taskId}/${resolution}`;

  const handleDownload = async() => {
    try {
    const response = await fetch(videoUrl);

    if (!response.ok) {
      alert("File not ready yet. Try again.");
      return;
    }

    const contentDisposition = response.headers.get("content-disposition");

    let downloadFilename = "video.mp4"; 
    if (contentDisposition) {
      const match = contentDisposition.match(/filename="?(.+?)"?$/);
      if (match && match[1]) {
        downloadFilename = match[1];
      }
    }

    const blob = await response.blob(); //converts the fetch response to a binary data
    const url = window.URL.createObjectURL(blob);

    const link = document.createElement("a");
    link.href = url;
    link.download = downloadFilename;

    document.body.appendChild(link);
    link.click();

    document.body.removeChild(link);
    window.URL.revokeObjectURL(url);

  } catch (error) {
    console.error("Download failed:", error);
    alert("Something went wrong while downloading.");
  }
  };

  const resolutionColors = {
    '360': 'from-green-500/20 to-green-600/20 border-green-500/30',
    '720': 'from-blue-500/20 to-blue-600/20 border-blue-500/30',
    '1080': 'from-purple-500/20 to-purple-600/20 border-purple-500/30',
  };

  const resolutionBadgeColors = {
    '360': 'bg-green-500/10 text-green-400',
    '720': 'bg-blue-500/10 text-blue-400',
    '1080': 'bg-purple-500/10 text-purple-400',
  };

  return (
    <motion.div
      layout
      initial={{ opacity: 0, y: 20 }}
      animate={{ opacity: 1, y: 0 }}
      transition={{ delay: index * 0.1 }}
      className={cn(
        'relative bg-gradient-to-br rounded-2xl border overflow-hidden',
        isAvailable 
          ? resolutionColors[resolution] 
          : isFailed 
            ? 'from-red-500/10 to-red-600/10 border-red-500/30'
            : 'from-dark-card to-dark-card border-dark-border'
      )}
    >
      <div className="relative p-6">
        <div className="flex items-center justify-between mb-4">
          <span className={cn(
            'px-3 py-1.5 rounded-lg text-sm font-semibold font-mono',
            isAvailable 
              ? resolutionBadgeColors[resolution]
              : isFailed 
                ? 'bg-red-500/10 text-red-400'
                : 'bg-gray-700/50 text-gray-400'
          )}>
            {resolution}p
          </span>
          
          {isAvailable && (
            <div className="flex items-center gap-1">
              <div className="w-2 h-2 bg-green-500 rounded-full animate-pulse" />
              <span className="text-xs text-gray-400">Ready</span>
            </div>
          )}
          {isFailed && (
            <div className="flex items-center gap-1 text-red-400">
              <AlertTriangle className="w-4 h-4" />
              <span className="text-xs">Failed</span>
            </div>
          )}
        </div>

        <div className="mb-6">
          <div className={cn(
            'w-16 h-16 rounded-xl flex items-center justify-center',
            isAvailable ? 'bg-white/5' : isFailed ? 'bg-red-500/10' : 'bg-gray-800/30'
          )}>
            <Film className={cn(
              'w-8 h-8',
              isAvailable ? 'text-white' : isFailed ? 'text-red-400' : 'text-gray-600'
            )} />
          </div>
        </div>

        <div className="mb-6">
          <h3 className={cn(
            'text-lg font-semibold mb-1',
            isAvailable ? 'text-white' : isFailed ? 'text-red-400' : 'text-gray-500'
          )}>
            {resolution}p Quality
          </h3>
          <p className={cn(
            'text-sm',
            isAvailable ? 'text-gray-400' : isFailed ? 'text-red-300' : 'text-gray-600'
          )}>
            {isAvailable ? 'Transcoding complete' : isFailed ? (errorMsg || 'Failed to process') : 'Not yet processed'}
          </p>
        </div>

        <div className="flex gap-2">
          {isAvailable && filename ? (
            <>
              <button onClick={handleDownload} className="flex-1 flex items-center justify-center gap-2 px-4 py-3 bg-white/10 hover:bg-white/15 text-white rounded-lg font-medium transition-all">
                <Download className="w-4 h-4" /> Download
              </button>
            </>
          ) : (
            <button disabled className="flex-1 px-4 py-3 bg-gray-800/30 text-gray-600 rounded-lg font-medium cursor-not-allowed">
              {isFailed ? 'Unavailable' : 'Processing...'}
            </button>
          )}
        </div>
      </div>

      {isAvailable && (
        <div className="absolute inset-0 bg-gradient-to-t from-black/20 to-transparent pointer-events-none" />
      )}
    </motion.div>
  );
}
