import { useQuery } from '@tanstack/react-query';
import { getTaskStatus } from '../services/api';
import {useState} from 'react';

export function useTaskStatus({ taskId, enabled = true, onSuccess, onError }) {

  const [pollInterval, setPollInterval] = useState(2000)

  return useQuery({
    queryKey: ['taskStatus', taskId],
    queryFn: () => getTaskStatus(taskId),
    enabled: enabled && !!taskId,
    refetchInterval: (data) => {
      const state = String(data?.state || '').toUpperCase();
      // Stop polling if task is complete or failed
      if (
        state === 'SUCCESS' || 
        state === 'COMPLETED' || 
        state === 'FAILED' || 
        state === 'PARTIAL_SUCCESS') {
        return false;
      }
      const progress = data?.overall_progress || 0;
      if (progress < 10) return 2000;  // Initial: 2s
      if (progress < 50) return 3000;  // Early: 3s  
      if (progress < 90) return 5000;  // Mid: 5s
      return 2500; // Poll every 2.5 seconds
    },
    retry: 3,
    retryDelay: (attemptIndex) => Math.min(1000 * 2 ** attemptIndex, 30000),
    onSuccess,
    onError,
  });
}
