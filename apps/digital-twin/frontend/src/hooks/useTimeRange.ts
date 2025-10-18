import { useQuery } from '@tanstack/react-query';
import { api } from '@/services/api';
import { useAppStore } from '@/store/appStore';

export function useTimeRange(limit: number = 100) {
  const selectedLocation = useAppStore((state) => state.selectedLocation);
  const timeRange = useAppStore((state) => state.timeRange);

  return useQuery({
    queryKey: ['timeRange', selectedLocation, timeRange?.start, timeRange?.end, limit],
    queryFn: () => {
      if (!selectedLocation || !timeRange) {
        throw new Error('Location and time range required');
      }
      return api.fetchTimeRange(selectedLocation, timeRange.start, timeRange.end, limit);
    },
    enabled: !!selectedLocation && !!timeRange,
    staleTime: 5 * 60 * 1000, // 5 minutes
  });
}
