import { useState, useRef } from 'react';
import { Upload, File, X, AlertCircle } from 'lucide-react';
import { motion, AnimatePresence } from 'framer-motion';
import { cn, formatFileSize, validateVideoFile } from '../utils/helpers';
import { ALLOWED_FILE_TYPES, ALLOWED_EXTENSIONS, MAX_FILE_SIZE } from '../types';

export default function VideoDropzone({ onFileSelect, disabled = false }) {
  const [isDragging, setIsDragging] = useState(false);
  const [selectedFile, setSelectedFile] = useState(null);
  const [error, setError] = useState(null);
  const fileInputRef = useRef(null);

  const handleDragOver = (e) => {
    e.preventDefault();
    if (!disabled) setIsDragging(true);
  };

  const handleDragLeave = (e) => {
    e.preventDefault();
    setIsDragging(false);
  };

  const handleDrop = (e) => {
    e.preventDefault();
    setIsDragging(false);

    if (disabled) return;

    const files = Array.from(e.dataTransfer.files);
    if (files.length > 0) {
      handleFileValidation(files[0]);
    }
  };

  const handleFileInput = (e) => {
    const files = e.target.files;
    if (files && files.length > 0) {
      handleFileValidation(files[0]);
    }
  };

  const handleFileValidation = (file) => {
    setError(null);
    const validation = validateVideoFile(file, ALLOWED_FILE_TYPES, MAX_FILE_SIZE);

    if (!validation.valid) {
      setError(validation.error);
      return;
    }

    setSelectedFile(file);
    onFileSelect(file);
  };

  const handleRemoveFile = () => {
    setSelectedFile(null);
    setError(null);
    if (fileInputRef.current) {
      fileInputRef.current.value = '';
    }
  };

  const handleBrowse = () => {
    fileInputRef.current?.click();
  };

  return (
    <div className="w-full">
      <input
        ref={fileInputRef}
        type="file"
        accept={ALLOWED_EXTENSIONS.join(',')}
        onChange={handleFileInput}
        className="hidden"
        disabled={disabled}
      />

      <AnimatePresence mode="wait">
        {!selectedFile ? (
          <motion.div
            key="dropzone"
            initial={{ opacity: 0, scale: 0.95 }}
            animate={{ opacity: 1, scale: 1 }}
            exit={{ opacity: 0, scale: 0.95 }}
            className={cn(
              'relative border-2 border-dashed rounded-2xl transition-all',
              isDragging
                ? 'border-accent-primary bg-accent-primary/5 scale-[1.02]'
                : 'border-dark-border bg-dark-card hover:border-dark-border/50',
              disabled && 'opacity-50 cursor-not-allowed'
            )}
            onDragOver={handleDragOver}
            onDragLeave={handleDragLeave}
            onDrop={handleDrop}
          >
            <div className="p-12 text-center">
              <motion.div
                className="w-20 h-20 mx-auto mb-6 bg-gradient-to-br from-accent-primary/20 to-accent-secondary/20 rounded-2xl flex items-center justify-center"
                animate={{ y: isDragging ? -10 : 0 }}
                transition={{ type: 'spring', stiffness: 300 }}
              >
                <Upload className="w-10 h-10 text-accent-primary" />
              </motion.div>

              <h3 className="text-xl font-semibold text-white mb-2">
                Drop your video here
              </h3>
              <p className="text-gray-400 mb-6">
                or click to browse from your device
              </p>

              <button
                onClick={handleBrowse}
                disabled={disabled}
                className="px-6 py-3 bg-accent-primary hover:bg-accent-primary/90 text-white rounded-lg font-medium transition-all disabled:opacity-50 disabled:cursor-not-allowed"
              >
                Browse Files
              </button>

              <div className="mt-8 pt-8 border-t border-dark-border">
                <p className="text-sm text-gray-500 mb-2">
                  Supported formats: <span className="text-gray-400 font-mono">MP4, MKV, MOV, WEBM</span>
                </p>
                <p className="text-sm text-gray-500">
                  Maximum file size: <span className="text-gray-400 font-mono">{formatFileSize(MAX_FILE_SIZE)}</span>
                </p>
              </div>
            </div>
          </motion.div>
        ) : (
          <motion.div
            key="selected"
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            exit={{ opacity: 0, y: -20 }}
            className="bg-dark-card border border-dark-border rounded-2xl p-6"
          >
            <div className="flex items-start gap-4">
              <div className="w-12 h-12 bg-accent-primary/10 rounded-lg flex items-center justify-center flex-shrink-0">
                <File className="w-6 h-6 text-accent-primary" />
              </div>

              <div className="flex-1 min-w-0">
                <h4 className="text-white font-medium truncate mb-1">
                  {selectedFile.name}
                </h4>
                <p className="text-sm text-gray-400">
                  {formatFileSize(selectedFile.size)}
                </p>
              </div>

              {!disabled && (
                <button
                  onClick={handleRemoveFile}
                  className="w-8 h-8 flex items-center justify-center rounded-lg hover:bg-dark-hover text-gray-400 hover:text-white transition-colors flex-shrink-0"
                >
                  <X className="w-5 h-5" />
                </button>
              )}
            </div>
          </motion.div>
        )}
      </AnimatePresence>

      <AnimatePresence>
        {error && (
          <motion.div
            initial={{ opacity: 0, y: -10 }}
            animate={{ opacity: 1, y: 0 }}
            exit={{ opacity: 0, y: -10 }}
            className="mt-4 p-4 bg-accent-error/10 border border-accent-error/20 rounded-lg flex items-start gap-3"
          >
            <AlertCircle className="w-5 h-5 text-accent-error flex-shrink-0 mt-0.5" />
            <p className="text-sm text-accent-error">{error}</p>
          </motion.div>
        )}
      </AnimatePresence>
    </div>
  );
}
