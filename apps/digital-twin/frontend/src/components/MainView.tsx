import { useAppStore } from '@/store/appStore';
import { MapContainer } from './map/MapContainer';

export function MainView() {
  const selectedLocation = useAppStore((state) => state.selectedLocation);

  if (!selectedLocation) {
    return (
      <div className="flex h-full items-center justify-center">
        <div className="text-center">
          <h2 className="text-2xl font-semibold text-gray-900 mb-2">
            Welcome to Casper's Digital Twin
          </h2>
          <p className="text-gray-600">
            Select a location from the dropdown above to begin
          </p>
        </div>
      </div>
    );
  }

  return (
    <div className="h-full p-4">
      <div className="grid h-full grid-cols-3 gap-4">
        {/* Map Panel - Left 2/3 */}
        <div className="col-span-2 rounded-lg bg-white shadow overflow-hidden">
          <MapContainer />
        </div>

        {/* Right Column - Kitchen & Metrics */}
        <div className="flex flex-col gap-4">
          {/* Kitchen Pipeline */}
          <div className="flex-1 rounded-lg bg-white p-6 shadow">
            <h3 className="text-lg font-semibold text-gray-900 mb-4">Kitchen Pipeline</h3>
            <div className="flex items-center justify-center h-full text-gray-500">
              Pipeline visualization coming in Phase 2
            </div>
          </div>

          {/* Metrics Dashboard */}
          <div className="flex-1 rounded-lg bg-white p-6 shadow">
            <h3 className="text-lg font-semibold text-gray-900 mb-4">Metrics</h3>
            <div className="flex items-center justify-center h-full text-gray-500">
              Metrics dashboard coming in Phase 2
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}
