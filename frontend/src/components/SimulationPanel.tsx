import { useState } from "react";
import { Play, RotateCcw, Loader2 } from "lucide-react";
import { api } from "../services/api";
import { SimulationResponse } from "../types";

interface SimulationPanelProps {
  cameras: any[];
  onSimulate: (data: SimulationResponse | null) => void;
}

function SimulationPanel({ cameras, onSimulate }: SimulationPanelProps) {
  const [vehicleReduction, setVehicleReduction] = useState(30);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const handleSimulate = async () => {
    if (!cameras || cameras.length === 0) {
      setError("No camera selected.");
      return;
    }

    setLoading(true);
    setError(null);

    try {
      console.log("Cameras received by SimulationPanel:", cameras);
      console.log("Sending payload:", {
        vehicle_reduction: vehicleReduction,
        cameras: cameras
      });

      const result = await api.runSimulation(vehicleReduction, cameras);
      console.log("Simulation result:", result);
      onSimulate(result);
    } catch (err) {
      const msg = err instanceof Error ? err.message : "Simulation failed";
      setError(msg);
      console.error("Simulation error:", msg);
    } finally {
      setLoading(false);
    }
  };

  const handleReset = () => {
    onSimulate(null);
    setVehicleReduction(30);
    setError(null);
  };

  return (
    <div className="bg-white shadow-xl rounded-xl p-6 w-96">
      <h2 className="text-xl font-bold mb-4">Scenario Simulation</h2>

      <label className="text-sm mb-1 block">Vehicle Reduction</label>
      <input
        type="range"
        min="0"
        max="100"
        value={vehicleReduction}
        onChange={(e) => setVehicleReduction(Number(e.target.value))}
        className="w-full"
      />

      <p className="mt-2 text-primary-600 font-bold">{vehicleReduction}%</p>

      {error && <p className="text-red-600 mt-3">{error}</p>}

      <button
        onClick={handleSimulate}
        className="w-full bg-blue-600 hover:bg-blue-700 text-white py-2 rounded-lg mt-4"
        disabled={loading}
      >
        {loading ? "Running..." : "Run Simulation"}
      </button>

      <button
        onClick={handleReset}
        className="w-full bg-gray-300 py-2 rounded-lg mt-2"
        disabled={loading}
      >
        Reset
      </button>
    </div>
  );
}

export default SimulationPanel;