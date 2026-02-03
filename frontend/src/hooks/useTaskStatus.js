import { useQuery } from '@tanstack/react-query';
import { getTaskStatus } from '../services/api';

export function useTaskStatus({ taskId, enabled = true, onSuccess, onError }) {
  return useQuery({
    queryKey: ['taskStatus', taskId],
    queryFn: () => getTaskStatus(taskId),
    enabled: enabled && !!taskId,
    refetchInterval: (data) => {
      // Stop polling if task is complete or failed
      if (data?.state === 'SUCCESS' || data?.state === 'FAILURE') {
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
