export interface TrafficFeature {
  type: 'Feature';
  geometry: {
    type: 'LineString';
    coordinates: number[][];
  };
  properties: {
    name?: string;
    speed?: number;
    avg_speed?: number;
    congestion?: string;
    congestion_level?: number;
    volume?: number;
    vehicle_count?: number;
    capacity?: number;
    segment_id?: number;
    link_id?: string;
  };
}

export interface AQIFeature {
  type: 'Feature';
  geometry: {
    type: 'Point';
    coordinates: number[];
  };
  properties: {
    aqi: number;
    category: string;
    pm25: number;
    pm10?: number;
    no2?: number;
    o3?: number;
    station: string;
    color?: string;
  };
}

export interface GeoJSONCollection {
  type: 'FeatureCollection';
  features: (TrafficFeature | AQIFeature)[];
}

export interface SimulationResponse {
  before: GeoJSONCollection;
  after: GeoJSONCollection;
  metrics: {
    avg_congestion_before: number;
    avg_congestion_after: number;
    avg_speed_before: number;
    avg_speed_after: number;
    aqi_before: number;
    aqi_after: number;
  };
}

export interface SimulationRequest {
  vehicle_reduction: number;
}
