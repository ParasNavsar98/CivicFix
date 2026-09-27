import React, { useEffect, useState } from 'react';
import { api } from '../../services/api';
import { IndustryInterest } from '../../types';
import { HeartHandshake, Clock, CheckCircle2 } from 'lucide-react';

export const MyInterestsPage: React.FC = () => {
  const [interests, setInterests] = useState<IndustryInterest[]>([]);

  useEffect(() => {
    // Load initial mock or api interests
    api.getSolutions().then(() => {
      setInterests([
        {
          interestId: 'INT-CLEANTECH-01',
          solutionId: 'SOL-SANIT-01',
          partnerId: 'IND-CLEANTECH-99',
          partnerName: 'CleanTech Innovations Pvt Ltd',
          supportOffered: ['Hardware', 'Testing'],
          contribution: { hardware: ['4 FRP modular shells'] },
          message: 'We are eager to co-deploy our FRP modular shells with BIT Mesra design for Namkum school.',
          status: 'PENDING',
          createdAt: '2026-09-25T15:30:00Z',
        },
      ]);
    });
  }, []);

  return (
    <div className="space-y-6 animate-in fade-in">
      <div>
        <h1 className="text-2xl font-extrabold text-[#17332F]">My Expressed Interests</h1>
        <p className="text-xs text-[#66736F] mt-1">Track partner support proposals submitted to university solution leads.</p>
      </div>

      <div className="bg-[#FFFDF5] rounded-3xl overflow-hidden border border-[#D8D8C8] shadow-sm">
        <div className="overflow-x-auto">
          <table className="w-full text-left text-xs">
            <thead className="bg-[#F4F1E1] border-b border-[#D8D8C8] text-[#66736F] uppercase text-[10px] font-bold">
              <tr>
                <th className="p-4">Interest ID</th>
                <th className="p-4">Solution & University</th>
                <th className="p-4">Support Offered</th>
                <th className="p-4">Submitted Date</th>
                <th className="p-4">Status</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-[#D8D8C8]">
              {interests.map((item) => (
                <tr key={item.interestId} className="hover:bg-[#F7F5E8]">
                  <td className="p-4 font-mono font-bold text-[#0F766E]">{item.interestId}</td>
                  <td className="p-4">
                    <span className="font-bold text-[#17332F] block">Eco-Friendly Biogas School Toilet</span>
                    <span className="text-[10px] text-[#66736F]">BIT Mesra</span>
                  </td>
                  <td className="p-4">
                    <div className="flex flex-wrap gap-1">
                      {item.supportOffered.map((s) => (
                        <span key={s} className="px-2 py-0.5 rounded bg-[#6A5ACD]/10 text-[#6A5ACD] border border-[#6A5ACD]/20">
                          {s}
                        </span>
                      ))}
                    </div>
                  </td>
                  <td className="p-4 text-[#66736F]">{new Date(item.createdAt).toLocaleDateString()}</td>
                  <td className="p-4">
                    <span className="px-2.5 py-1 rounded-full bg-[#B7791F]/10 text-[#B7791F] font-bold border border-[#B7791F]/20">
                      {item.status}
                    </span>
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      </div>
    </div>
  );
};
