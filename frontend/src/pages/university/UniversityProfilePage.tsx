import React, { useState } from 'react';
import { Building, Award, CheckCircle, Save } from 'lucide-react';

export const UniversityProfilePage: React.FC = () => {
  const [activeProjects, setActiveProjects] = useState(6);
  const [maxProjects, setMaxProjects] = useState(10);
  const [availability, setAvailability] = useState<'AVAILABLE' | 'LIMITED' | 'UNAVAILABLE'>('AVAILABLE');
  const [saved, setSaved] = useState(false);

  const handleSave = (e: React.FormEvent) => {
    e.preventDefault();
    setSaved(true);
    setTimeout(() => setSaved(false), 3000);
  };

  return (
    <div className="max-w-3xl mx-auto space-y-6 animate-in fade-in">
      <div>
        <h1 className="text-2xl font-extrabold text-[#17332F]">University Profile & Capacity Management</h1>
        <p className="text-xs text-[#66736F] mt-1">Manage institutional expertise, faculty roster, lab infrastructure, and project capacity.</p>
      </div>

      <form onSubmit={handleSave} className="glass-card rounded-3xl p-6 sm:p-8 space-y-6 text-xs">
        {saved && (
          <div className="p-3 rounded-xl bg-[#087F6B]/15 text-[#087F6B] border border-[#087F6B]/30 flex items-center gap-2">
            <CheckCircle className="w-4 h-4" /> Capacity and capabilities updated successfully.
          </div>
        )}

        <div className="space-y-4">
          <div>
            <label className="block font-semibold text-[#17332F] mb-1">University Name</label>
            <input
              type="text"
              readOnly
              value="Birla Institute of Technology (BIT Mesra)"
              className="w-full px-3.5 py-2.5 rounded-xl bg-[#FFFDF5] border border-[#D8D8C8] text-[#17332F] font-bold"
            />
          </div>

          <div className="grid grid-cols-1 sm:grid-cols-3 gap-4">
            <div>
              <label className="block font-semibold text-[#17332F] mb-1">Active Projects</label>
              <input
                type="number"
                value={activeProjects}
                onChange={(e) => setActiveProjects(Number(e.target.value))}
                className="w-full px-3.5 py-2.5 rounded-xl bg-[#FFFDF5] border border-[#D8D8C8] text-[#17332F]"
              />
            </div>

            <div>
              <label className="block font-semibold text-[#17332F] mb-1">Maximum Projects</label>
              <input
                type="number"
                value={maxProjects}
                onChange={(e) => setMaxProjects(Number(e.target.value))}
                className="w-full px-3.5 py-2.5 rounded-xl bg-[#FFFDF5] border border-[#D8D8C8] text-[#17332F]"
              />
            </div>

            <div>
              <label className="block font-semibold text-[#17332F] mb-1">Availability Status</label>
              <select
                value={availability}
                onChange={(e) => setAvailability(e.target.value as any)}
                className="w-full px-3.5 py-2.5 rounded-xl bg-[#FFFDF5] border border-[#D8D8C8] text-[#17332F] font-bold"
              >
                <option value="AVAILABLE">AVAILABLE (Normal Scoring)</option>
                <option value="LIMITED">LIMITED (Halves Free Ratio)</option>
                <option value="UNAVAILABLE">UNAVAILABLE (Zero Capacity Score)</option>
              </select>
            </div>
          </div>

          <div>
            <label className="block font-semibold text-[#17332F] mb-1">Departments</label>
            <input
              type="text"
              readOnly
              value="Environmental Science, Civil Engineering, Electrical Engineering, Biotechnology"
              className="w-full px-3.5 py-2.5 rounded-xl bg-[#FFFDF5] border border-[#D8D8C8] text-[#66736F]"
            />
          </div>

          <div>
            <label className="block font-semibold text-[#17332F] mb-1">Core Expertise Keywords</label>
            <input
              type="text"
              readOnly
              value="Sanitation Infrastructure, Water Supply Design, Environmental Engineering, Renewable Microgrids"
              className="w-full px-3.5 py-2.5 rounded-xl bg-[#FFFDF5] border border-[#D8D8C8] text-[#6A5ACD] font-mono"
            />
          </div>
        </div>

        <div className="pt-4 border-t border-[#D8D8C8] flex justify-end">
          <button
            type="submit"
            className="px-6 py-2.5 rounded-full font-bold bg-[#034F46] text-white hover:bg-[#0F766E] transition shadow-md flex items-center gap-2 cursor-pointer"
          >
            <Save className="w-4 h-4" /> Save Profile Settings
          </button>
        </div>
      </form>
    </div>
  );
};
