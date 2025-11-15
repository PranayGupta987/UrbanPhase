import { useState } from "react";
import MapView from "./components/MapView";
import Sidebar from "./components/Sidebar";
import MetricsPanel from "./components/MetricsPanel";
import SimulationPanel from "./components/SimulationPanel";
import { SimulationResponse } from "./types";

function App() {
  const [simulationData, setSimulationData] = useState<SimulationResponse | null>(null);
  const [activeLayer, setActiveLayer] = useState<"traffic" | "aqi">("traffic");

  const [selectedCameras, setSelectedCameras] = useState<any[]>([]);

  return (
    <div className="flex h-screen w-screen overflow-hidden">
      
      {/* Sidebar */}
      <Sidebar activeLayer={activeLayer} onLayerChange={setActiveLayer} />

      {/* Map + Floating Panels */}
      <div className="flex-1 relative">

        {/* MAP */}
        <MapView
          activeLayer={activeLayer}
          simulationData={simulationData}
          onCameraSelect={(cams) => {
            console.log("Selected Cameras:", cams);
            setSelectedCameras(cams);
          }}
        />

        {/* SIMULATION PANEL — FLOATING, FIXED POSITION */}
        <div className="absolute top-3/4 right- -translate-y-1/2 z-[60]">
          <SimulationPanel
            cameras={selectedCameras}
            onSimulate={setSimulationData}
          />
        </div>

        {/* METRICS PANEL — FLOATING ABOVE SIMULATION PANEL */}
        {simulationData && (
          <div className="absolute top-8 right-8 z-[50]">
            <MetricsPanel simulationData={simulationData} />
          </div>
        )}
      </div>
    </div>
  );
}

export default App;
