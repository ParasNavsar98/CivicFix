import React, { useState } from 'react';
import { Compass, ShieldCheck, ArrowRight, BookOpen, Building2 } from 'lucide-react';

export const RoutingPage: React.FC = () => {
  const [route, setRoute] = useState<'GOVERNMENT' | 'RESEARCH' | 'BOTH'>('BOTH');
  const [rationale, setRationale] = useState('Problem requires immediate government infrastructure funding and university research design.');
  const [routed, setRouted] = useState(false);

  return (
    <div className="max-w-2xl mx-auto space-y-6 animate-in fade-in">
      <div>
        <h1 className="text-2xl font-extrabold text-[#17332F]">Sector Routing Dispatch</h1>
        <p className="text-xs text-[#66736F] mt-1">Route validated problems to government departments, university research matching, or both.</p>
      </div>

      {!routed ? (
        <div className="glass-card rounded-3xl p-6 sm:p-8 space-y-6 border border-[#D8D8C8] text-xs">
          <div className="p-4 rounded-2xl bg-[#F7F5E8] border border-[#D8D8C8] space-y-1">
            <span className="text-[10px] font-mono font-bold text-[#6A5ACD]">CF-2026-001</span>
            <h3 className="text-sm font-bold text-[#17332F]">Unsafe school toilets causing students to miss classes</h3>
            <span className="text-[10px] text-[#66736F] block">Sanitation • Toilets • Education</span>
          </div>

          <div className="space-y-2">
            <label className="block font-semibold text-[#17332F]">Select Resolution Pathway</label>
            <div className="grid grid-cols-1 sm:grid-cols-3 gap-3">
              {[
                { id: 'GOVERNMENT', label: 'Government Action Only', icon: <Building2 className="w-4 h-4 text-[#034F46]" /> },
                { id: 'RESEARCH', label: 'University Match Only', icon: <BookOpen className="w-4 h-4 text-[#6A5ACD]" /> },
                { id: 'BOTH', label: 'Dual Routing (Both)', icon: <Compass className="w-4 h-4 text-[#087F6B]" /> },
              ].map((item) => (
                <button
                  key={item.id}
                  type="button"
                  onClick={() => setRoute(item.id as any)}
                  className={`p-3 rounded-xl border text-left flex flex-col items-center text-center transition cursor-pointer ${
                    route === item.id
                      ? 'bg-[#E9DFFF] border-[#6A5ACD]/50 text-[#17332F] font-bold'
                      : 'bg-[#FFFDF5] border-[#D8D8C8] text-[#66736F] hover:text-[#17332F]'
                  }`}
                >
                  <div className="mb-2">{item.icon}</div>
                  <span>{item.label}</span>
                </button>
              ))}
            </div>
          </div>

          <div>
            <label className="block font-semibold text-[#B7791F] mb-1">Human Officer Rationale (Mandatory)</label>
            <textarea
              rows={3}
              required
              value={rationale}
              onChange={(e) => setRationale(e.target.value)}
              className="w-full px-3.5 py-2.5 rounded-xl bg-[#FFFDF5] border border-[#D8D8C8] text-[#17332F]"
            />
          </div>

          <div className="pt-2 flex justify-end">
            <button
              onClick={() => setRouted(true)}
              className="px-6 py-2.5 rounded-full font-bold bg-[#034F46] text-white hover:bg-[#0F766E] transition shadow-md flex items-center gap-2 cursor-pointer"
            >
              Confirm & Dispatch Route <ArrowRight className="w-4 h-4" />
            </button>
          </div>
        </div>
      ) : (
        <div className="glass-card rounded-3xl p-8 text-center space-y-3 border border-[#087F6B]/30 bg-[#FFFDF5]">
          <ShieldCheck className="w-10 h-10 text-[#087F6B] mx-auto" />
          <h3 className="text-lg font-bold text-[#17332F]">Problem Successfully Routed</h3>
          <p className="text-xs text-[#66736F]">Case dispatched to 7-Factor University Matcher and PWD Department.</p>
        </div>
      )}
    </div>
  );
};
