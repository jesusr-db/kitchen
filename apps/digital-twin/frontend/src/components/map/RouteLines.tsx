import { Polyline } from 'react-leaflet';
import type { OrderLifecycle } from '@/types/order';
import type { LocationConfig } from '@/types/location';

interface RouteLinesProps {
  orders: OrderLifecycle[];
  kitchen: LocationConfig;
}

function getRouteColor(status: string): string {
  switch (status) {
    case 'completed':
      return '#10b981'; // green
    case 'out_for_delivery':
      return '#3b82f6'; // blue
    case 'ready_for_pickup':
      return '#f59e0b'; // orange
    default:
      return '#9ca3af'; // gray
  }
}

export function RouteLines({ orders, kitchen }: RouteLinesProps) {
  return (
    <>
      {orders.map((order) => {
        if (!order.customer_lat || !order.customer_lon) return null;

        const positions: [number, number][] = [
          [kitchen.gk_lat, kitchen.gk_lon],
          [order.customer_lat, order.customer_lon],
        ];

        return (
          <Polyline
            key={order.order_id}
            positions={positions}
            pathOptions={{
              color: getRouteColor(order.status),
              weight: 2,
              opacity: order.status === 'completed' ? 0.4 : 0.7,
              dashArray: order.status === 'completed' ? '5, 5' : undefined,
            }}
          />
        );
      })}
    </>
  );
}
