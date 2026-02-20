import { useParams, useNavigate } from 'react-router-dom';
import { motion } from 'framer-motion';
import { ArrowLeft, Sparkles ,AlertTriangle} from 'lucide-react';
import { useTaskStatus } from '../hooks/useTaskStatus';
import ResolutionCard from '../components/ResolutionCard';
import LoadingSpinner from '../components/LoadingSpinner';
import { RESOLUTIONS } from '../types';

export default function ResultsPage() {
  const { taskId } = useParams();
  const navigate = useNavigate();

  const { data: status, isLoading, isError } = useTaskStatus({
    taskId: taskId || null,
  });

  if (isLoading) {
    return (
      <div className="max-w-4xl mx-auto">
        <div className="bg-dark-card border border-dark-border rounded-2xl p-12 text-center">
          <LoadingSpinner size="lg" className="text-accent-primary mx-auto mb-4" />
          <h3 className="text-xl font-semibold text-white mb-2">Loading Results...</h3>
          <p className="text-gray-400">Fetching your transcoded videos</p>
        </div>
      </div>
    );
  }

  if (isError || !status) {
    return (
      <div className="max-w-4xl mx-auto">
        <div className="bg-dark-card border border-dark-border rounded-2xl p-12 text-center">
          <h2 className="text-2xl font-bold text-white mb-2">Error Loading Results</h2>
          <p className="text-gray-400 mb-6">
            Could not fetch results for this task. Please check the task ID.
          </p>
          <button
            onClick={() => navigate('/')}
            className="px-6 py-3 bg-accent-primary hover:bg-accent-primary/90 text-white rounded-lg font-medium transition-colors"
          >
            Upload New Video
          </button>
        </div>
      </div>
    );
  }

  const currentState = status.state?.toUpperCase();
  if (currentState !== 'SUCCESS' && currentState != "COMPLETED" && currentState !== 'PARTIAL_SUCCESS') {
    return (
      <div className="max-w-4xl mx-auto">
        <div className="bg-dark-card border border-dark-border rounded-2xl p-12 text-center">
          <h2 className="text-2xl font-bold text-white mb-2">
            {currentState === 'FAILED' ? 'Transcoding Failed' : 'Transcoding Not Complete'}
          </h2>
          <p className="text-gray-400 mb-6">
            {currentState === 'FAILED'
              ? 'This task failed to process completely. No videos are available.' 
              : "This task hasn't finished processing yet. Please check the status page."}
          </p>
          <button onClick={() => navigate(`/status/${taskId}`)} className="px-6 py-3 bg-accent-primary hover:bg-accent-primary/90 text-white rounded-lg font-medium transition-colors">
            View Status
          </button>
        </div>
      </div>
    );
  }

  const isPartialSuccess = status.state === 'PARTIAL_SUCCESS';

  return (
    <div className="max-w-6xl mx-auto">
      <motion.button onClick={() => navigate('/')} initial={{ opacity: 0, x: -20 }} animate={{ opacity: 1, x: 0 }} className="inline-flex items-center gap-2 text-gray-400 hover:text-white mb-8 transition-colors">
        <ArrowLeft className="w-4 h-4" /> Upload Another Video
      </motion.button>

      <motion.div initial={{ opacity: 0, y: 20 }} animate={{ opacity: 1, y: 0 }} className="text-center mb-12">
        <div className={`inline-flex items-center gap-2 px-4 py-2 border rounded-full text-sm font-medium mb-6 ${
          isPartialSuccess ? 'bg-accent-warning/10 border-accent-warning/20 text-accent-warning' : 'bg-accent-success/10 border-accent-success/20 text-accent-success'
        }`}>
          {isPartialSuccess ? <AlertTriangle className="w-4 h-4" /> : <Sparkles className="w-4 h-4" />}
          {isPartialSuccess ? 'Partial Completion' : 'Transcoding Complete'}
        </div>
        
        <h1 className="text-5xl font-bold text-white mb-4 font-display">
          {isPartialSuccess ? 'Some Videos Are Ready' : 'Your Videos Are Ready'}
        </h1>
        <p className="text-xl text-gray-400 max-w-2xl mx-auto">
          {isPartialSuccess 
            ? 'We encountered an error processing some resolutions, but the successful ones are available below.' 
            : 'Download your transcoded videos in multiple resolutions'}
        </p>
      </motion.div>

      <motion.div initial={{ opacity: 0, y: 20 }} animate={{ opacity: 1, y: 0 }} transition={{ delay: 0.1 }} className="mb-8 p-4 bg-dark-card border border-dark-border rounded-xl">
        <p className="text-sm text-gray-500 mb-1">Task ID</p>
        <code className="text-sm font-mono text-accent-primary">{taskId}</code>
      </motion.div>

      <div className="grid md:grid-cols-3 gap-6 mb-12">
  {status?.details &&
    Object.entries(status.details).map(([resKey, taskDetail], index) => {
      const currentTaskStatus = taskDetail?.status || 'QUEUED';
      const errorMsg = taskDetail?.error || null;

      const filename =
        currentTaskStatus === 'COMPLETED' ? resKey : null;

      return (
        <ResolutionCard
          key={resKey}
          resolution={resKey}
          filename={filename}
          taskStatus={currentTaskStatus}
          errorMsg={errorMsg}
          index={index}
            />
          );
        })}
      </div>

      <motion.div initial={{ opacity: 0, y: 20 }} animate={{ opacity: 1, y: 0 }} transition={{ delay: 0.3 }} className="bg-dark-card border border-dark-border rounded-xl p-6">
        <h3 className="text-lg font-semibold text-white mb-4">About Your Videos</h3>
        <div className="grid md:grid-cols-2 gap-6">
          <div>
            <h4 className="text-sm font-medium text-gray-400 mb-2">Processing Details</h4>
            <ul className="space-y-2 text-sm text-gray-500">
              <li>• Transcoded using FFmpeg workers</li>
              <li>• Processed via distributed Celery tasks</li>
              <li>• Stored securely</li>
            </ul>
          </div>
          <div>
            <h4 className="text-sm font-medium text-gray-400 mb-2">Available Formats</h4>
            <ul className="space-y-2 text-sm text-gray-500">
              <li>• 360p - Mobile & low bandwidth</li>
              <li>• 720p - Standard HD quality</li>
              <li>• 1080p - Full HD quality</li>
            </ul>
          </div>
        </div>
      </motion.div>
    </div>
  );
}
