import { motion } from 'framer-motion';
import { cn } from '../utils/helpers';

export default function ProgressBar({ 
  progress, 
  className = '', 
  label,
  showPercentage = true 
}) {
  const clampedProgress = Math.min(Math.max(progress, 0), 100);

  return (
    <div className={cn('w-full', className)}>
      {(label || showPercentage) && (
        <div className="flex justify-between items-center mb-2">
          {label && <span className="text-sm text-gray-400">{label}</span>}
          {showPercentage && (
            <span className="text-sm font-mono text-accent-primary">
              {clampedProgress.toFixed(0)}%
            </span>
          )}
        </div>
      )}
      <div className="h-2 bg-dark-border rounded-full overflow-hidden">
        <motion.div
          className="h-full bg-gradient-to-r from-accent-primary to-accent-secondary rounded-full"
          initial={{ width: 0 }}
          animate={{ width: `${clampedProgress}%` }}
          transition={{ duration: 0.3, ease: 'easeOut' }}
        />
      </div>
    </div>
  );
}
