import React, { useState } from 'react';
import { Link, useNavigate } from 'react-router-dom';
import { useAuth } from '../../services/auth';
import { User, Sparkles, ArrowRight, ShieldCheck } from 'lucide-react';

export const CitizenLoginPage: React.FC = () => {
  const { login } = useAuth();
  const navigate = useNavigate();

  const [email, setEmail] = useState('ramesh.kumar@gmail.com');
  const [password, setPassword] = useState('password123');

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    login('citizen', { email });
    navigate('/citizen/dashboard');
  };

  const handleDemoLogin = () => {
    login('citizen');
    navigate('/citizen/dashboard');
  };

  return (
    <div className="min-h-screen bg-[#F7F5E8] text-[#17332F] flex items-center justify-center p-6">
      <div className="max-w-4xl w-full glass-card rounded-3xl overflow-hidden grid grid-cols-1 md:grid-cols-2 border border-[#087F6B]/30 shadow-xl">
        {/* Left Side Panel */}
        <div className="p-8 sm:p-10 bg-[#FFFDF5] flex flex-col justify-between border-b md:border-b-0 md:border-r border-[#D8D8C8]">
          <div>
            <Link to="/login" className="text-xs text-[#66736F] hover:text-[#17332F] transition">
              ← Change Role
            </Link>

            <div className="mt-8 flex items-center gap-2">
              <div className="w-8 h-8 rounded-xl bg-[#087F6B]/10 text-[#087F6B] border border-[#087F6B]/20 flex items-center justify-center">
                <User className="w-4 h-4" />
              </div>
              <span className="text-xs font-bold text-[#087F6B] uppercase tracking-wider">Citizen Portal</span>
            </div>

            <h2 className="text-3xl font-extrabold text-[#17332F] mt-4">
              Your community. <br />
              <span className="font-serif-italic font-normal text-[#087F6B]">Your voice.</span>
            </h2>

            <p className="text-xs text-[#66736F] mt-3 leading-relaxed">
              Report societal problems in your neighborhood and track their progress through transparent AI understanding, human review, and university resolution.
            </p>
          </div>

          <div className="mt-8 p-3.5 rounded-xl bg-[#F7F5E8] border border-[#D8D8C8] text-xs text-[#66736F]">
            <span className="text-[#087F6B] font-semibold block mb-0.5">Community Transparency</span>
            Private citizen details are masked on public GIS maps and audit logs.
          </div>
        </div>

        {/* Right Form */}
        <div className="p-8 sm:p-10 flex flex-col justify-center bg-[#FFFDF5]">
          <h3 className="text-xl font-bold text-[#17332F]">Welcome Back</h3>
          <p className="text-xs text-[#66736F] mt-1">Track the problems you've reported</p>

          {/* Demo Login Banner */}
          <div className="mt-4 p-3 rounded-xl bg-[#E9DFFF] border border-[#6A5ACD]/20 text-xs text-[#6A5ACD] flex items-center justify-between">
            <span>Development Demo Login</span>
            <button
              onClick={handleDemoLogin}
              className="px-2.5 py-1 rounded-lg bg-[#6A5ACD] text-white font-bold text-[11px] hover:bg-[#6A5ACD]/80 transition cursor-pointer"
            >
              Instant Access →
            </button>
          </div>

          <form onSubmit={handleSubmit} className="mt-6 space-y-4">
            <div>
              <label className="block text-xs font-semibold text-[#17332F] mb-1">Email Address</label>
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

            <div className="flex items-center justify-between text-xs text-[#66736F] pt-1">
              <label className="flex items-center gap-2 cursor-pointer">
                <input type="checkbox" defaultChecked className="rounded border-[#D8D8C8] text-[#034F46] focus:ring-0" />
                Remember me
              </label>
              <a href="#" className="hover:text-[#17332F] transition">Forgot Password?</a>
            </div>

            <button
              type="submit"
              className="w-full py-3 rounded-xl text-xs font-bold bg-[#034F46] text-white hover:bg-[#0F766E] transition shadow-md flex items-center justify-center gap-2 cursor-pointer"
            >
              Sign In as Citizen <ArrowRight className="w-4 h-4" />
            </button>
          </form>

          <div className="mt-6 text-center text-xs text-[#66736F]">
            Don't have an account?{' '}
            <button onClick={handleDemoLogin} className="text-[#087F6B] font-semibold hover:underline cursor-pointer">
              Create Citizen Account
            </button>
          </div>
        </div>
      </div>
    </div>
  );
};
