import React from 'react';
import { Link, useNavigate } from 'react-router-dom';
import { useAuth } from '../../services/auth';
import { UserRole } from '../../types';
import { User, Shield, BookOpen, Briefcase, Sparkles, ArrowRight } from 'lucide-react';

export const RoleSelectionPage: React.FC = () => {
  const { login } = useAuth();
  const navigate = useNavigate();

  const roles = [
    {
      role: 'citizen' as UserRole,
      title: 'Citizen / Community',
      icon: <User className="w-8 h-8 text-[#087F6B]" />,
      desc: 'Report problems and track their progress in your community.',
      cta: 'Continue as Citizen',
      border: 'hover:border-[#087F6B]',
      badge: 'bg-[#087F6B]/10 text-[#087F6B] border-[#087F6B]/20',
    },
    {
      role: 'government' as UserRole,
      title: 'Government & Review',
      icon: <Shield className="w-8 h-8 text-[#B7791F]" />,
      desc: 'Validate problems, review AI analysis, check duplicates and coordinate action.',
      cta: 'Continue as Government / Reviewer',
      border: 'hover:border-[#B7791F]',
      badge: 'bg-[#B7791F]/10 text-[#B7791F] border-[#B7791F]/20',
    },
    {
      role: 'university' as UserRole,
      title: 'University / Research',
      icon: <BookOpen className="w-8 h-8 text-[#6A5ACD]" />,
      desc: 'Discover problems that match your research expertise, faculty, and capabilities.',
      cta: 'Continue as University',
      border: 'hover:border-[#6A5ACD]',
      badge: 'bg-[#E9DFFF] text-[#6A5ACD] border-[#6A5ACD]/20',
    },
    {
      role: 'industry' as UserRole,
      title: 'Industry / CSR',
      icon: <Briefcase className="w-8 h-8 text-[#0F766E]" />,
      desc: 'Contribute technology, resources, equipment, testing, and CSR partnerships.',
      cta: 'Continue as Industry / CSR',
      border: 'hover:border-[#0F766E]',
      badge: 'bg-[#0F766E]/10 text-[#0F766E] border-[#0F766E]/20',
    },
  ];

  const handleSelectRole = (r: UserRole) => {
    navigate(`/login/${r}`);
  };

  return (
    <div className="min-h-screen bg-[#F7F5E8] text-[#17332F] flex flex-col justify-between p-6">
      {/* Top Header */}
      <div className="max-w-6xl mx-auto w-full flex items-center justify-between">
        <Link to="/" className="flex items-center gap-2.5">
          <div className="w-9 h-9 rounded-xl bg-[#034F46] flex items-center justify-center text-white shadow-md">
            <Sparkles className="w-5 h-5" />
          </div>
          <span className="text-xl font-extrabold text-[#17332F] tracking-tight">
            Civic<span className="text-transparent bg-clip-text bg-gradient-to-r from-[#034F46] to-[#0F766E]">Fix</span>
          </span>
        </Link>

        <Link to="/" className="text-xs text-[#66736F] hover:text-[#17332F] transition">
          ← Back to Public Site
        </Link>
      </div>

      {/* Main Content */}
      <div className="max-w-5xl mx-auto w-full my-12 text-center">
        <span className="text-xs font-bold text-[#034F46] uppercase tracking-wider">Ecosystem Authentication</span>
        <h1 className="text-3xl sm:text-5xl font-extrabold text-[#17332F] mt-2">
          How are you participating in CivicFix?
        </h1>
        <p className="text-xs sm:text-sm text-[#66736F] mt-3 max-w-xl mx-auto">
          CivicFix provides tailored portal interfaces for citizens, reviewers, government departments, research universities, and industry partners.
        </p>

        {/* 4 Role Selection Cards */}
        <div className="mt-12 grid grid-cols-1 md:grid-cols-2 gap-6 text-left">
          {roles.map((card) => (
            <div
              key={card.role}
              onClick={() => handleSelectRole(card.role)}
              className={`glass-card rounded-2xl p-6 cursor-pointer border transition-all duration-300 ${card.border} group flex flex-col justify-between`}
            >
              <div>
                <div className="flex items-center justify-between mb-4">
                  <div className="p-3 rounded-2xl bg-[#F7F5E8] border border-[#D8D8C8] group-hover:scale-105 transition">
                    {card.icon}
                  </div>
                  <span className={`text-[10px] font-bold px-2.5 py-0.5 rounded-full border ${card.badge}`}>
                    {card.role.toUpperCase()}
                  </span>
                </div>

                <h3 className="text-xl font-bold text-[#17332F] group-hover:text-[#034F46] transition">
                  {card.title}
                </h3>
                <p className="text-xs text-[#66736F] mt-2 leading-relaxed">{card.desc}</p>
              </div>

              <div className="mt-6 pt-4 border-t border-[#D8D8C8] flex items-center justify-between text-xs font-bold text-[#17332F]">
                <span>{card.cta}</span>
                <ArrowRight className="w-4 h-4 text-[#034F46] group-hover:translate-x-1 transition" />
              </div>
            </div>
          ))}
        </div>
      </div>

      {/* Footer copyright */}
      <div className="text-center text-xs text-[#66736F]">
        CivicFix Integrated Platform • AI Assists. Humans Decide.
      </div>
    </div>
  );
};
