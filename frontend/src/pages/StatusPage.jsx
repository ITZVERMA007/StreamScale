import { useParams, useNavigate } from 'react-router-dom';
import { motion, AnimatePresence } from 'framer-motion';
import { 
  Clock, 
  CheckCircle, 
  XCircle, 
  RefreshCw, 
  ArrowRight,
  Activity,
  AlertCircle
} from 'lucide-react';
import { useTaskStatus } from '../hooks/useTaskStatus';
import ProgressBar from '../components/ProgressBar';
import LoadingSpinner from '../components/LoadingSpinner';
import toast from 'react-hot-toast';

export default function StatusPage() {
  const { taskId } = useParams();
  const navigate = useNavigate();

  const { data: status, isLoading, isError, refetch } = useTaskStatus({
    taskId: taskId || null,
    onSuccess: (data) => {
      if (data.state === 'SUCCESS') {
        toast.success('Transcoding completed!');
      } else if (data.state === 'FAILURE') {
        toast.error('Transcoding failed');
      }
    },
    onError: () => {
      toast.error('Failed to fetch status');
    },
  });

  const handleViewResults = () => {
    navigate(`/results/${taskId}`);
  };

  const handleRetry = () => {
    refetch();
  };

  if (!taskId) {
    return (
      <div className="max-w-2xl mx-auto text-center">
        <div className="bg-dark-card border border-dark-border rounded-2xl p-12">
          <AlertCircle className="w-16 h-16 text-accent-warning mx-auto mb-4" />
          <h2 className="text-2xl font-bold text-white mb-2">No Task ID</h2>
          <p className="text-gray-400 mb-6">
            Please provide a valid task ID to check the status.
          </p>
          <button
            onClick={() => {
              sessionStorage.removeItem('streamscale_active_task'); 
              navigate('/');
            }}
            className="px-6 py-3 bg-accent-primary hover:bg-accent-primary/90 text-white rounded-lg font-medium transition-colors"
          >
            Upload New Video
          </button>
        </div>
      </div>
    );
  }

  if (isLoading) {
    return (
      <div className="max-w-2xl mx-auto">
        <div className="bg-dark-card border border-dark-border rounded-2xl p-12 text-center">
          <LoadingSpinner size="lg" className="text-accent-primary mx-auto mb-4" />
          <h3 className="text-xl font-semibold text-white mb-2">Loading Status...</h3>
          <p className="text-gray-400">Fetching transcoding information</p>
        </div>
      </div>
    );
  }

  if (isError) {
    return (
      <div className="max-w-2xl mx-auto">
        <div className="bg-dark-card border border-dark-border rounded-2xl p-12 text-center">
          <XCircle className="w-16 h-16 text-accent-error mx-auto mb-4" />
          <h2 className="text-2xl font-bold text-white mb-2">Error Loading Status</h2>
          <p className="text-gray-400 mb-6">
            Could not fetch status for this task. Please check the task ID and try again.
          </p>
          <button
            onClick={handleRetry}
            className="inline-flex items-center gap-2 px-6 py-3 bg-accent-primary hover:bg-accent-primary/90 text-white rounded-lg font-medium transition-colors"
          >
            <RefreshCw className="w-4 h-4" />
            Retry
          </button>
        </div>
      </div>
    );
  }

  const stateConfig = {
    PENDING: { 
      icon: Clock, 
      color: 'text-accent-warning', 
      bg: 'bg-accent-warning/10',
      label: 'Pending',
      description: 'Task is queued and waiting to be processed'
    },
    STARTED: { 
      icon: Activity, 
      color: 'text-blue-400', 
      bg: 'bg-blue-500/10',
      label: 'Started',
      description: 'Processing has begun'
    },
    PROGRESS: { 
      icon: Activity, 
      color: 'text-accent-primary', 
      bg: 'bg-accent-primary/10',
      label: 'In Progress',
      description: 'Actively transcoding your video'
    },
    SUCCESS: { 
      icon: CheckCircle, 
      color: 'text-accent-success', 
      bg: 'bg-accent-success/10',
      label: 'Success',
      description: 'Transcoding completed successfully'
    },
    COMPLETED: { 
      icon: CheckCircle, 
      color: 'text-accent-success',
      bg: 'bg-accent-success/10', 
      label: 'Success', 
      description: 'Transcoding completed successfully' 
    },
    PARTIAL_SUCCESS: { 
      icon: AlertCircle,
      color: 'text-accent-warning', 
      bg: 'bg-accent-warning/10', 
      label: 'Partial Success', 
      description: 'Some resolutions failed, but others are ready' 
    },
    FAILURE: { 
      icon: XCircle, 
      color: 'text-accent-error', 
      bg: 'bg-accent-error/10',
      label: 'Failed',
      description: 'Transcoding encountered an error'
    },
  };

  const currentState = status?.state?.toUpperCase() || "PENDING";
  const config = stateConfig[currentState] || stateConfig.PENDING;
  const Icon = config.icon;

  const hasCompletedTasks = status?.details && Object.values(status.details).some(t => t.status === "COMPLETED");
  const isFinished = currentState === "SUCCESS" || currentState === 'COMPLETED'|| currentState === "PARTIAL_SUCCESS";
  return (
    <div className="max-w-3xl mx-auto">
      
      <motion.div initial={{ opacity: 0, y: 20 }} animate={{ opacity: 1, y: 0 }} className="text-center mb-12">
        <h1 className="text-4xl font-bold text-white mb-4 font-display">Processing Status</h1>
        <p className="text-gray-400">Track your video transcoding progress in real-time</p>
      </motion.div>

      <motion.div initial={{ opacity: 0, y: 20 }} animate={{ opacity: 1, y: 0 }} transition={{ delay: 0.1 }} className="bg-dark-card border border-dark-border rounded-2xl overflow-hidden">
        
        <div className="border-b border-dark-border p-6 bg-dark-bg/50 flex justify-between">
          <div>
            <p className="text-sm text-gray-500 mb-1">Task ID</p>
            <code className="text-sm font-mono text-accent-primary">{taskId}</code>
          </div>
        </div>

        <div className="p-8">
          <AnimatePresence mode="wait">
            <motion.div key={status?.state} initial={{ opacity: 0, scale: 0.95 }} animate={{ opacity: 1, scale: 1 }} exit={{ opacity: 0, scale: 0.95 }} className="text-center mb-8">
              <div className={`w-20 h-20 ${config.bg} rounded-2xl flex items-center justify-center mx-auto mb-4`}>
                <Icon className={`w-10 h-10 ${config.color}`} />
              </div>
              <h2 className="text-2xl font-bold text-white mb-2">{config.label}</h2>
              <p className="text-gray-400">{status?.error || config.description}</p>
            </motion.div>
          </AnimatePresence>

          {status && (status.state === 'PROCESSING' || status.state === 'STARTED') && (
            <motion.div initial={{ opacity: 0, y: 10 }} animate={{ opacity: 1, y: 0 }} className="mb-8">
              <ProgressBar progress={status.overall_progress || 0} label="Overall Progress" />
            </motion.div>
          )}

          {status?.details && (
            <div className="mb-8 grid gap-4">
              {Object.entries(status.details).map(([res, info]) => (
                <div key={res} className="p-4 bg-dark-bg/50 rounded-lg border border-dark-border">
                  <div className="flex justify-between items-center mb-2">
                    <span className="font-mono text-sm text-white">{res}p</span>
                    <span className={`text-xs font-semibold px-2 py-1 rounded-full ${
                      info.status === 'COMPLETED' ? 'bg-green-500/10 text-green-400' :
                      info.status === 'FAILED' ? 'bg-red-500/10 text-red-400' :
                      info.status === 'RUNNING' ? 'bg-blue-500/10 text-blue-400' :
                      'bg-gray-500/10 text-gray-400'
                    }`}>
                      {info.status}
                    </span>
                  </div>
                  {(info.status === 'RUNNING' || info.status === 'QUEUED') && (
                    <ProgressBar progress={info.progress} showPercentage={true} />
                  )}
                  {info.error && <p className="text-xs text-red-400 mt-2 line-clamp-1">{info.error}</p>}
                </div>
              ))}
            </div>
          )}

          <div className="flex gap-3 mt-8">
            {(isFinished || hasCompletedTasks) && (
              <button onClick={handleViewResults} className="flex-1 group inline-flex items-center justify-center gap-2 px-6 py-4 bg-gradient-to-r from-accent-primary to-accent-secondary hover:shadow-lg text-white rounded-xl font-semibold transition-all">
                View Results <ArrowRight className="w-5 h-5 group-hover:translate-x-1 transition-transform" />
              </button>
            )}

            {(status?.state === 'FAILED' || isFinished) && (
              <button 
                onClick={() => {
                  sessionStorage.removeItem('streamscale_active_task');
                  navigate('/');
                }} 
                className="flex-1 px-6 py-4 bg-dark-hover hover:bg-dark-border text-white rounded-xl font-semibold transition-colors"
              >
                Upload New Video
              </button>
            )}
          </div>
        </div>
      </motion.div>
    </div>
  );
}
