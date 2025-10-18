import { Marker, Popup } from 'react-leaflet';
import { Icon } from 'leaflet';
import type { LocationConfig } from '@/types/location';

interface KitchenMarkerProps {
  location: LocationConfig;
}

const kitchenIcon = new Icon({
  iconUrl: 'data:image/svg+xml;base64,' + btoa(`
    <svg xmlns="http://www.w3.org/2000/svg" width="32" height="32" viewBox="0 0 24 24" fill="none" stroke="#dc2626" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
      <path d="M3 2v7c0 1.1.9 2 2 2h4a2 2 0 0 0 2-2V2"/>
      <path d="M7 2v20"/>
      <path d="M21 15V2v0a5 5 0 0 0-5 5v6c0 1.1.9 2 2 2h3Zm0 0v7"/>
    </svg>
  `),
  iconSize: [32, 32],
  iconAnchor: [16, 16],
  popupAnchor: [0, -16],
});

export function KitchenMarker({ location }: KitchenMarkerProps) {
  return (
    <Marker
      position={[location.gk_lat, location.gk_lon]}
      icon={kitchenIcon}
    >
      <Popup>
        <div className="text-sm">
          <h3 className="font-semibold text-gray-900 mb-1">
            {location.display_name} Kitchen
          </h3>
          <p className="text-gray-600">
            Total Orders: {location.total_orders.toLocaleString()}
          </p>
          <p className="text-gray-600">
            Delivery Radius: {location.radius_mi} miles
          </p>
        </div>
      </Popup>
    </Marker>
  );
}
