import React, { useState } from 'react';
import { Building, Save, CheckCircle } from 'lucide-react';

export const OrganizationProfilePage: React.FC = () => {
  const [name, setName] = useState('CleanTech Innovations Pvt Ltd');
  const [type, setType] = useState('Industry');
  const [saved, setSaved] = useState(false);

  const handleSave = (e: React.FormEvent) => {
    e.preventDefault();
    setSaved(true);
    setTimeout(() => setSaved(false), 3000);
  };

  return (
    <div className="max-w-3xl mx-auto space-y-6 animate-in fade-in">
      <div>
        <h1 className="text-2xl font-extrabold text-[#17332F]">Organization Profile</h1>
        <p className="text-xs text-[#66736F] mt-1">Manage partner credentials, technological capabilities, and CSR focus areas.</p>
      </div>

      <form onSubmit={handleSave} className="bg-[#FFFDF5] rounded-3xl p-6 sm:p-8 space-y-6 text-xs border border-[#D8D8C8] shadow-sm">
        {saved && (
          <div className="p-3 rounded-xl bg-[#087F6B]/10 text-[#087F6B] border border-[#087F6B]/20 flex items-center gap-2 font-bold">
            <CheckCircle className="w-4 h-4" /> Organization profile saved successfully.
          </div>
        )}

        <div className="space-y-4">
          <div>
            <label className="block font-semibold text-[#17332F] mb-1">Organization Name</label>
            <input
              type="text"
              value={name}
              onChange={(e) => setName(e.target.value)}
              className="w-full px-3.5 py-2.5 rounded-xl bg-[#FFFDF5] border border-[#D8D8C8] text-[#17332F] font-bold focus:outline-none focus:border-[#034F46]"
            />
          </div>

          <div>
            <label className="block font-semibold text-[#17332F] mb-1">Partner Type</label>
            <select
              value={type}
              onChange={(e) => setType(e.target.value)}
              className="w-full px-3.5 py-2.5 rounded-xl bg-[#FFFDF5] border border-[#D8D8C8] text-[#17332F] font-medium focus:outline-none focus:border-[#034F46]"
            >
              <option value="Industry">Industry</option>
              <option value="Startup">Startup</option>
              <option value="MSME">MSME</option>
              <option value="CSR Organization">CSR Organization</option>
            </select>
          </div>

          <div>
            <label className="block font-semibold text-[#17332F] mb-1">Capabilities & Resources Offered</label>
            <input
              type="text"
              readOnly
              value="Modular FRP Shell Manufacturing, Testing Labs, Environmental Sensors, CSR Grants"
              className="w-full px-3.5 py-2.5 rounded-xl bg-[#F4F1E1] border border-[#D8D8C8] text-[#034F46] font-mono"
            />
          </div>
        </div>

        <div className="pt-4 border-t border-[#D8D8C8] flex justify-end">
          <button
            type="submit"
            className="px-6 py-2.5 rounded-full font-bold bg-[#034F46] text-white hover:bg-[#0F766E] transition shadow-md flex items-center gap-2"
          >
            <Save className="w-4 h-4" /> Save Organization Profile
          </button>
        </div>
      </form>
    </div>
  );
};
