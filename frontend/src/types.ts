export interface GeoJSONFeatureProperties {
  [key: string]: any;
}

export interface GeoJSONFeature {
  type: 'Feature';
  geometry:
    | {
        type: 'LineString';
        coordinates: [number, number][];
      }
    | {
        type: 'Point';
        coordinates: [number, number];
      };
  properties: GeoJSONFeatureProperties;
}

export interface GeoJSONCollection {
  type: 'FeatureCollection';
  features: GeoJSONFeature[];
}

export interface SimulationRequest {
  vehicle_reduction: number; // 0–100
  segment_ids?: number[] | null;
}

export interface SimulationMetrics {
  congestion: number;
  total_vehicle_count: number;
  pm25: number;
  aqi: number;
  aqi_category: string;
}

export interface SimulationResponse {
  baseline: SimulationMetrics;
  simulated: SimulationMetrics & {
    reduce_vehicles_pct: number;
  };
}

