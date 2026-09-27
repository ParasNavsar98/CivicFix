import React from 'react';
import { Link } from 'react-router-dom';
import {
  Sparkles,
  ArrowRight,
  ShieldCheck,
  CheckCircle2,
  BookOpen,
  Building2,
  Users,
  Briefcase,
  Search,
  ChevronRight,
  Layers,
  MapPin,
  Cpu,
  Target,
  FileCheck2,
  ShieldAlert,
  PlusCircle,
  Compass,
  Award,
} from 'lucide-react';
import { Footer } from '../../components/common/Footer';

export const LandingPage: React.FC = () => {
  return (
    <div className="min-h-screen bg-[#F7F5E8] text-[#17332F] font-sans overflow-x-hidden">
      {/* Landing Floating Top Bar */}
      <header className="sticky top-4 z-50 max-w-6xl mx-auto px-4">
        <nav className="glass-panel rounded-full px-6 py-3 flex items-center justify-between shadow-lg">
          <Link to="/" className="flex items-center gap-2.5 group">
            <div className="w-8 h-8 rounded-xl bg-[#034F46] flex items-center justify-center text-white shadow-md">
              <Sparkles className="w-4 h-4" />
            </div>
            <span className="text-lg font-extrabold text-[#17332F] tracking-tight">
              Civic<span className="text-transparent bg-clip-text bg-gradient-to-r from-[#034F46] to-[#0F766E]">Fix</span>
            </span>
          </Link>

          <div className="hidden md:flex items-center gap-6 text-xs font-medium text-[#66736F]">
            <a href="#how-it-works" className="hover:text-[#17332F] transition">How It Works</a>
            <a href="#features" className="hover:text-[#17332F] transition">Integrated AI</a>
            <a href="#transparency" className="hover:text-[#17332F] transition">Human Boundary</a>
            <a href="#ecosystem" className="hover:text-[#17332F] transition">Ecosystem Roles</a>
          </div>

          <div className="flex items-center gap-3">
            <Link
              to="/login"
              className="px-4 py-2 rounded-full text-xs font-semibold bg-[#034F46] text-white hover:bg-[#0F766E] transition shadow-md"
            >
              Access Portals
            </Link>
          </div>
        </nav>
      </header>

      {/* Hero Section */}
      <section className="relative pt-24 pb-20 max-w-6xl mx-auto px-6 text-center">
        <div className="inline-flex items-center gap-2 px-3.5 py-1.5 rounded-full bg-[#E9DFFF] border border-[#6A5ACD]/20 text-[#6A5ACD] text-xs font-medium mb-6 animate-in fade-in">
          <Sparkles className="w-3.5 h-3.5 text-[#6A5ACD] animate-pulse" />
          <span>Unified Civic Engine • Gemma 3 4B & 7-Factor University Matcher</span>
        </div>

        <h1 className="text-4xl sm:text-6xl lg:text-7xl font-extrabold tracking-tight text-[#17332F] max-w-4xl mx-auto leading-[1.08]">
          From Societal Problems to <br className="hidden sm:inline" />
          <span className="font-serif-italic font-normal text-transparent bg-clip-text bg-gradient-to-r from-[#034F46] via-[#0F766E] to-[#6A5ACD]">
            Real Solutions.
          </span>
        </h1>

        <p className="mt-6 text-base sm:text-xl text-[#66736F] max-w-2xl mx-auto font-normal leading-relaxed">
          CivicFix connects citizens, reviewers, government, universities and industry to transform real-world problems into measurable, coordinated solutions.
        </p>

        {/* Hero CTAs */}
        <div className="mt-10 flex flex-wrap items-center justify-center gap-4">
          <Link
            to="/citizen/report"
            className="px-6 py-3.5 rounded-full text-sm font-bold bg-[#034F46] hover:bg-[#0F766E] text-white shadow-md transition flex items-center gap-2"
          >
            Report a Problem <ArrowRight className="w-4 h-4" />
          </Link>
          <a
            href="#how-it-works"
            className="px-6 py-3.5 rounded-full text-sm font-semibold bg-[#FFFDF5] hover:bg-[#F7F5E8] text-[#17332F] border border-[#D8D8C8] transition shadow-xs"
          >
            Explore CivicFix
          </a>
          <a
            href="#how-it-works"
            className="px-6 py-3.5 rounded-full text-sm font-semibold text-[#6A5ACD] hover:text-[#034F46] transition"
          >
            How It Works →
          </a>
        </div>

        {/* Hero Visual Diagram: 8-Stage Lifecycle */}
        <div className="mt-16 glass-card rounded-3xl p-6 sm:p-8 max-w-5xl mx-auto relative overflow-hidden text-left">
          <div className="text-xs font-bold uppercase tracking-wider text-[#034F46] mb-4 flex items-center gap-2">
            <Cpu className="w-4 h-4 text-[#0F766E]" /> Orchestrated Societal Problem Lifecycle
          </div>

          <div className="grid grid-cols-2 sm:grid-cols-4 lg:grid-cols-8 gap-3">
            {[
              { step: '1', title: 'Citizen', sub: 'Report Issue' },
              { step: '2', title: 'AI Understand', sub: 'Gemma 3 4B' },
              { step: '3', title: 'Human Review', sub: 'Validation' },
              { step: '4', title: 'Govt Route', sub: 'Department Case' },
              { step: '5', title: 'Uni Match', sub: '7-Factor Score' },
              { step: '6', title: 'Industry CSR', sub: 'Resources' },
              { step: '7', title: 'Implement', sub: 'Field Project' },
              { step: '8', title: 'Impact', sub: 'Resolution' },
            ].map((s) => (
              <div key={s.step} className="bg-[#FFFDF5] p-3 rounded-2xl border border-[#D8D8C8] text-center flex flex-col items-center">
                <span className="w-6 h-6 rounded-full bg-[#E9DFFF] text-[#6A5ACD] text-xs font-bold flex items-center justify-center mb-2">
                  {s.step}
                </span>
                <span className="text-xs font-bold text-[#17332F] block">{s.title}</span>
                <span className="text-[10px] text-[#66736F] mt-0.5">{s.sub}</span>
              </div>
            ))}
          </div>
        </div>
      </section>

      {/* Problem → Solution 8 Cards Section */}
      <section id="how-it-works" className="py-20 max-w-6xl mx-auto px-6">
        <div className="text-center max-w-3xl mx-auto">
          <h2 className="text-3xl sm:text-4xl font-extrabold text-[#17332F]">
            One Problem. Many Experts. <br />
            <span className="font-serif-italic font-normal text-transparent bg-clip-text bg-gradient-to-r from-[#034F46] to-[#6A5ACD]">
              One Coordinated Solution.
            </span>
          </h2>
          <p className="mt-4 text-base text-[#66736F]">
            CivicFix structures raw citizen concerns into standardized multi-stakeholder resolution tracks.
          </p>
        </div>

        <div className="mt-14 grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-6">
          {[
            {
              step: '01',
              title: 'Capture',
              icon: <PlusCircle className="w-5 h-5 text-[#6A5ACD]" />,
              desc: 'Citizens submit real-world problems with descriptions, geographic location, and media evidence.',
            },
            {
              step: '02',
              title: 'Understand',
              icon: <Sparkles className="w-5 h-5 text-[#0F766E]" />,
              desc: 'Gemma 3 4B analyzes text to produce structured taxonomy domain, subcategory, severity, and required skills.',
            },
            {
              step: '03',
              title: 'Validate',
              icon: <ShieldCheck className="w-5 h-5 text-[#087F6B]" />,
              desc: 'Human reviewers verify AI findings, evaluate BGE-small duplicate candidates, and confirm category rules.',
            },
            {
              step: '04',
              title: 'Route',
              icon: <Compass className="w-5 h-5 text-[#B7791F]" />,
              desc: 'Cases are dispatched to authorized government departments or flagged for university research routing.',
            },
            {
              step: '05',
              title: 'Match',
              icon: <Award className="w-5 h-5 text-[#6A5ACD]" />,
              desc: '7-factor weighted scoring algorithm evaluates university expertise, faculty, capacity, and infrastructure.',
            },
            {
              step: '06',
              title: 'Collaborate',
              icon: <Briefcase className="w-5 h-5 text-[#B83A3A]" />,
              desc: 'Industry, startups, and CSR partners contribute equipment, funding, testing labs, and technology.',
            },
            {
              step: '07',
              title: 'Implement',
              icon: <Target className="w-5 h-5 text-[#0F766E]" />,
              desc: 'University research teams execute field deployments and prototype solutions under mentor guidance.',
            },
            {
              step: '08',
              title: 'Measure',
              icon: <CheckCircle2 className="w-5 h-5 text-[#087F6B]" />,
              desc: 'Verifiable impact metrics and audit trails confirm long-term societal problem resolution.',
            },
          ].map((card) => (
            <div key={card.step} className="glass-card rounded-2xl p-6 relative group hover:-translate-y-1 transition duration-300">
              <div className="flex items-center justify-between mb-4">
                <div className="p-2.5 rounded-xl bg-[#F7F5E8] border border-[#D8D8C8] group-hover:scale-110 transition">
                  {card.icon}
                </div>
                <span className="text-xs font-mono font-bold text-[#66736F]">{card.step}</span>
              </div>
              <h3 className="text-lg font-bold text-[#17332F] mb-2">{card.title}</h3>
              <p className="text-xs text-[#66736F] leading-relaxed">{card.desc}</p>
            </div>
          ))}
        </div>
      </section>

      {/* Why CivicFix Integrated Features */}
      <section id="features" className="py-20 max-w-6xl mx-auto px-6 border-t border-[#D8D8C8]">
        <div className="text-center max-w-2xl mx-auto">
          <span className="text-xs font-bold text-[#034F46] uppercase tracking-wider">Engine Intelligence</span>
          <h2 className="text-3xl font-extrabold text-[#17332F] mt-2">Integrated AI & Matching Capabilities</h2>
        </div>

        <div className="mt-12 grid grid-cols-1 md:grid-cols-2 gap-6">
          <div className="glass-card rounded-2xl p-6 border-l-4 border-l-[#6A5ACD]">
            <div className="flex items-center gap-3 mb-3">
              <Sparkles className="w-5 h-5 text-[#6A5ACD]" />
              <h3 className="text-lg font-bold text-[#17332F]">AI-Assisted Understanding</h3>
            </div>
            <p className="text-xs text-[#66736F] leading-relaxed">
              Gemma 3 4B via Ollama analyzes submitted problem text to produce structured taxonomy classifications (12 controlled domains), severity ratings, urgency, required expertise, and research requirement flags.
            </p>
          </div>

          <div className="glass-card rounded-2xl p-6 border-l-4 border-l-[#0F766E]">
            <div className="flex items-center gap-3 mb-3">
              <Layers className="w-5 h-5 text-[#0F766E]" />
              <h3 className="text-lg font-bold text-[#17332F]">Duplicate Detection (`duplicate-v2`)</h3>
            </div>
            <p className="text-xs text-[#66736F] leading-relaxed">
              `BAAI/bge-small-en-v1.5` 384-dimensional dense sentence embeddings, cosine similarity, Haversine location proximity, and fingerprint contradiction protection evaluate candidate duplicates using available-signal normalized composite scoring.
            </p>
          </div>

          <div className="glass-card rounded-2xl p-6 border-l-4 border-l-[#034F46]">
            <div className="flex items-center gap-3 mb-3">
              <Award className="w-5 h-5 text-[#034F46]" />
              <h3 className="text-lg font-bold text-[#17332F]">7-Factor University Matching</h3>
            </div>
            <p className="text-xs text-[#66736F] leading-relaxed">
              Evaluates university capabilities against problem needs across 7 weighted factors: Expertise (35%), Faculty (20%), Infrastructure (15%), Past Projects (10%), Geography (10%), Capacity (5%), and Industry (5%).
            </p>
          </div>

          <div className="glass-card rounded-2xl p-6 border-l-4 border-l-[#087F6B]">
            <div className="flex items-center gap-3 mb-3">
              <Briefcase className="w-5 h-5 text-[#087F6B]" />
              <h3 className="text-lg font-bold text-[#17332F]">Industry & CSR Collaboration</h3>
            </div>
            <p className="text-xs text-[#66736F] leading-relaxed">
              Allows industry, MSME, startup, and CSR partners to discover published university solutions and contribute hardware, testing labs, mentorship, funding, and deployment partnerships.
            </p>
          </div>
        </div>
      </section>

      {/* Transparency & Human Decision Boundary */}
      <section id="transparency" className="py-20 max-w-5xl mx-auto px-6">
        <div className="glass-card rounded-3xl p-8 border border-[#B7791F]/30 bg-[#FFFDF5] text-center shadow-md">
          <span className="inline-flex items-center gap-2 px-3 py-1 rounded-full bg-[#B7791F]/10 text-[#B7791F] text-xs font-bold border border-[#B7791F]/20 mb-4">
            <ShieldCheck className="w-4 h-4" /> Core Architectural Principle
          </span>

          <h2 className="text-3xl font-extrabold text-[#17332F]">
            "AI Assists. <span className="font-serif-italic font-normal text-[#B7791F]">Humans Decide."</span>
          </h2>

          <div className="mt-8 flex flex-col md:flex-row items-center justify-center gap-4 text-xs font-semibold">
            <div className="bg-[#F7F5E8] px-4 py-3 rounded-xl border border-[#D8D8C8] text-[#6A5ACD]">
              1. AI Analysis & Signals
            </div>
            <ArrowRight className="w-4 h-4 text-[#66736F] hidden md:block" />
            <div className="bg-[#F7F5E8] px-4 py-3 rounded-xl border border-[#B7791F]/30 text-[#B7791F] font-bold">
              2. Human Reviewer Check
            </div>
            <ArrowRight className="w-4 h-4 text-[#66736F] hidden md:block" />
            <div className="bg-[#F7F5E8] px-4 py-3 rounded-xl border border-[#087F6B]/30 text-[#087F6B]">
              3. Authorized Validated Action
            </div>
          </div>

          <p className="mt-6 text-xs text-[#66736F] max-w-2xl mx-auto leading-relaxed">
            AI does not independently make consequential decisions. Human reviewers and authorized officers remain responsible for category corrections, duplicate merges, government routing, university assignment acceptance, and collaboration approvals.
          </p>
        </div>
      </section>

      {/* Ecosystem Role Sections */}
      <section id="ecosystem" className="py-20 max-w-6xl mx-auto px-6 border-t border-[#D8D8C8] space-y-16">
        {/* For Citizens */}
        <div className="grid grid-cols-1 lg:grid-cols-2 gap-10 items-center">
          <div>
            <span className="text-xs font-bold text-[#087F6B] uppercase tracking-wider">Role 1: Citizens</span>
            <h3 className="text-2xl sm:text-3xl font-bold text-[#17332F] mt-2">Have you identified a problem in your community?</h3>
            <p className="text-xs text-[#66736F] mt-3 leading-relaxed">
              Report issues directly to the platform with photos and location. Track real-time progress as AI understands it, reviewers validate it, and universities/government resolve it.
            </p>

            <div className="mt-4 flex flex-wrap gap-2">
              {['Sanitation', 'Water Resources', 'Urban Infrastructure', 'Environment', 'Healthcare', 'Education'].map((cat) => (
                <span key={cat} className="text-xs px-2.5 py-1 rounded-lg bg-[#FFFDF5] text-[#17332F] border border-[#D8D8C8]">
                  {cat}
                </span>
              ))}
            </div>

            <div className="mt-6">
              <Link to="/citizen/report" className="px-5 py-2.5 rounded-full text-xs font-bold bg-[#034F46] hover:bg-[#0F766E] text-white transition inline-flex items-center gap-2 shadow-xs">
                Report a Problem <ArrowRight className="w-4 h-4" />
              </Link>
            </div>
          </div>

          <div className="glass-card rounded-2xl p-6 border border-[#D8D8C8]">
            <div className="text-xs font-bold text-[#66736F] mb-3">Citizen Status Timeline Example</div>
            <div className="space-y-3 text-xs">
              <div className="flex items-center gap-3 bg-[#F7F5E8] p-3 rounded-xl border border-[#D8D8C8]">
                <CheckCircle2 className="w-4 h-4 text-[#087F6B] shrink-0" />
                <div>
                  <span className="font-semibold text-[#17332F]">Problem Submitted</span>
                  <span className="text-[10px] text-[#66736F] block">CF-2026-001 • Unsafe school toilets</span>
                </div>
              </div>
              <div className="flex items-center gap-3 bg-[#F7F5E8] p-3 rounded-xl border border-[#6A5ACD]/30">
                <Sparkles className="w-4 h-4 text-[#6A5ACD] shrink-0 animate-pulse" />
                <div>
                  <span className="font-semibold text-[#17332F]">AI Classification Complete</span>
                  <span className="text-[10px] text-[#6A5ACD] block">Sanitation • Toilets • Education</span>
                </div>
              </div>
              <div className="flex items-center gap-3 bg-[#F7F5E8] p-3 rounded-xl border border-[#034F46]/20">
                <Award className="w-4 h-4 text-[#034F46] shrink-0" />
                <div>
                  <span className="font-semibold text-[#17332F]">University Match Assigned</span>
                  <span className="text-[10px] text-[#034F46] block">BIT Mesra (Match Score 88.5/100)</span>
                </div>
              </div>
            </div>
          </div>
        </div>

        {/* For Universities & Industry */}
        <div className="grid grid-cols-1 md:grid-cols-2 gap-8">
          <div className="glass-card rounded-2xl p-6 border border-[#6A5ACD]/20">
            <span className="text-xs font-bold text-[#6A5ACD] uppercase tracking-wider">Role 3: Universities</span>
            <h4 className="text-xl font-bold text-[#17332F] mt-2">Turn Research Into Real-World Impact</h4>
            <p className="text-xs text-[#66736F] mt-2 leading-relaxed">
              Discover validated societal problems matching faculty expertise, lab infrastructure, and project capacity. Accept assignment chains and deploy solutions.
            </p>
            <Link to="/login/university" className="mt-4 inline-flex items-center gap-1 text-xs font-bold text-[#6A5ACD] hover:text-[#034F46]">
              Access University Portal <ChevronRight className="w-4 h-4" />
            </Link>
          </div>

          <div className="glass-card rounded-2xl p-6 border border-[#0F766E]/20">
            <span className="text-xs font-bold text-[#0F766E] uppercase tracking-wider">Role 4: Industry & CSR</span>
            <h4 className="text-xl font-bold text-[#17332F] mt-2">Bring Your Resources Where They Matter</h4>
            <p className="text-xs text-[#66736F] mt-2 leading-relaxed">
              Browse published university solutions, contribute technology, testing equipment, mentorship, and CSR funding to accelerate field implementation.
            </p>
            <Link to="/login/industry" className="mt-4 inline-flex items-center gap-1 text-xs font-bold text-[#0F766E] hover:text-[#034F46]">
              Browse Industry Opportunities <ChevronRight className="w-4 h-4" />
            </Link>
          </div>
        </div>
      </section>

      {/* Final CTA */}
      <section className="py-20 max-w-4xl mx-auto px-6 text-center">
        <h2 className="text-3xl font-extrabold text-[#17332F]">Join the CivicFix Ecosystem</h2>
        <p className="mt-3 text-xs sm:text-sm text-[#66736F]">
          Select your portal to start transforming societal problems into verified, measurable solutions.
        </p>

        <div className="mt-8 flex flex-wrap items-center justify-center gap-4">
          <Link to="/citizen/report" className="px-5 py-3 rounded-full text-xs font-bold bg-[#034F46] text-white hover:bg-[#0F766E] transition shadow-xs">
            Report a Problem
          </Link>
          <Link to="/login/government" className="px-5 py-3 rounded-full text-xs font-semibold bg-[#B7791F]/10 text-[#B7791F] border border-[#B7791F]/30 hover:bg-[#B7791F]/20 transition">
            For Government
          </Link>
          <Link to="/login/university" className="px-5 py-3 rounded-full text-xs font-semibold bg-[#E9DFFF] text-[#6A5ACD] border border-[#6A5ACD]/30 hover:bg-[#E9DFFF]/80 transition">
            For Universities
          </Link>
          <Link to="/login/industry" className="px-5 py-3 rounded-full text-xs font-semibold bg-[#0F766E]/10 text-[#0F766E] border border-[#0F766E]/30 hover:bg-[#0F766E]/20 transition">
            For Industry
          </Link>
        </div>
      </section>

      <Footer />
    </div>
  );
};
