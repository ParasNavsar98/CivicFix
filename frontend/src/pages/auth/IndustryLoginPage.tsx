import React, { useState } from 'react';
import { Link, useNavigate } from 'react-router-dom';
import { useAuth } from '../../services/auth';
import { Briefcase, ArrowRight } from 'lucide-react';

export const IndustryLoginPage: React.FC = () => {
  const { login } = useAuth();
  const navigate = useNavigate();

  const [email, setEmail] = useState('vikram.mehta@cleantech.com');
  const [password, setPassword] = useState('password123');
  const [organization, setOrganization] = useState('CleanTech Innovations Pvt Ltd');
  const [partnerType, setPartnerType] = useState('Industry');

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    login('industry', { email, organization, subRole: partnerType });
    navigate('/industry/dashboard');
  };

  const handleDemoLogin = () => {
    login('industry');
    navigate('/industry/dashboard');
  };

  return (
    <div className="min-h-screen bg-[#F7F5E8] text-[#17332F] flex items-center justify-center p-6">
      <div className="max-w-xl w-full glass-card rounded-3xl p-8 sm:p-10 border border-[#0F766E]/30 shadow-xl bg-[#FFFDF5]">
        <Link to="/login" className="text-xs text-[#66736F] hover:text-[#17332F] transition">
          ← Change Role
        </Link>

        <div className="mt-6 flex items-center gap-3">
          <div className="p-3 rounded-2xl bg-[#0F766E]/10 text-[#0F766E] border border-[#0F766E]/20">
            <Briefcase className="w-6 h-6" />
          </div>
          <div>
            <h2 className="text-2xl font-extrabold text-[#17332F]">Industry & CSR Portal</h2>
            <p className="text-xs text-[#66736F]">Contribute technology, resources, testing & partnerships</p>
          </div>
        </div>

        {/* Development Demo Login */}
        <div className="mt-4 p-3 rounded-xl bg-[#E9DFFF] border border-[#6A5ACD]/20 text-xs text-[#6A5ACD] flex items-center justify-between">
          <span>Development Demo Login</span>
          <button
            onClick={handleDemoLogin}
            className="px-2.5 py-1 rounded-lg bg-[#6A5ACD] text-white font-bold text-[11px] hover:bg-[#6A5ACD]/80 transition cursor-pointer"
          >
            Instant Partner Access →
          </button>
        </div>

        <form onSubmit={handleSubmit} className="mt-6 space-y-4">
          <div>
            <label className="block text-xs font-semibold text-[#17332F] mb-1">Organization Email</label>
            <input
              type="email"
              required
              value={email}
              onChange={(e) => setEmail(e.target.value)}
              className="w-full px-3.5 py-2.5 rounded-xl bg-[#FFFDF5] border border-[#D8D8C8] text-xs text-[#17332F] focus:outline-none focus:border-[#034F46] transition"
            />
          </div>

          <div>
            <label className="block text-xs font-semibold text-[#17332F] mb-1">Password</label>
            <input
              type="password"
              required
              value={password}
              onChange={(e) => setPassword(e.target.value)}
              className="w-full px-3.5 py-2.5 rounded-xl bg-[#FFFDF5] border border-[#D8D8C8] text-xs text-[#17332F] focus:outline-none focus:border-[#034F46] transition"
            />
          </div>

          <div className="grid grid-cols-1 sm:grid-cols-2 gap-4">
            <div>
              <label className="block text-xs font-semibold text-[#17332F] mb-1">Organization Name</label>
              <input
                type="text"
                required
                value={organization}
                onChange={(e) => setOrganization(e.target.value)}
                className="w-full px-3.5 py-2.5 rounded-xl bg-[#FFFDF5] border border-[#D8D8C8] text-xs text-[#17332F] focus:outline-none focus:border-[#034F46] transition"
              />
            </div>

            <div>
              <label className="block text-xs font-semibold text-[#17332F] mb-1">Partner Type</label>
              <select
                value={partnerType}
                onChange={(e) => setPartnerType(e.target.value)}
                className="w-full px-3.5 py-2.5 rounded-xl bg-[#FFFDF5] border border-[#D8D8C8] text-xs text-[#17332F] focus:outline-none focus:border-[#034F46] transition"
              >
                <option value="Industry">Industry</option>
                <option value="Startup">Startup</option>
                <option value="MSME">MSME</option>
                <option value="CSR Organization">CSR Organization</option>
              </select>
            </div>
          </div>

          <button
            type="submit"
            className="w-full py-3 rounded-xl text-xs font-bold bg-[#034F46] text-white hover:bg-[#0F766E] transition shadow-md flex items-center justify-center gap-2 mt-2 cursor-pointer"
          >
            Access Industry Portal <ArrowRight className="w-4 h-4" />
          </button>
        </form>
      </div>
    </div>
  );
};
