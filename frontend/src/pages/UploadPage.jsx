import { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { motion } from 'framer-motion';
import { Rocket, ArrowRight } from 'lucide-react';
import toast from 'react-hot-toast';
import VideoDropzone from '../components/VideoDropzone';
import ProgressBar from '../components/ProgressBar';
import LoadingSpinner from '../components/LoadingSpinner';
import { uploadVideo } from '../services/api';

export default function UploadPage() {
  const [selectedFile, setSelectedFile] = useState(null);
  const [uploadProgress, setUploadProgress] = useState(0);
  const [isUploading, setIsUploading] = useState(false);
  const [taskId, setTaskId] = useState(null);
  const navigate = useNavigate();

  const handleFileSelect = (file) => {
    setSelectedFile(file);
    setTaskId(null);
    setUploadProgress(0);
  };

  const handleUpload = async () => {
    console.log("DATA TYPE CHECK:", selectedFile); 
    console.log("Is it an array?", Array.isArray(selectedFile));
    if (!selectedFile) return;
    

    setIsUploading(true);
    setUploadProgress(0);

    try {
      const response = await uploadVideo(selectedFile, (progress) => {
        setUploadProgress(progress);
      });

      setTaskId(response.task_id);
      localStorage.setItem('streamscale_active_task',response.task_id);
      toast.success('Video uploaded successfully!');
      
      // Auto-navigate after a brief delay
      setTimeout(() => {
        navigate(`/status/${response.task_id}`);
      }, 1500);
    } catch (error) {
      console.error('Upload failed:', error);
      toast.error(error.response?.data?.message || 'Upload failed. Please try again.');
      setIsUploading(false);
    }
  };

  return (
    <div className="max-w-4xl mx-auto">
      {/* Header Section */}
      <motion.div
        initial={{ opacity: 0, y: 20 }}
        animate={{ opacity: 1, y: 0 }}
        className="text-center mb-12"
      >
        <div className="inline-flex items-center gap-2 px-4 py-2 bg-accent-primary/10 border border-accent-primary/20 rounded-full text-accent-primary text-sm font-medium mb-6">
          <Rocket className="w-4 h-4" />
          Distributed Video Transcoding
        </div>
        
        <h1 className="text-5xl font-bold text-white mb-4 font-display">
          Upload Your Video
        </h1>
        <p className="text-xl text-gray-400 max-w-2xl mx-auto">
          Upload your video file and we'll transcode it to multiple resolutions using our distributed processing system.
        </p>
      </motion.div>

      {/* Upload Section */}
      <motion.div
        initial={{ opacity: 0, y: 20 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ delay: 0.1 }}
      >
        <VideoDropzone 
          onFileSelect={handleFileSelect}
          disabled={isUploading}
        />
      </motion.div>

      {/* Upload Progress */}
      {isUploading && (
        <motion.div
          initial={{ opacity: 0, height: 0 }}
          animate={{ opacity: 1, height: 'auto' }}
          className="mt-8"
        >
          <div className="bg-dark-card border border-dark-border rounded-2xl p-6">
            <div className="flex items-center gap-3 mb-4">
              <LoadingSpinner size="sm" className="text-accent-primary" />
              <h3 className="text-lg font-semibold text-white">
                {uploadProgress < 100 ? 'Uploading...' : 'Processing...'}
              </h3>
            </div>
            
            <ProgressBar 
              progress={uploadProgress} 
              label="Upload Progress"
              className="mb-4"
            />

            {taskId && (
              <div className="mt-4 p-4 bg-accent-primary/5 border border-accent-primary/20 rounded-lg">
                <p className="text-sm text-gray-400 mb-1">Task ID</p>
                <code className="text-sm font-mono text-accent-primary break-all">
                  {taskId}
                </code>
              </div>
            )}
          </div>
        </motion.div>
      )}

      {/* Upload Button */}
      {selectedFile && !isUploading && !taskId && (
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          className="mt-8 flex justify-center"
        >
          <button
            onClick={handleUpload}
            className="group inline-flex items-center gap-3 px-8 py-4 bg-gradient-to-r from-accent-primary to-accent-secondary hover:shadow-lg hover:shadow-accent-primary/25 text-white rounded-xl font-semibold text-lg transition-all"
          >
            Start Transcoding
            <ArrowRight className="w-5 h-5 group-hover:translate-x-1 transition-transform" />
          </button>
        </motion.div>
      )}

      {/* Info Cards */}
      <motion.div
        initial={{ opacity: 0, y: 20 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ delay: 0.2 }}
        className="mt-16 grid md:grid-cols-3 gap-6"
      >
        <InfoCard
          title="Fast Processing"
          description="Distributed workers process your video in parallel for maximum speed"
          icon="⚡"
        />
        <InfoCard
          title="Multiple Resolutions"
          description="Get 360p, 720p, and 1080p versions automatically"
          icon="📹"
        />
        <InfoCard
          title="Real-time Status"
          description="Track your transcoding progress in real-time"
          icon="📊"
        />
      </motion.div>
    </div>
  );
}

function InfoCard({ title, description, icon }) {
  return (
    <div className="bg-dark-card border border-dark-border rounded-xl p-6 hover:border-dark-border/50 transition-colors">
      <div className="text-3xl mb-3">{icon}</div>
      <h3 className="text-lg font-semibold text-white mb-2">{title}</h3>
      <p className="text-sm text-gray-400">{description}</p>
    </div>
  );
}
