import React from 'react';
import { useAuth } from '../../services/auth';
import { User, ShieldCheck, Mail, Building } from 'lucide-react';

export const CitizenProfilePage: React.FC = () => {
  const { user } = useAuth();

  return (
    <div className="max-w-2xl mx-auto space-y-6 animate-in fade-in">
      <div>
        <h1 className="text-2xl font-extrabold text-[#17332F]">Citizen Account Profile</h1>
        <p className="text-xs text-[#66736F] mt-1">Manage your citizen identity & notification preferences</p>
      </div>

      <div className="glass-card rounded-3xl p-6 sm:p-8 space-y-6">
        <div className="flex items-center gap-4 pb-6 border-b border-[#D8D8C8]">
          <img
            src={user?.avatarUrl || 'https://images.unsplash.com/photo-1534528741775-53994a69daeb?auto=format&fit=crop&w=150&q=80'}
            alt={user?.name}
            className="w-16 h-16 rounded-full object-cover border-2 border-[#034F46]/50 shadow-md"
          />
          <div>
            <h3 className="text-lg font-bold text-[#17332F]">{user?.name}</h3>
            <p className="text-xs text-[#6A5ACD] font-medium">{user?.email}</p>
            <span className="inline-flex items-center gap-1 text-[10px] text-[#087F6B] mt-1 font-semibold">
              <ShieldCheck className="w-3.5 h-3.5" /> Verified Citizen Account
            </span>
          </div>
        </div>

        <div className="space-y-4 text-xs">
          <div>
            <label className="block font-semibold text-[#17332F] mb-1">Full Name</label>
            <input
              type="text"
              readOnly
              value={user?.name || ''}
              className="w-full px-3.5 py-2.5 rounded-xl bg-[#FFFDF5] border border-[#D8D8C8] text-[#17332F] font-medium"
            />
          </div>

          <div>
            <label className="block font-semibold text-[#17332F] mb-1">Email Address</label>
            <input
              type="text"
              readOnly
              value={user?.email || ''}
              className="w-full px-3.5 py-2.5 rounded-xl bg-[#FFFDF5] border border-[#D8D8C8] text-[#17332F] font-medium"
            />
          </div>

          <div>
            <label className="block font-semibold text-[#17332F] mb-1">Community Group / Organization</label>
            <input
              type="text"
              readOnly
              value={user?.organization || 'Independent Citizen'}
              className="w-full px-3.5 py-2.5 rounded-xl bg-[#FFFDF5] border border-[#D8D8C8] text-[#17332F] font-medium"
            />
          </div>
        </div>
      </div>
    </div>
  );
};
