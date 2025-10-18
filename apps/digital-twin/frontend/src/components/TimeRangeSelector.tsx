import { ChevronLeft, ChevronRight } from 'lucide-react';
import { useAppStore } from '@/store/appStore';

export function TimeRangeSelector() {
  const timeRange = useAppStore((state) => state.timeRange);
  const setTimeRange = useAppStore((state) => state.setTimeRange);
  const availableLocations = useAppStore((state) => state.availableLocations);
  const selectedLocation = useAppStore((state) => state.selectedLocation);

  const location = availableLocations.find(
    (loc) => loc.location_name === selectedLocation
  );

  if (!timeRange || !location) return null;

  const locationStart = new Date(location.date_range.start);
  const locationEnd = new Date(location.date_range.end);

  const goToPreviousHour = () => {
    const newStart = new Date(timeRange.start.getTime() - 60 * 60 * 1000);
    if (newStart >= locationStart) {
      const newEnd = new Date(timeRange.end.getTime() - 60 * 60 * 1000);
      setTimeRange(newStart, newEnd);
    }
  };

  const goToNextHour = () => {
    const newEnd = new Date(timeRange.end.getTime() + 60 * 60 * 1000);
    if (newEnd <= locationEnd) {
      const newStart = new Date(timeRange.start.getTime() + 60 * 60 * 1000);
      setTimeRange(newStart, newEnd);
    }
  };

  const canGoPrevious = timeRange.start > locationStart;
  const canGoNext = timeRange.end < locationEnd;

  const formatDateTime = (date: Date) => {
    return date.toLocaleString('en-US', {
      month: 'short',
      day: 'numeric',
      hour: 'numeric',
      minute: '2-digit',
      hour12: true,
    });
  };

  const getDurationHours = () => {
    const diffMs = timeRange.end.getTime() - timeRange.start.getTime();
    return Math.round(diffMs / (1000 * 60 * 60));
  };

  return (
    <div className="flex items-center gap-3 bg-white rounded-lg shadow px-4 py-2">
      <button
        onClick={goToPreviousHour}
        disabled={!canGoPrevious}
        className="p-1 rounded hover:bg-gray-100 disabled:opacity-30 disabled:cursor-not-allowed"
        title="Previous hour"
      >
        <ChevronLeft className="w-5 h-5" />
      </button>

      <div className="flex flex-col min-w-[280px]">
        <div className="text-xs text-gray-500 font-medium">Time Range</div>
        <div className="text-sm font-semibold text-gray-900">
          {formatDateTime(timeRange.start)} - {formatDateTime(timeRange.end)}
        </div>
        <div className="text-xs text-gray-500">
          {getDurationHours()} hour{getDurationHours() !== 1 ? 's' : ''}
        </div>
      </div>

      <button
        onClick={goToNextHour}
        disabled={!canGoNext}
        className="p-1 rounded hover:bg-gray-100 disabled:opacity-30 disabled:cursor-not-allowed"
        title="Next hour"
      >
        <ChevronRight className="w-5 h-5" />
      </button>
    </div>
  );
}
