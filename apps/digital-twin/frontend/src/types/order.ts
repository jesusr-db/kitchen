export interface OrderEvent {
  event_type: string;
  timestamp: string;
  body?: Record<string, any>;
}

export interface OrderLifecycle {
  order_id: string;
  location: string;
  brand: string;
  customer_lat: number | null;
  customer_lon: number | null;
  events: OrderEvent[];
  created_at: string;
  completed_at: string | null;
  status: string;
}

export interface OrderMetrics {
  total_orders: number;
  completed_orders: number;
  in_progress_orders: number;
  avg_prep_time_minutes: number | null;
  avg_delivery_time_minutes: number | null;
  avg_total_time_minutes: number | null;
}

export interface TimeRangeResponse {
  location: string;
  start_time: string;
  end_time: string;
  metrics: OrderMetrics;
  orders: OrderLifecycle[];
}
