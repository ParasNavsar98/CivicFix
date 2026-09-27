import React, { useState } from 'react';
import { Problem } from '../../types';
import { MapPin, Navigation, Layers, Filter } from 'lucide-react';
import { StatusBadge } from './StatusBadge';
import { SeverityBadge } from './SeverityBadge';

interface MapComponentProps {
  problems: Problem[];
  onSelectProblem?: (problem: Problem) => void;
  height?: string;
}

export const MapComponent: React.FC<MapComponentProps> = ({ problems, onSelectProblem, height = 'h-[450px]' }) => {
  const [selected, setSelected] = useState<Problem | null>(problems[0] || null);

  return (
    <div className={`glass-card rounded-2xl p-4 relative overflow-hidden flex flex-col ${height}`}>
      {/* Map Control Bar */}
      <div className="flex items-center justify-between pb-3 border-b border-[#D8D8C8] mb-3 z-10">
        <div className="flex items-center gap-2">
          <span className="p-1.5 rounded-lg bg-[#0F766E]/10 text-[#0F766E] border border-[#0F766E]/20">
            <Navigation className="w-4 h-4" />
          </span>
          <div>
            <h4 className="text-xs font-semibold text-[#17332F]">Interactive Civic GIS Map</h4>
            <p className="text-[10px] text-[#66736F]">Showing public-safe problem locations across Jharkhand districts</p>
          </div>
        </div>

        <div className="flex items-center gap-2">
          <span className="text-xs px-2.5 py-1 rounded-lg bg-[#FFFDF5] text-[#17332F] border border-[#D8D8C8] flex items-center gap-1 shadow-xs">
            <Layers className="w-3.5 h-3.5 text-[#6A5ACD]" /> {problems.length} Markers
          </span>
        </div>
      </div>

      {/* Map Visual Container (Light Warm Canvas Graphic Map) */}
      <div className="flex-1 relative rounded-xl bg-[#F4F1E1] border border-[#D8D8C8] overflow-hidden flex items-center justify-center p-6">
        {/* Background Grid Lines */}
        <div
          className="absolute inset-0 opacity-40 pointer-events-none"
          style={{
            backgroundImage:
              'radial-gradient(circle at 1px 1px, rgba(3, 79, 70, 0.12) 1px, transparent 0)',
            backgroundSize: '24px 24px',
          }}
        />

        {/* Ambient District Region Overlay (SVG Map Canvas) */}
        <svg className="absolute inset-0 w-full h-full opacity-30 pointer-events-none" viewBox="0 0 800 500" fill="none">
          <path
            d="M150 120 Q300 80 450 140 T700 180 Q650 350 480 420 T200 380 Z"
            stroke="#034F46"
            strokeWidth="1.5"
            strokeDasharray="4 4"
            fill="rgba(3, 79, 70, 0.05)"
          />
          <path
            d="M250 180 Q400 150 550 220 T400 360 Z"
            stroke="#6A5ACD"
            strokeWidth="1"
            fill="rgba(106, 90, 205, 0.04)"
          />
        </svg>

        {/* Dynamic Pins */}
        <div className="absolute inset-0 p-8 flex items-center justify-center">
          {problems.map((prob, idx) => {
            // Position pin visually based on index or coordinates fallback
            const lefts = ['25%', '65%', '45%', '78%', '35%'];
            const tops = ['35%', '28%', '62%', '70%', '48%'];
            const isSelected = selected?.problemId === prob.problemId;

            return (
              <button
                key={prob.problemId}
                onClick={() => {
                  setSelected(prob);
                  if (onSelectProblem) onSelectProblem(prob);
                }}
                className={`absolute group transform -translate-x-1/2 -translate-y-1/2 transition-all duration-300 z-20 ${
                  isSelected ? 'scale-125 z-30' : 'hover:scale-110'
                }`}
                style={{ left: lefts[idx % lefts.length], top: tops[idx % tops.length] }}
              >
                <div className="relative flex flex-col items-center">
                  <div
                    className={`p-2 rounded-full shadow-md transition-all ${
                      prob.severity === 'CRITICAL'
                        ? 'bg-[#B83A3A] text-white ring-4 ring-[#B83A3A]/20'
                        : prob.severity === 'HIGH'
                        ? 'bg-[#B7791F] text-white ring-4 ring-[#B7791F]/20'
                        : 'bg-[#034F46] text-white ring-4 ring-[#034F46]/20'
                    }`}
                  >
                    <MapPin className="w-4 h-4" />
                  </div>

                  <span className="mt-1 px-2 py-0.5 rounded bg-[#FFFDF5] text-[10px] font-semibold text-[#17332F] border border-[#D8D8C8] shadow-md whitespace-nowrap opacity-90 group-hover:opacity-100">
                    {prob.location.district}
                  </span>
                </div>
              </button>
            );
          })}
        </div>

        {/* Selected Map Card Overlay */}
        {selected && (
          <div className="absolute bottom-4 left-4 right-4 bg-[#FFFDF5]/95 backdrop-blur-md border border-[#D8D8C8] p-4 rounded-xl shadow-xl z-30 flex flex-col sm:flex-row items-start sm:items-center justify-between gap-3">
            <div>
              <div className="flex items-center gap-2 mb-1">
                <span className="text-[10px] font-mono text-[#6A5ACD] font-bold">{selected.problemId}</span>
                <SeverityBadge severity={selected.severity || 'MODERATE'} size="sm" />
                <StatusBadge status={selected.status} size="sm" />
              </div>
              <h5 className="text-sm font-bold text-[#17332F] line-clamp-1">{selected.title}</h5>
              <p className="text-xs text-[#66736F] line-clamp-1">{selected.location.address || `${selected.location.district}, ${selected.location.state}`}</p>
            </div>

            {onSelectProblem && (
              <button
                onClick={() => onSelectProblem(selected)}
                className="px-3 py-1.5 rounded-lg text-xs font-semibold bg-[#034F46] hover:bg-[#0F766E] text-white transition self-end sm:self-auto shrink-0 shadow-xs cursor-pointer"
              >
                View Problem Details
              </button>
            )}
          </div>
        )}
      </div>
    </div>
  );
};
