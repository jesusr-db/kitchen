import { create } from 'zustand';
import { persist } from 'zustand/middleware';
import type { LocationConfig } from '@/types/location';
import type { PlaybackState, TimeRange, MapViewport } from '@/types/ui';

interface AppState {
  // Location
  selectedLocation: string | null;
  availableLocations: LocationConfig[];
  
  // Timeline
  timeRange: TimeRange | null;
  currentTime: Date | null;
  playbackState: PlaybackState;
  playbackSpeed: number;
  
  // Map
  mapViewport: MapViewport;
  
  // UI
  selectedOrder: string | null;
  
  // Actions
  setLocations: (locations: LocationConfig[]) => void;
  selectLocation: (locationName: string) => void;
  setTimeRange: (start: Date, end: Date) => void;
  setCurrentTime: (time: Date) => void;
  setPlaybackState: (state: PlaybackState) => void;
  setPlaybackSpeed: (speed: number) => void;
  setMapViewport: (viewport: MapViewport) => void;
  selectOrder: (orderId: string | null) => void;
  reset: () => void;
}

const initialState = {
  selectedLocation: null,
  availableLocations: [],
  timeRange: null,
  currentTime: null,
  playbackState: 'stopped' as PlaybackState,
  playbackSpeed: 60,
  mapViewport: {
    center: [0, 0] as [number, number],
    zoom: 12,
  },
  selectedOrder: null,
};

export const useAppStore = create<AppState>()(
  persist(
    (set, get) => ({
      ...initialState,

      setLocations: (locations) => set({ availableLocations: locations }),

      selectLocation: (locationName) => {
        const location = get().availableLocations.find(
          (loc) => loc.location_name === locationName
        );
        
        if (location) {
          const startDate = new Date(location.date_range.start);
          
          // Set time range to first 1 hour by default
          const adjustedEndDate = new Date(startDate.getTime() + 60 * 60 * 1000);
          
          set({
            selectedLocation: locationName,
            mapViewport: {
              center: [location.gk_lon, location.gk_lat],
              zoom: 12,
            },
            timeRange: {
              start: startDate,
              end: adjustedEndDate,
            },
            currentTime: startDate,
            playbackState: 'stopped',
            selectedOrder: null,
          });
        }
      },

      setTimeRange: (start, end) => set({ timeRange: { start, end } }),

      setCurrentTime: (time) => set({ currentTime: time }),

      setPlaybackState: (state) => set({ playbackState: state }),

      setPlaybackSpeed: (speed) => set({ playbackSpeed: speed }),

      setMapViewport: (viewport) => set({ mapViewport: viewport }),

      selectOrder: (orderId) => set({ selectedOrder: orderId }),

      reset: () => set(initialState),
    }),
    {
      name: 'digital-twin-storage',
      partialize: (state) => ({
        selectedLocation: state.selectedLocation,
        playbackSpeed: state.playbackSpeed,
      }),
    }
  )
);
