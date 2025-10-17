import { Fragment } from 'react';
import { Listbox, Transition } from '@headlessui/react';
import { Check, ChevronsUpDown, MapPin } from 'lucide-react';
import { useAppStore } from '@/store/appStore';
import { useLocations } from '@/hooks/useLocations';
import { LoadingSpinner } from './LoadingSpinner';

export function LocationSelector() {
  const { data, isLoading, error } = useLocations();
  const { selectedLocation, availableLocations, setLocations, selectLocation } = useAppStore();

  // Update store with fetched locations
  if (data && data.locations.length > 0 && availableLocations.length === 0) {
    setLocations(data.locations);
  }

  if (isLoading) {
    return (
      <div className="flex items-center gap-2 text-gray-600">
        <LoadingSpinner size="sm" />
        <span className="text-sm">Loading locations...</span>
      </div>
    );
  }

  if (error) {
    return (
      <div className="text-sm text-red-600">
        Failed to load locations
      </div>
    );
  }

  if (!data || data.locations.length === 0) {
    return (
      <div className="text-sm text-gray-600">
        No locations available
      </div>
    );
  }

  const selectedLocationData = data.locations.find(
    (loc) => loc.location_name === selectedLocation
  );

  return (
    <Listbox value={selectedLocation} onChange={selectLocation}>
      <div className="relative w-64">
        <Listbox.Button className="relative w-full cursor-pointer rounded-lg bg-white py-2 pl-3 pr-10 text-left shadow-md focus:outline-none focus:ring-2 focus:ring-blue-500 focus:ring-offset-2">
          <span className="flex items-center gap-2">
            <MapPin className="h-4 w-4 text-gray-500" />
            <span className="block truncate">
              {selectedLocationData?.display_name || 'Select a location'}
            </span>
          </span>
          <span className="pointer-events-none absolute inset-y-0 right-0 flex items-center pr-2">
            <ChevronsUpDown className="h-5 w-5 text-gray-400" />
          </span>
        </Listbox.Button>
        
        <Transition
          as={Fragment}
          leave="transition ease-in duration-100"
          leaveFrom="opacity-100"
          leaveTo="opacity-0"
        >
          <Listbox.Options className="absolute z-10 mt-1 max-h-60 w-full overflow-auto rounded-md bg-white py-1 shadow-lg ring-1 ring-black ring-opacity-5 focus:outline-none">
            {data.locations.map((location) => (
              <Listbox.Option
                key={location.location_name}
                value={location.location_name}
                className={({ active }) =>
                  `relative cursor-pointer select-none py-2 pl-10 pr-4 ${
                    active ? 'bg-blue-100 text-blue-900' : 'text-gray-900'
                  }`
                }
              >
                {({ selected }) => (
                  <>
                    <span className={`block truncate ${selected ? 'font-medium' : 'font-normal'}`}>
                      {location.display_name}
                    </span>
                    <span className="block text-xs text-gray-500">
                      {location.total_orders.toLocaleString()} orders
                    </span>
                    {selected && (
                      <span className="absolute inset-y-0 left-0 flex items-center pl-3 text-blue-600">
                        <Check className="h-5 w-5" />
                      </span>
                    )}
                  </>
                )}
              </Listbox.Option>
            ))}
          </Listbox.Options>
        </Transition>
      </div>
    </Listbox>
  );
}
