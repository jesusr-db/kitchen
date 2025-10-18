import { Marker, Tooltip } from 'react-leaflet';
import { Icon } from 'leaflet';
import type { OrderLifecycle } from '@/types/order';

interface CustomerMarkersProps {
  orders: OrderLifecycle[];
}

const completedIcon = new Icon({
  iconUrl: 'data:image/svg+xml;base64,' + btoa(`
    <svg xmlns="http://www.w3.org/2000/svg" width="24" height="24" viewBox="0 0 24 24" fill="#10b981" stroke="white" stroke-width="2">
      <circle cx="12" cy="12" r="10"/>
      <path d="M9 12l2 2 4-4" stroke="white" stroke-width="2" fill="none"/>
    </svg>
  `),
  iconSize: [24, 24],
  iconAnchor: [12, 12],
  tooltipAnchor: [0, -12],
});

const inProgressIcon = new Icon({
  iconUrl: 'data:image/svg+xml;base64,' + btoa(`
    <svg xmlns="http://www.w3.org/2000/svg" width="24" height="24" viewBox="0 0 24 24" fill="#f59e0b" stroke="white" stroke-width="2">
      <circle cx="12" cy="12" r="10"/>
      <circle cx="12" cy="12" r="3" fill="white"/>
    </svg>
  `),
  iconSize: [24, 24],
  iconAnchor: [12, 12],
  tooltipAnchor: [0, -12],
});

function getIcon(status: string): Icon {
  return status === 'completed' ? completedIcon : inProgressIcon;
}

export function CustomerMarkers({ orders }: CustomerMarkersProps) {
  return (
    <>
      {orders.map((order) => {
        if (!order.customer_lat || !order.customer_lon) return null;

        return (
          <Marker
            key={order.order_id}
            position={[order.customer_lat, order.customer_lon]}
            icon={getIcon(order.status)}
          >
            <Tooltip>
              <div className="text-xs">
                <div className="font-semibold">{order.brand}</div>
                <div className="text-gray-600">Order: {order.order_id.slice(0, 8)}</div>
                <div className="text-gray-600">Status: {order.status}</div>
              </div>
            </Tooltip>
          </Marker>
        );
      })}
    </>
  );
}
