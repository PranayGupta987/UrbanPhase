import { GeoJSONCollection, SimulationResponse } from "../types";

const API_BASE_URL = import.meta.env.VITE_API_URL || "http://127.0.0.1:8000";

export const api = {
  async getStatus() {
    const response = await fetch(`${API_BASE_URL}/status`);
    if (!response.ok) throw new Error("Failed to fetch status");
    return response.json();
  },

  async getTrafficData(): Promise<GeoJSONCollection> {
    const response = await fetch(`${API_BASE_URL}/data/traffic`);
    if (!response.ok) throw new Error("Failed to fetch traffic data");
    return response.json();
  },

  async getAQIData(): Promise<GeoJSONCollection> {
    const response = await fetch(`${API_BASE_URL}/data/aqi`);
    if (!response.ok) throw new Error("Failed to fetch AQI data");
    return response.json();
  },

  async getWeatherData() {
    const response = await fetch(`${API_BASE_URL}/data/weather`);
    if (!response.ok) throw new Error("Failed to fetch weather data");
    return response.json();
  },

  /** 
   * Runs the full ML Simulation:
   * - vehicle reduction %
   * - selected cameras (with ImageLink, Lat, Lon, etc.)
   */
  async runSimulation(vehicleReduction: number, cameras: any[]): Promise<SimulationResponse> {
    const response = await fetch(`${API_BASE_URL}/simulate`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({
        vehicle_reduction: vehicleReduction,
        cameras: cameras,
      }),
    });

    if (!response.ok) {
      const errText = await response.text();
      throw new Error(errText || "Simulation failed");
    }

    return response.json();
  },
};
