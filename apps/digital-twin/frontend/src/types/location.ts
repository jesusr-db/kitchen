export interface DateRange {
  start: string;
  end: string;
}

export interface LocationConfig {
  location_name: string;
  display_name: string;
  gk_lat: number;
  gk_lon: number;
  radius_mi: number;
  total_orders: number;
  date_range: DateRange;
}

export interface LocationsResponse {
  locations: LocationConfig[];
}
