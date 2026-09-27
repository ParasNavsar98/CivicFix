import React, { useState } from 'react';
import { Link, useNavigate } from 'react-router-dom';
import { useAuth } from '../../services/auth';
import { BookOpen, ArrowRight } from 'lucide-react';

export const UniversityLoginPage: React.FC = () => {
  const { login } = useAuth();
  const navigate = useNavigate();

  const [email, setEmail] = useState('r.sharma@bitmesra.ac.in');
  const [password, setPassword] = useState('password123');
  const [university, setUniversity] = useState('Birla Institute of Technology (BIT Mesra)');
  const [role, setRole] = useState('University SPOC');

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    login('university', { email, organization: university, subRole: role });
    navigate('/university/dashboard');
  };

  const handleDemoLogin = () => {
    login('university');
    navigate('/university/dashboard');
  };

  return (
    <div className="min-h-screen bg-[#F7F5E8] text-[#17332F] flex items-center justify-center p-6">
      <div className="max-w-xl w-full glass-card rounded-3xl p-8 sm:p-10 border border-[#6A5ACD]/30 shadow-xl bg-[#FFFDF5]">
        <Link to="/login" className="text-xs text-[#66736F] hover:text-[#17332F] transition">
          ← Change Role
        </Link>

        <div className="mt-6 flex items-center gap-3">
          <div className="p-3 rounded-2xl bg-[#E9DFFF] text-[#6A5ACD] border border-[#6A5ACD]/20">
            <BookOpen className="w-6 h-6" />
          </div>
          <div>
            <h2 className="text-2xl font-extrabold text-[#17332F]">University & Research Portal</h2>
            <p className="text-xs text-[#66736F]">Discover matched problems & deploy research solutions</p>
          </div>
        </div>

        {/* Development Demo Login */}
        <div className="mt-4 p-3 rounded-xl bg-[#E9DFFF] border border-[#6A5ACD]/20 text-xs text-[#6A5ACD] flex items-center justify-between">
          <span>Development Demo Login</span>
          <button
            onClick={handleDemoLogin}
            className="px-2.5 py-1 rounded-lg bg-[#6A5ACD] text-white font-bold text-[11px] hover:bg-[#6A5ACD]/80 transition cursor-pointer"
          >
            Instant SPOC Access →
          </button>
        </div>

        <form onSubmit={handleSubmit} className="mt-6 space-y-4">
          <div>
            <label className="block text-xs font-semibold text-[#17332F] mb-1">Institution Email</label>
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
              <label className="block text-xs font-semibold text-[#17332F] mb-1">University</label>
              <select
                value={university}
                onChange={(e) => setUniversity(e.target.value)}
                className="w-full px-3.5 py-2.5 rounded-xl bg-[#FFFDF5] border border-[#D8D8C8] text-xs text-[#17332F] focus:outline-none focus:border-[#034F46] transition"
              >
                <option value="Birla Institute of Technology (BIT Mesra)">BIT Mesra</option>
                <option value="National Institute of Technology Jamshedpur">NIT Jamshedpur</option>
                <option value="IIT (ISM) Dhanbad">IIT (ISM) Dhanbad</option>
              </select>
            </div>

            <div>
              <label className="block text-xs font-semibold text-[#17332F] mb-1">Role</label>
              <select
                value={role}
                onChange={(e) => setRole(e.target.value)}
                className="w-full px-3.5 py-2.5 rounded-xl bg-[#FFFDF5] border border-[#D8D8C8] text-xs text-[#17332F] focus:outline-none focus:border-[#034F46] transition"
              >
                <option value="University SPOC">University SPOC</option>
                <option value="Faculty Mentor">Faculty Mentor</option>
                <option value="Student / Researcher">Student / Researcher</option>
              </select>
            </div>
          </div>

          <button
            type="submit"
            className="w-full py-3 rounded-xl text-xs font-bold bg-[#034F46] text-white hover:bg-[#0F766E] transition shadow-md flex items-center justify-center gap-2 mt-2 cursor-pointer"
          >
            Access University Portal <ArrowRight className="w-4 h-4" />
          </button>
        </form>
      </div>
    </div>
  );
};
