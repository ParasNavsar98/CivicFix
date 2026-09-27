import React from 'react';
import { BarChart3, TrendingUp, ShieldAlert, CheckCircle } from 'lucide-react';

export const AnalyticsPage: React.FC = () => {
  return (
    <div className="space-y-6 animate-in fade-in">
      <div>
        <h1 className="text-2xl font-extrabold text-[#17332F]">Government Analytics & Resolution SLAs</h1>
        <p className="text-xs text-[#66736F] mt-1">Performance indicators across primary domains and district jurisdictions.</p>
      </div>

      <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
        <div className="glass-card rounded-2xl p-5">
          <span className="text-[10px] font-bold text-[#66736F] uppercase tracking-wider block">Average Resolution Time</span>
          <span className="text-3xl font-black text-[#17332F] mt-1 block">4.2 Days</span>
          <span className="text-xs text-[#087F6B] font-semibold mt-1 inline-flex items-center gap-1">
            <TrendingUp className="w-3.5 h-3.5" /> 18% faster than SLA target
          </span>
        </div>

        <div className="glass-card rounded-2xl p-5">
          <span className="text-[10px] font-bold text-[#66736F] uppercase tracking-wider block">AI Classification Accuracy</span>
          <span className="text-3xl font-black text-[#6A5ACD] mt-1 block">91.4%</span>
          <span className="text-xs text-[#66736F] mt-1 block">Based on reviewer acceptance rate</span>
        </div>

        <div className="glass-card rounded-2xl p-5">
          <span className="text-[10px] font-bold text-[#66736F] uppercase tracking-wider block">University Matching Rate</span>
          <span className="text-3xl font-black text-[#0F766E] mt-1 block">84.0%</span>
          <span className="text-xs text-[#66736F] mt-1 block">Accepted rank 1-2 assignments</span>
        </div>
      </div>
    </div>
  );
};
