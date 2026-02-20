import { useQuery } from '@tanstack/react-query';
import { getTaskStatus } from '../services/api';

export function useTaskStatus({ taskId, enabled = true, onSuccess, onError }) {
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
      return 2500; // Poll every 2.5 seconds
    },
    retry: 3,
    retryDelay: (attemptIndex) => Math.min(1000 * 2 ** attemptIndex, 30000),
    onSuccess,
    onError,
  });
}
