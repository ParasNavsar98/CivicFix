import React, { useState } from 'react';
import { Link, useNavigate } from 'react-router-dom';
import { useAuth } from '../../services/auth';
import { Shield, ShieldAlert, ArrowRight } from 'lucide-react';

export const GovernmentLoginPage: React.FC = () => {
  const { login } = useAuth();
  const navigate = useNavigate();

  const [email, setEmail] = useState('priya.verma@gov.in');
  const [password, setPassword] = useState('password123');
  const [department, setDepartment] = useState('Urban Development & Public Works');
  const [role, setRole] = useState('Reviewer / Officer');

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    login('government', { email, organization: department, subRole: role });
    navigate('/government/dashboard');
  };

  const handleDemoLogin = () => {
    login('government');
    navigate('/government/dashboard');
  };

  return (
    <div className="min-h-screen bg-[#F7F5E8] text-[#17332F] flex items-center justify-center p-6">
      <div className="max-w-xl w-full glass-card rounded-3xl p-8 sm:p-10 border border-[#B7791F]/30 shadow-xl bg-[#FFFDF5]">
        <Link to="/login" className="text-xs text-[#66736F] hover:text-[#17332F] transition">
          ← Change Role
        </Link>

        <div className="mt-6 flex items-center gap-3">
          <div className="p-3 rounded-2xl bg-[#B7791F]/10 text-[#B7791F] border border-[#B7791F]/20">
            <Shield className="w-6 h-6" />
          </div>
          <div>
            <h2 className="text-2xl font-extrabold text-[#17332F]">Government & Review Portal</h2>
            <p className="text-xs text-[#66736F]">Validate problems, review AI findings & coordinate action</p>
          </div>
        </div>

        {/* Security Alert Banner */}
        <div className="mt-4 p-3 rounded-xl bg-[#B7791F]/10 border border-[#B7791F]/20 text-xs text-[#B7791F] flex items-center gap-2">
          <ShieldAlert className="w-4 h-4 shrink-0" />
          <span>Authorized Personnel Only. Actions logged for audit compliance.</span>
        </div>

        {/* Development Demo Login */}
        <div className="mt-4 p-3 rounded-xl bg-[#E9DFFF] border border-[#6A5ACD]/20 text-xs text-[#6A5ACD] flex items-center justify-between">
          <span>Development Demo Login</span>
          <button
            onClick={handleDemoLogin}
            className="px-2.5 py-1 rounded-lg bg-[#6A5ACD] text-white font-bold text-[11px] hover:bg-[#6A5ACD]/80 transition cursor-pointer"
          >
            Instant Officer Access →
          </button>
        </div>

        <form onSubmit={handleSubmit} className="mt-6 space-y-4">
          <div>
            <label className="block text-xs font-semibold text-[#17332F] mb-1">Official Email</label>
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
              <label className="block text-xs font-semibold text-[#17332F] mb-1">Department</label>
              <select
                value={department}
                onChange={(e) => setDepartment(e.target.value)}
                className="w-full px-3.5 py-2.5 rounded-xl bg-[#FFFDF5] border border-[#D8D8C8] text-xs text-[#17332F] focus:outline-none focus:border-[#034F46] transition"
              >
                <option value="Urban Development & Public Works">Urban Development & PWD</option>
                <option value="Water Supply & Sanitation">Water & Sanitation Dept</option>
                <option value="Environmental Protection Agency">Environment Dept</option>
                <option value="Health & Family Welfare">Health Department</option>
              </select>
            </div>

            <div>
              <label className="block text-xs font-semibold text-[#17332F] mb-1">Assigned Role</label>
              <select
                value={role}
                onChange={(e) => setRole(e.target.value)}
                className="w-full px-3.5 py-2.5 rounded-xl bg-[#FFFDF5] border border-[#D8D8C8] text-xs text-[#17332F] focus:outline-none focus:border-[#034F46] transition"
              >
                <option value="Reviewer / Officer">Reviewer / Officer</option>
                <option value="Department Admin">Department Admin</option>
              </select>
            </div>
          </div>

          <button
            type="submit"
            className="w-full py-3 rounded-xl text-xs font-bold bg-[#034F46] text-white hover:bg-[#0F766E] transition shadow-md flex items-center justify-center gap-2 mt-2 cursor-pointer"
          >
            Access Government Portal <ArrowRight className="w-4 h-4" />
          </button>
        </form>
      </div>
    </div>
  );
};
