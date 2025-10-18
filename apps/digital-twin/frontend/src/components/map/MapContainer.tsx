import { MapContainer as LeafletMap, TileLayer } from 'react-leaflet';
import { useAppStore } from '@/store/appStore';
import { useTimeRange } from '@/hooks/useTimeRange';
import { KitchenMarker } from './KitchenMarker';
import { DeliveryRadius } from './DeliveryRadius';
import { CustomerMarkers } from './CustomerMarkers';
import { RouteLines } from './RouteLines';

export function MapContainer() {
  const mapViewport = useAppStore((state) => state.mapViewport);
  const selectedLocation = useAppStore((state) => state.selectedLocation);
  const availableLocations = useAppStore((state) => state.availableLocations);

  const location = availableLocations.find(
    (loc) => loc.location_name === selectedLocation
  );

  const { data: timeRangeData } = useTimeRange(50);

  if (!location) {
    return (
      <div className="h-full flex items-center justify-center bg-gray-100">
        <p className="text-gray-500">No location selected</p>
      </div>
    );
  }

  return (
    <LeafletMap
      center={[location.gk_lat, location.gk_lon]}
      zoom={mapViewport.zoom}
      className="h-full w-full"
      zoomControl={true}
    >
      <TileLayer
        attribution='&copy; <a href="https://www.openstreetmap.org/copyright">OpenStreetMap</a> contributors'
        url="https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png"
      />
      
      <KitchenMarker location={location} />
      <DeliveryRadius location={location} />
      
      {timeRangeData?.orders && (
        <>
          <RouteLines orders={timeRangeData.orders} kitchen={location} />
          <CustomerMarkers orders={timeRangeData.orders} />
        </>
      )}
    </LeafletMap>
  );
}
