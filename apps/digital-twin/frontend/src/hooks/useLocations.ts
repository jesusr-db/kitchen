import { useQuery } from '@tanstack/react-query';
import { api } from '@/services/api';

export function useLocations() {
  return useQuery({
    queryKey: ['locations'],
    queryFn: api.fetchLocations,
    staleTime: 1000 * 60 * 15, // 15 minutes
    retry: 3,
  });
}
