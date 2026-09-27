import React from 'react';
import { Link } from 'react-router-dom';
import { Sparkles } from 'lucide-react';

export const Footer: React.FC = () => {
  return (
    <footer className="bg-[#F7F5E8] border-t border-[#D8D8C8] pt-16 pb-12 text-[#66736F]">
      <div className="max-w-7xl mx-auto px-6">
        <div className="grid grid-cols-1 md:grid-cols-5 gap-10 pb-12 border-b border-[#D8D8C8]">
          {/* Brand Info */}
          <div className="md:col-span-2 space-y-4">
            <Link to="/" className="flex items-center gap-2.5">
              <div className="w-8 h-8 rounded-xl bg-gradient-to-tr from-[#034F46] to-[#0F766E] flex items-center justify-center text-white shadow-md">
                <Sparkles className="w-4 h-4" />
              </div>
              <span className="text-xl font-extrabold text-[#17332F] tracking-tight">
                Civic<span className="text-transparent bg-clip-text bg-gradient-to-r from-[#034F46] to-[#6A5ACD]">Fix</span>
              </span>
            </Link>

            <p className="text-xs leading-relaxed max-w-sm text-[#66736F]">
              CivicFix transforms citizen-reported societal problems into structured, actionable workflows involving citizens, human reviewers, government departments, research universities, and industry partners.
            </p>

            <div className="flex items-center gap-3 pt-2">
              <a
                href="https://github.com/ParasNavsar98/CivicFix"
                target="_blank"
                rel="noreferrer"
                className="px-3 py-1.5 rounded-xl bg-[#FFFDF5] border border-[#D8D8C8] hover:border-[#0F766E] text-[#17332F] transition flex items-center gap-2 font-medium"
              >
                <svg className="w-4 h-4 fill-current text-[#17332F]" viewBox="0 0 24 24">
                  <path d="M12 0C5.37 0 0 5.37 0 12c0 5.31 3.435 9.795 8.205 11.385.6.105.825-.255.825-.57 0-.285-.015-1.23-.015-2.235-3.015.555-3.795-.735-4.035-1.41-.135-.345-.72-1.41-1.23-1.695-.42-.225-1.02-.78-.015-.795.945-.015 1.62.87 1.845 1.23 1.08 1.815 2.805 1.305 3.495.99.105-.78.42-1.305.765-1.605-2.67-.3-5.46-1.335-5.46-5.925 0-1.305.465-2.385 1.23-3.225-.12-.3-.54-1.53.12-3.18 0 0 1.005-.315 3.3 1.23.96-.27 1.98-.405 3-.405s2.04.135 3 .405c2.295-1.56 3.3-1.23 3.3-1.23.66 1.65.24 2.88.12 3.18.765.84 1.23 1.905 1.23 3.225 0 4.605-2.805 5.625-5.475 5.925.435.375.81 1.095.81 2.22 0 1.605-.015 2.895-.015 3.3 0 .315.225.69.825.57A12.02 12.02 0 0024 12c0-6.63-5.37-12-12-12z" />
                </svg>
                <span className="text-xs">GitHub Repository</span>
              </a>
              <span className="text-xs text-[#66736F] font-mono">v1.0.0 (civicfix-engine :8000)</span>
            </div>
          </div>

          {/* Quick Portals */}
          <div>
            <h5 className="text-xs font-bold text-[#17332F] uppercase tracking-wider mb-4">Ecosystem Portals</h5>
            <ul className="space-y-2.5 text-xs font-medium">
              <li><Link to="/login/citizen" className="hover:text-[#034F46] transition">Citizen Portal</Link></li>
              <li><Link to="/login/government" className="hover:text-[#034F46] transition">Government & Review Portal</Link></li>
              <li><Link to="/login/university" className="hover:text-[#034F46] transition">University & Research Portal</Link></li>
              <li><Link to="/login/industry" className="hover:text-[#034F46] transition">Industry & CSR Portal</Link></li>
            </ul>
          </div>

          {/* Platform Lifecycle */}
          <div>
            <h5 className="text-xs font-bold text-[#17332F] uppercase tracking-wider mb-4">Lifecycle</h5>
            <ul className="space-y-2.5 text-xs font-medium">
              <li><Link to="/#how-it-works" className="hover:text-[#034F46] transition">1. Capture & Understand</Link></li>
              <li><Link to="/#how-it-works" className="hover:text-[#034F46] transition">2. Validate & Route</Link></li>
              <li><Link to="/#how-it-works" className="hover:text-[#034F46] transition">3. 7-Factor University Match</Link></li>
              <li><Link to="/#how-it-works" className="hover:text-[#034F46] transition">4. Industry Collaboration</Link></li>
            </ul>
          </div>

          {/* Legal & Docs */}
          <div>
            <h5 className="text-xs font-bold text-[#17332F] uppercase tracking-wider mb-4">Resources</h5>
            <ul className="space-y-2.5 text-xs font-medium">
              <li><a href="http://localhost:8000/docs" target="_blank" rel="noreferrer" className="hover:text-[#034F46] transition">FastAPI Swagger Specs</a></li>
              <li><Link to="/login" className="hover:text-[#034F46] transition">Developer QA Console</Link></li>
              <li><a href="#" className="hover:text-[#034F46] transition">Privacy Policy</a></li>
              <li><a href="#" className="hover:text-[#034F46] transition">Terms of Service</a></li>
            </ul>
          </div>
        </div>

        {/* Bottom copyright */}
        <div className="mt-8 flex flex-col sm:flex-row items-center justify-between text-xs gap-4 text-[#66736F]">
          <p>© 2026 CivicFix Platform. Open-source societal innovation orchestration.</p>
          <p className="flex items-center gap-1 font-medium">
            AI Assists. <span className="text-[#034F46] font-bold">Humans Decide.</span>
          </p>
        </div>
      </div>
    </footer>
  );
};
