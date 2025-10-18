import { useState, useRef, useEffect } from 'react';
import { Calendar, Clock } from 'lucide-react';
import { DayPicker } from 'react-day-picker';
import { format, setHours, setMinutes, startOfDay, differenceInHours } from 'date-fns';
import { useAppStore } from '@/store/appStore';
import 'react-day-picker/dist/style.css';

export function CustomTimeRangeSelector() {
  const timeRange = useAppStore((state) => state.timeRange);
  const setTimeRange = useAppStore((state) => state.setTimeRange);
  const availableLocations = useAppStore((state) => state.availableLocations);
  const selectedLocation = useAppStore((state) => state.selectedLocation);

  const [isOpen, setIsOpen] = useState(false);
  const [startDate, setStartDate] = useState<Date | undefined>(undefined);
  const [endDate, setEndDate] = useState<Date | undefined>(undefined);
  const [startHour, setStartHour] = useState(0);
  const [endHour, setEndHour] = useState(1);
  const dropdownRef = useRef<HTMLDivElement>(null);

  const location = availableLocations.find(
    (loc) => loc.location_name === selectedLocation
  );

  useEffect(() => {
    if (timeRange) {
      setStartDate(timeRange.start);
      setEndDate(timeRange.end);
      setStartHour(timeRange.start.getHours());
      setEndHour(timeRange.end.getHours());
    }
  }, [timeRange]);

  useEffect(() => {
    function handleClickOutside(event: MouseEvent) {
      if (dropdownRef.current && !dropdownRef.current.contains(event.target as Node)) {
        setIsOpen(false);
      }
    }

    if (isOpen) {
      document.addEventListener('mousedown', handleClickOutside);
    }

    return () => {
      document.removeEventListener('mousedown', handleClickOutside);
    };
  }, [isOpen]);

  if (!timeRange || !location) return null;

  const locationStart = new Date(location.date_range.start);
  const locationEnd = new Date(location.date_range.end);

  const hours = Array.from({ length: 24 }, (_, i) => i);

  const handleApply = () => {
    if (!startDate || !endDate) return;

    const newStart = setMinutes(setHours(startOfDay(startDate), startHour), 0);
    const newEnd = setMinutes(setHours(startOfDay(endDate), endHour), 0);

    if (newStart >= locationStart && newEnd <= locationEnd && newStart < newEnd) {
      setTimeRange(newStart, newEnd);
      setIsOpen(false);
    }
  };

  const formatTimeRange = () => {
    const sameDay = format(timeRange.start, 'MMM d') === format(timeRange.end, 'MMM d');
    if (sameDay) {
      return `${format(timeRange.start, 'MMM d, h:mm a')} - ${format(timeRange.end, 'h:mm a')}`;
    }
    return `${format(timeRange.start, 'MMM d, h:mm a')} - ${format(timeRange.end, 'MMM d, h:mm a')}`;
  };

  const getDurationHours = () => {
    return differenceInHours(timeRange.end, timeRange.start);
  };

  return (
    <div className="relative" ref={dropdownRef}>
      <button
        onClick={() => setIsOpen(!isOpen)}
        className="flex items-center gap-3 bg-white rounded-lg shadow px-4 py-2 hover:bg-gray-50"
      >
        <Calendar className="w-5 h-5 text-gray-600" />
        <div className="flex flex-col text-left min-w-[260px]">
          <div className="text-xs text-gray-500 font-medium">Time Range</div>
          <div className="text-sm font-semibold text-gray-900">
            {formatTimeRange()}
          </div>
          <div className="text-xs text-gray-500">
            {getDurationHours()} hour{getDurationHours() !== 1 ? 's' : ''}
          </div>
        </div>
      </button>

      {isOpen && (
        <div className="absolute right-0 mt-2 bg-white rounded-lg shadow-lg border border-gray-200 p-4 z-[1000] min-w-[700px]">
          <div className="space-y-4">
            <div className="grid grid-cols-2 gap-4">
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-2">
                  Start Date
                </label>
                <DayPicker
                  mode="single"
                  selected={startDate}
                  onSelect={setStartDate}
                  fromDate={locationStart}
                  toDate={endDate || locationEnd}
                  disabled={{ before: locationStart, after: endDate || locationEnd }}
                  className="border rounded-lg p-2"
                />
              </div>

              <div>
                <label className="block text-sm font-medium text-gray-700 mb-2">
                  End Date
                </label>
                <DayPicker
                  mode="single"
                  selected={endDate}
                  onSelect={setEndDate}
                  fromDate={startDate || locationStart}
                  toDate={locationEnd}
                  disabled={{ before: startDate || locationStart, after: locationEnd }}
                  className="border rounded-lg p-2"
                />
              </div>
            </div>

            <div className="grid grid-cols-2 gap-4">
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-2">
                  <Clock className="w-4 h-4 inline mr-1" />
                  Start Hour
                </label>
                <select
                  value={startHour}
                  onChange={(e) => setStartHour(Number(e.target.value))}
                  className="w-full border border-gray-300 rounded-lg px-3 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-blue-500"
                >
                  {hours.map((hour) => (
                    <option key={hour} value={hour}>
                      {format(setHours(new Date(), hour), 'h:mm a')}
                    </option>
                  ))}
                </select>
              </div>

              <div>
                <label className="block text-sm font-medium text-gray-700 mb-2">
                  <Clock className="w-4 h-4 inline mr-1" />
                  End Hour
                </label>
                <select
                  value={endHour}
                  onChange={(e) => setEndHour(Number(e.target.value))}
                  className="w-full border border-gray-300 rounded-lg px-3 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-blue-500"
                >
                  {hours.map((hour) => (
                    <option key={hour} value={hour}>
                      {format(setHours(new Date(), hour), 'h:mm a')}
                    </option>
                  ))}
                </select>
              </div>
            </div>

            <div className="flex justify-end gap-2 pt-2 border-t">
              <button
                onClick={() => setIsOpen(false)}
                className="px-4 py-2 text-sm text-gray-700 hover:bg-gray-100 rounded-lg"
              >
                Cancel
              </button>
              <button
                onClick={handleApply}
                disabled={!startDate || !endDate}
                className="px-4 py-2 text-sm bg-blue-600 text-white rounded-lg hover:bg-blue-700 disabled:opacity-50 disabled:cursor-not-allowed"
              >
                Apply
              </button>
            </div>
          </div>
        </div>
      )}
    </div>
  );
}
