import { motion } from 'framer-motion';
import { Download, Play, Film } from 'lucide-react';
import { useState } from 'react';
import { getDownloadUrl } from '../services/api';
import { cn } from '../utils/helpers';

export default function ResolutionCard({ 
  resolution, 
  filename, 
  available,
  index 
}) {
  const [showPreview, setShowPreview] = useState(false);

  const handleDownload = () => {
    if (filename) {
      window.open(getDownloadUrl(filename), '_blank');
    }
  };

  const resolutionColors = {
    '360p': 'from-green-500/20 to-green-600/20 border-green-500/30',
    '720p': 'from-blue-500/20 to-blue-600/20 border-blue-500/30',
    '1080p': 'from-purple-500/20 to-purple-600/20 border-purple-500/30',
  };

  const resolutionBadgeColors = {
    '360p': 'bg-green-500/10 text-green-400',
    '720p': 'bg-blue-500/10 text-blue-400',
    '1080p': 'bg-purple-500/10 text-purple-400',
  };

  return (
    <motion.div
      initial={{ opacity: 0, y: 20 }}
      animate={{ opacity: 1, y: 0 }}
      transition={{ delay: index * 0.1 }}
      className={cn(
        'relative bg-gradient-to-br rounded-2xl border overflow-hidden',
        available 
          ? resolutionColors[resolution] 
          : 'from-dark-card to-dark-card border-dark-border'
      )}
    >
      <div className="relative p-6">
        {/* Resolution Badge */}
        <div className="flex items-center justify-between mb-4">
          <span className={cn(
            'px-3 py-1.5 rounded-lg text-sm font-semibold font-mono',
            available 
              ? resolutionBadgeColors[resolution]
              : 'bg-gray-700/50 text-gray-400'
          )}>
            {resolution}
          </span>
          
          {available && (
            <div className="flex items-center gap-1">
              <div className="w-2 h-2 bg-green-500 rounded-full animate-pulse" />
              <span className="text-xs text-gray-400">Ready</span>
            </div>
          )}
        </div>

        {/* Icon */}
        <div className="mb-6">
          <div className={cn(
            'w-16 h-16 rounded-xl flex items-center justify-center',
            available ? 'bg-white/5' : 'bg-gray-800/30'
          )}>
            <Film className={cn(
              'w-8 h-8',
              available ? 'text-white' : 'text-gray-600'
            )} />
          </div>
        </div>

        {/* Info */}
        <div className="mb-6">
          <h3 className={cn(
            'text-lg font-semibold mb-1',
            available ? 'text-white' : 'text-gray-500'
          )}>
            {resolution} Quality
          </h3>
          <p className={cn(
            'text-sm',
            available ? 'text-gray-400' : 'text-gray-600'
          )}>
            {available ? 'Transcoding complete' : 'Not yet processed'}
          </p>
        </div>

        {/* Actions */}
        <div className="flex gap-2">
          {available && filename ? (
            <>
              <button
                onClick={handleDownload}
                className="flex-1 flex items-center justify-center gap-2 px-4 py-3 bg-white/10 hover:bg-white/15 text-white rounded-lg font-medium transition-all"
              >
                <Download className="w-4 h-4" />
                Download
              </button>
              <button
                onClick={() => setShowPreview(!showPreview)}
                className="px-4 py-3 bg-white/5 hover:bg-white/10 text-white rounded-lg transition-all"
                title="Preview"
              >
                <Play className="w-4 h-4" />
              </button>
            </>
          ) : (
            <button
              disabled
              className="flex-1 px-4 py-3 bg-gray-800/30 text-gray-600 rounded-lg font-medium cursor-not-allowed"
            >
              Unavailable
            </button>
          )}
        </div>

        {/* Preview Player */}
        {showPreview && available && filename && (
          <motion.div
            initial={{ opacity: 0, height: 0 }}
            animate={{ opacity: 1, height: 'auto' }}
            exit={{ opacity: 0, height: 0 }}
            className="mt-4 pt-4 border-t border-white/10"
          >
            <video
              controls
              className="w-full rounded-lg"
              src={getDownloadUrl(filename)}
            >
              Your browser does not support the video tag.
            </video>
          </motion.div>
        )}
      </div>

      {/* Decorative gradient overlay */}
      {available && (
        <div className="absolute inset-0 bg-gradient-to-t from-black/20 to-transparent pointer-events-none" />
      )}
    </motion.div>
  );
}
