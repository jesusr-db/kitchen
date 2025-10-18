import { Circle } from 'react-leaflet';
import type { LocationConfig } from '@/types/location';

interface DeliveryRadiusProps {
  location: LocationConfig;
}

const MILES_TO_METERS = 1609.34;

export function DeliveryRadius({ location }: DeliveryRadiusProps) {
  const radiusInMeters = location.radius_mi * MILES_TO_METERS;

  return (
    <Circle
      center={[location.gk_lat, location.gk_lon]}
      radius={radiusInMeters}
      pathOptions={{
        color: '#3b82f6',
        fillColor: '#3b82f6',
        fillOpacity: 0.1,
        weight: 2,
        dashArray: '10, 10',
      }}
    />
  );
}
