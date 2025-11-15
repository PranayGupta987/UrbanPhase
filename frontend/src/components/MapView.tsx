import { useEffect, useRef } from "react";
import maplibregl from "maplibre-gl";
import { SimulationResponse } from "../types";

interface MapViewProps {
  activeLayer: "traffic" | "aqi";
  simulationData: SimulationResponse | null;
  onCameraSelect: (cams: any[]) => void;
}

function MapView({ activeLayer, simulationData, onCameraSelect }: MapViewProps) {
  const mapContainer = useRef<HTMLDivElement>(null);
  const map = useRef<maplibregl.Map | null>(null);

  // -----------------------------
  //  INIT MAP
  // -----------------------------
  useEffect(() => {
    if (!mapContainer.current) return;

    const mapInstance = new maplibregl.Map({
      container: mapContainer.current,
      style: {
        version: 8,
        glyphs: "https://demotiles.maplibre.org/font/{fontstack}/{range}.pbf",
        sources: {
          osm: {
            type: "raster",
            tiles: ["https://tile.openstreetmap.org/{z}/{x}/{y}.png"],
            tileSize: 256,
          },
        },
        layers: [
          {
            id: "osm",
            type: "raster",
            source: "osm",
          },
        ],
      },
      center: [103.85, 1.29],
      zoom: 12,
    });

    map.current = mapInstance;

    // Add traffic layer
    mapInstance.on("load", () => {
      mapInstance.addSource("traffic", {
        type: "geojson",
        data: {
          type: "FeatureCollection",
          features: [],
        },
      });

      mapInstance.addLayer({
        id: "traffic-lines",
        type: "line",
        source: "traffic",
        paint: {
          "line-color": "#22c55e", // green default
          "line-width": 6,
          "line-opacity": 1,
        },
      });

      console.log("Map and traffic layer ready.");

      // NOW load traffic data
      loadTrafficData();
    });

    return () => {
      if (mapInstance) mapInstance.remove();
      map.current = null;
    };
  }, []);

  // -----------------------------
  // LOAD TRAFFIC DATA FROM BACKEND
  // -----------------------------
  const loadTrafficData = async () => {
    if (!map.current) return;

    try {
      const response = await fetch("http://127.0.0.1:8000/data/traffic");
      const data = await response.json();

      console.log("Traffic Data:", data);

      const source = map.current.getSource("traffic") as maplibregl.GeoJSONSource;
      if (source) {
        source.setData(data);
        console.log("Traffic set on map.");
      }
    } catch (err) {
      console.error("Failed to load traffic data:", err);
    }
  };

  // -----------------------------
  // APPLY SIMULATION COLOR
  // -----------------------------
  useEffect(() => {
    if (!map.current || !simulationData) return;

    console.log("Simulation Data:", simulationData);

    const congestion = simulationData.simulated.congestion;

    const color =
      congestion < 0.4
        ? "#22c55e"
        : congestion < 0.7
        ? "#eab308"
        : "#ef4444";

    try {
      map.current.setPaintProperty("traffic-lines", "line-color", color);
      console.log("Applied color:", color);
    } catch (err) {
      console.error("Color apply error:", err);
    }
  }, [simulationData]);

  // -----------------------------
  // CAMERA SELECT
  // -----------------------------
  useEffect(() => {
    if (!map.current) return;

    map.current.on("click", (e) => {
      const lngLat = e.lngLat;

      const clickedCamera = {
        CameraID: "cam1",
        Latitude: lngLat.lat,
        Longitude: lngLat.lng,
        ImageLink:
          "https://dm-traffic-camera-itsc.s3.ap-southeast-1.amazonaws.com/2025-11-15/11-40/6715_1129_20251115034051_554D82.jpg?X-Amz-Security-Token=IQoJb3JpZ2luX2VjEKr%2F%2F%2F%2F%2F%2F%2F%2F%2F%2FwEaDmFwLXNvdXRoZWFzdC0xIkYwRAIgDafYm1PeKG5jq7Hpu7hOqriv4mJ%2BMzWHBBAZ6D0SXlgCIE1LqPa1j8MiDqlegjVYFsyS4sAfc0zd5fz3ahYw6JfcKvsCCHMQBBoMMzQwNjQ1MzgxMzA0Igy4%2FSrrTujbkJEW6M4q2AKEY1e29aE9uFh%2FX6KpiKJKqiD6TBFB2wXjx%2Fz0QUNtESiY8omgpZO%2FO7jXeH63u2T6JE9Yz4YoEG8JVnX54%2BUqTT%2BBcUWI2%2FHw4IFwjDLkgTRHtt%2BkHVSvDmFKCaLCAB8jNPi%2Bl4N2j%2FtO7Di4lU6uZ9zzq9ykOEuh25%2FGBKAhZVG7MGBYTUNBUcPRaG0VVdtF9dsUezHdxx14It9VjNTQzjW%2FRL5u0idqQoJrUFThXd48bM9Ts9Hl5NDVRLbacAxgbtBiys%2BIlbnPwyTRU19f7Stuy6qzkUlWrJ7MFcz0mcUGU2Z2TpIY9Or5wTIo7bxNbNT%2FoF7GtpkFquP4h1uiKt6rO%2FzypkK3hP4vbPHx5G37vHbKXu6pdpJKw7rDmdkthmJVBdhM%2ByDSfitepz7s0ilCLwHqrTnw1xmNu0woSYwBILci5T5TiYG2izh5ZpsQsGOm%2Fh9ddzCFwt%2FIBjqfASSf0FWz3aXEtn9e0j4Y7S3xkukD3tK0h4qXKNKORNjsH603EKXMbWhhj9ibOjc%2FXGuAYeWYY8DZIv%2BIDdbexVk8L9og0cvib2UmIwVKWCAnclx2nrH5SU0qBfzVPVOu0ch%2BeupM6Ui%2F0vHFcA9kfPU2WS%2B8qNOR7Za2Uctdy05byJSEWkYZ0C14BeRrnpKpaJCsIwfniNVOqPFR%2FED4ag%3D%3D&X-Amz-Algorithm=AWS4-HMAC-SHA256&X-Amz-Date=20251115T034051Z&X-Amz-SignedHeaders=host&X-Amz-Credential=ASIAU6UAMAS4MKMZ5YFN%2F20251115%2Fap-southeast-1%2Fs3%2Faws4_request&X-Amz-Expires=900&X-Amz-Signature=e875ff6bef71f05993941f96200f5dd7220bd85f46990145c4282d2374cd145d",
        Timestamp: new Date().toISOString(),
      };

      console.log("Selected Camera:", clickedCamera);
      onCameraSelect([clickedCamera]);
    });
  }, []);

  return <div ref={mapContainer} className="absolute inset-0 w-full h-full" />;
}

export default MapView;
