import { SimulationResponse } from "../types";
import { ArrowUp, ArrowDown } from "lucide-react";
import { motion } from "framer-motion";

interface MetricsPanelProps {
  simulationData: SimulationResponse;
}

function diff(current: number, previous: number) {
  const d = current - previous;
  return {
    value: Math.abs(d).toFixed(2),
    positive: d > 0,
    negative: d < 0,
  };
}

export default function MetricsPanel({ simulationData }: MetricsPanelProps) {
  const before = simulationData.baseline;
  const after = simulationData.simulated;

  const metrics = [
    {
      label: "Congestion",
      before: before.congestion,
      after: after.congestion,
      format: (v: number) => v.toFixed(3),
    },
    {
      label: "Vehicle Count",
      before: before.total_vehicle_count,
      after: after.total_vehicle_count,
      format: (v: number) => v.toFixed(0),
    },
    {
      label: "PM2.5 (µg/m³)",
      before: before.pm25,
      after: after.pm25,
      format: (v: number) => v.toFixed(2),
    },
    {
      label: "Air Quality Index",
      before: before.aqi,
      after: after.aqi,
      format: (v: number) => `${v} (${after.aqi_category})`,
    },
  ];

  return (
    <motion.div
      initial={{ opacity: 0, y: 40 }}
      animate={{ opacity: 1, y: 0 }}
      className="bg-white shadow-2xl rounded-2xl p-6 w-[380px] border border-gray-100"
    >
      <h2 className="text-xl font-bold mb-4 text-gray-900">
        Simulation Results
      </h2>

      <p className="text-sm text-gray-500 mb-4">
        Vehicle Reduction Applied:{" "}
        <span className="font-semibold text-blue-600">
          {after.reduce_vehicles_pct}%
        </span>
      </p>

      <div className="space-y-5">
        {metrics.map((m) => {
          const d = diff(m.after, m.before);
          return (
            <div
              key={m.label}
              className="bg-gray-50 p-4 rounded-xl border border-gray-200"
            >
              <div className="flex justify-between items-center mb-2">
                <span className="text-gray-600 font-medium">{m.label}</span>

                <div className="flex items-center gap-1">
                  {d.positive && (
                    <span className="flex items-center text-red-500 text-sm">
                      <ArrowUp size={16} /> {d.value}
                    </span>
                  )}
                  {d.negative && (
                    <span className="flex items-center text-green-600 text-sm">
                      <ArrowDown size={16} /> {d.value}
                    </span>
                  )}
                  {!d.positive && !d.negative && (
                    <span className="text-gray-500 text-sm">0</span>
                  )}
                </div>
              </div>

              <div className="flex justify-between text-sm">
                <span className="text-gray-800">
                  Before:{" "}
                  <span className="font-semibold text-gray-900">
                    {m.format(m.before)}
                  </span>
                </span>

                <span className="text-gray-800">
                  After:{" "}
                  <span className="font-semibold text-blue-600">
                    {m.format(m.after)}
                  </span>
                </span>
              </div>
            </div>
          );
        })}
      </div>
    </motion.div>
  );
}
