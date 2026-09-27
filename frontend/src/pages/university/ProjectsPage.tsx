import React from 'react';
import { Briefcase, AlertCircle, Clock, CheckCircle2, Users, Target } from 'lucide-react';

export const ProjectsPage: React.FC = () => {
  return (
    <div className="space-y-6 animate-in fade-in">
      <div>
        <h1 className="text-2xl font-extrabold text-[#17332F]">University Research Projects</h1>
        <p className="text-xs text-[#66736F] mt-1">Field deployment projects, faculty mentorship, and milestone execution.</p>
      </div>

      {/* Backend Integration Pending Banner */}
      <div className="p-4 rounded-2xl bg-[#E9DFFF] border border-[#6A5ACD]/30 text-xs text-[#6A5ACD] flex items-center justify-between">
        <div className="flex items-center gap-2">
          <AlertCircle className="w-4 h-4 text-[#6A5ACD] shrink-0" />
          <span>
            <strong>Backend Integration Notice</strong>: Project lifecycle & milestone verification UI is active in frontend mockup mode. Full automated milestone telemetry backend integration pending in next release.
          </span>
        </div>
      </div>

      {/* Sample Project Cards */}
      <div className="space-y-4">
        <div className="glass-card rounded-3xl p-6 border border-[#D8D8C8] space-y-4">
          <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-3 pb-3 border-b border-[#D8D8C8]">
            <div>
              <span className="text-[10px] font-mono font-bold text-[#6A5ACD]">PRJ-BIT-901</span>
              <h3 className="text-lg font-bold text-[#17332F] mt-0.5">Eco-Friendly Biogas Modular School Toilet Unit</h3>
              <p className="text-xs text-[#66736F]">Targeting Problem CF-2026-001 (Namkum School)</p>
            </div>
            <span className="text-xs px-3 py-1 rounded-full bg-[#0F766E]/10 text-[#0F766E] font-bold border border-[#0F766E]/30 self-start sm:self-auto">
              Stage: PROTOTYPE
            </span>
          </div>

          <div className="grid grid-cols-1 sm:grid-cols-3 gap-3 text-xs">
            <div className="bg-[#F7F5E8] p-3 rounded-xl border border-[#D8D8C8]">
              <span className="text-[10px] text-[#66736F] uppercase block font-semibold">Faculty Mentor</span>
              <span className="font-bold text-[#17332F] mt-0.5 block">Dr. A. K. Singh</span>
            </div>
            <div className="bg-[#F7F5E8] p-3 rounded-xl border border-[#D8D8C8]">
              <span className="text-[10px] text-[#66736F] uppercase block font-semibold">Student Team</span>
              <span className="font-bold text-[#17332F] mt-0.5 block">Team GreenTech (4 Researchers)</span>
            </div>
            <div className="bg-[#F7F5E8] p-3 rounded-xl border border-[#D8D8C8]">
              <span className="text-[10px] text-[#66736F] uppercase block font-semibold">Industry Partner</span>
              <span className="font-bold text-[#0F766E] mt-0.5 block">CleanTech Innovations</span>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
};
