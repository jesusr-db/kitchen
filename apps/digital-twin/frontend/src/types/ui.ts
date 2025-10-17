export type PlaybackState = 'stopped' | 'playing' | 'paused';

export interface TimeRange {
  start: Date;
  end: Date;
}

export interface MapViewport {
  center: [number, number];
  zoom: number;
}
