import React, { useEffect, useState } from 'react';
import { api } from '../../services/api';
import { CollaborationItem } from '../../types';
import { Handshake, CheckCircle2 } from 'lucide-react';

export const CollaborationsPage: React.FC = () => {
  const [collabs, setCollabs] = useState<CollaborationItem[]>([]);

  useEffect(() => {
    api.getCollaborations().then(setCollabs);
  }, []);

  return (
    <div className="space-y-6 animate-in fade-in">
      <div>
        <h1 className="text-2xl font-extrabold text-[#17332F]">Active Industry Collaborations</h1>
        <p className="text-xs text-[#66736F] mt-1">Active partnerships co-deploying technology, testing, and CSR funding with research universities.</p>
      </div>

      <div className="space-y-4">
        {collabs.map((col) => (
          <div key={col.collaborationId} className="bg-[#FFFDF5] rounded-3xl p-6 border border-[#D8D8C8] shadow-sm space-y-4">
            <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-3 pb-3 border-b border-[#D8D8C8]">
              <div>
                <span className="text-[10px] font-mono font-bold text-[#087F6B]">{col.collaborationId}</span>
                <h3 className="text-base font-bold text-[#17332F] mt-0.5">Nanocomposite Bio-Filtration Water Purification Unit</h3>
                <p className="text-xs text-[#66736F]">University: IIT (ISM) Dhanbad • Partner: Tata Trust CSR</p>
              </div>

              <span className="text-xs px-3 py-1 rounded-full bg-[#087F6B]/10 text-[#087F6B] font-bold border border-[#087F6B]/20 self-start sm:self-auto flex items-center gap-1">
                <CheckCircle2 className="w-3.5 h-3.5" /> {col.status}
              </span>
            </div>

            <div className="bg-[#F4F1E1] p-3.5 rounded-xl border border-[#D8D8C8] text-xs space-y-1">
              <span className="text-[10px] text-[#66736F] uppercase font-semibold block">Active Support Commitment</span>
              <p className="text-[#17332F] font-medium">Grant funding of ₹5,00,000 for 3 village water pond deployment sites.</p>
            </div>
          </div>
        ))}
      </div>
    </div>
  );
};
